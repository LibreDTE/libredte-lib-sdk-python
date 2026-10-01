# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests de `response_registry` y de `ApiClient.call_response()`."""

from __future__ import annotations

import httpx
import pytest
import respx

from libredte_lib_sdk import LibreDTE  # noqa: F401  (importa todos los DTO)
from libredte_lib_sdk.billing.document.models import DocumentBag, DocumentBatch
from libredte_lib_sdk.client import ApiResponse
from libredte_lib_sdk.exceptions import LibreDteUnmappedResponseError
from libredte_lib_sdk.response_registry import (
    _REGISTRY,
    api_response,
    build_response,
)

from .conftest import TEST_BASE_URL

_SUPPORT = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Document\\Support'
)


def test_document_bag_and_batch_are_registered_for_their_php_classes():
    bag = build_response(
        DocumentBag,
        ApiResponse(f'{_SUPPORT}\\DocumentBag', {'document_parsed': {}}),
    )
    batch = build_response(
        DocumentBatch,
        ApiResponse(f'{_SUPPORT}\\DocumentBatch', {'document_bags': []}),
    )

    assert isinstance(bag, DocumentBag)
    assert isinstance(batch, DocumentBatch)


def test_build_response_rejects_a_class_without_a_dto():
    response = ApiResponse('Vendor\\Unknown\\Thing', {})

    with pytest.raises(LibreDteUnmappedResponseError, match='Thing'):
        build_response(DocumentBag, response)


def test_build_response_rejects_a_missing_data_type():
    with pytest.raises(LibreDteUnmappedResponseError):
        build_response(DocumentBag, ApiResponse(None, {}))


def test_build_response_rejects_a_dto_other_than_the_expected_one():
    response = ApiResponse(f'{_SUPPORT}\\DocumentBatch', {'document_bags': []})

    with pytest.raises(LibreDteUnmappedResponseError, match='DocumentBag'):
        build_response(DocumentBag, response)


def test_api_response_rejects_registering_a_class_twice():
    with pytest.raises(ValueError, match='ya está registrada'):

        @api_response(f'{_SUPPORT}\\DocumentBag')
        class _Other:
            @classmethod
            def from_api(cls, _data):
                return cls()


@respx.mock
def test_call_response_returns_the_php_class_and_the_data(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/parser/parse').mock(
        return_value=httpx.Response(
            200,
            json={'meta': {'data_type': 'array'}, 'data': [1, 2]},
        ),
    )

    response = api_client.call_response(
        'billing.document.parser::parse',
        bag={},
    )

    assert response == ApiResponse('array', [1, 2])


@respx.mock
def test_call_response_has_no_data_type_for_a_non_json_response(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/renderer/render').mock(
        return_value=httpx.Response(
            200,
            content=b'%PDF',
            headers={'content-type': 'application/pdf'},
        ),
    )

    response = api_client.call_response(
        'billing.document.renderer::render',
        bag={},
    )

    assert response == ApiResponse(None, b'%PDF')


_B = 'libredte\\lib\\Core\\Package\\Billing\\Component\\'
_SII = _B + 'Integration\\Support\\Response\\'


@pytest.mark.parametrize(
    ('php_class', 'dto'),
    [
        (_B + 'Document\\Support\\DocumentBag', 'DocumentBag'),
        (_B + 'Document\\Support\\DocumentBatch', 'DocumentBatch'),
        (_B + 'Document\\Support\\DocumentEnvelope', 'DocumentEnvelope'),
        (
            'libredte\\lib\\Core\\Package\\System\\Component\\Rendering'
            '\\Support\\RenderResult',
            'RenderResult',
        ),
        (_B + 'Identifier\\Entity\\Caf', 'Caf'),
        ('Derafu\\Certificate\\Certificate', 'Certificate'),
        (_B + 'TradingParties\\Entity\\Mandatario', 'Mandatario'),
        (_B + 'Book\\Support\\BookBag', 'BookBag'),
        (_B + 'OwnershipTransfer\\Entity\\Aec', 'Aec'),
        (_B + 'Exchange\\Entity\\EnvioRecibos', 'EnvioRecibos'),
        (_B + 'Exchange\\Entity\\RespuestaEnvio', 'RespuestaEnvio'),
        (_SII + 'SiiDte\\SendXmlDocumentResponse', 'SendXmlDocumentResponse'),
        (
            _SII + 'SiiDte\\CheckXmlDocumentSentStatusResponse',
            'CheckXmlDocumentSentStatusResponse',
        ),
        (
            _SII + 'SiiDte\\RequestXmlDocumentSentStatusByEmailResponse',
            'RequestXmlDocumentSentStatusByEmailResponse',
        ),
        (
            _SII + 'SiiDte\\ValidateDocumentResponse',
            'ValidateDocumentResponse',
        ),
        (
            _SII + 'SiiDte\\ValidateDocumentSignatureResponse',
            'ValidateDocumentSignatureResponse',
        ),
        (_SII + 'SiiRtc\\SendAecResponse', 'SendAecResponse'),
        (
            _SII + 'SiiRcv\\CheckDocumentAssignabilityResponse',
            'CheckDocumentAssignabilityResponse',
        ),
        (
            _SII + 'SiiRcv\\SubmitDocumentAcceptanceResponse',
            'SubmitDocumentAcceptanceResponse',
        ),
        (
            _SII + 'SiiRcv\\GetDocumentSiiReceptionDateResponse',
            'GetDocumentSiiReceptionDateResponse',
        ),
        (
            _SII + 'SiiRcv\\ListDocumentEventsResponse',
            'ListDocumentEventsResponse',
        ),
    ],
)
def test_every_response_class_has_its_dto(php_class, dto):
    assert _REGISTRY[php_class].__name__ == dto


def test_no_unexpected_response_class_is_registered():
    assert len(_REGISTRY) == 21
