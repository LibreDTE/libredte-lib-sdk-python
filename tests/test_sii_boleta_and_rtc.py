# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests (con HTTP mockeado) de `sii_boleta`, de las consultas de `sii_rtc` y
del receptor de la carátula en `dispatcher`.

Las respuestas son las que entregó la API real contra el SII de
certificación.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest
import respx

from libredte_lib_sdk.billing.common import SII_RUT
from libredte_lib_sdk.billing.document.models import DocumentBag
from libredte_lib_sdk.billing.enums import SiiEnvironment
from libredte_lib_sdk.billing.trading_parties import Certificate

from .conftest import TEST_BASE_URL

_CERTIFICATE = Certificate(certificate='cert-pem', private_key='key-pem')
_PRO = (
    'libredte\\lib\\Pro\\Package\\Billing\\Component\\Integration\\'
    'Support\\Response\\SiiBoleta\\'
)
_CORE_RTC = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\'
    'Support\\Response\\SiiRtc\\'
)
_ENVELOPE_CLASS = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Document\\Support\\'
    'DocumentEnvelope'
)
_CHILE = timezone(timedelta(hours=-3))


def _mock(path: str, php_class: str, data: object) -> respx.Route:
    return respx.post(f'{TEST_BASE_URL}/{path}').mock(
        return_value=httpx.Response(
            200,
            json={'meta': {'data_type': php_class}, 'data': data},
        ),
    )


def _sent(route: respx.Route) -> dict:
    return json.loads(route.calls.last.request.content)['parameters']


@respx.mock
def test_boleta_send_returns_the_typed_response(sdk):
    route = _mock(
        'billing/integration/sii_boleta/send_xml_document',
        _PRO + 'SendXmlDocumentResponse',
        {
            'track_id': 33996918,
            'status': 'REC',
            'received_at': '2026-11-13T15:27:57-03:00',
            'rut_sender': '16261063-5',
            'rut_company': '76192083-9',
            'retry_after': 5,
            'location': 'https://apicert.sii.cl/recursos/v1/x',
            'rate_limit': {'limit': 10, 'remaining': 9, 'reset': 1},
            'file': 'libredte_boleta.xml',
        },
    )

    result = sdk.billing.integration.sii_boleta.send(
        'ZW52',
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
        environment=SiiEnvironment.CERTIFICATION,
        retries=2,
    )

    sent = _sent(route)
    assert sent['doc'] == 'ZW52'
    assert sent['company'] == '76192083-9'
    assert sent['retries'] == 2
    assert sent['request']['options']['environment'] == 1
    assert 'compress' not in sent
    assert result.track_id == 33996918
    assert result.status == 'REC'
    assert result.received_at == datetime(
        2026, 11, 13, 15, 27, 57, tzinfo=_CHILE
    )
    assert result.retry_after == 5
    assert result.rate_limit is not None
    assert result.rate_limit.remaining == 9
    assert result.file == 'libredte_boleta.xml'


@respx.mock
def test_boleta_send_defaults_to_production(sdk):
    route = _mock(
        'billing/integration/sii_boleta/send_xml_document',
        _PRO + 'SendXmlDocumentResponse',
        {'track_id': 1, 'status': 'REC'},
    )

    result = sdk.billing.integration.sii_boleta.send(
        'ZW52',
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
    )

    assert _sent(route)['request']['options']['environment'] == 0
    assert result.received_at is None
    assert result.rate_limit is None


@respx.mock
def test_boleta_check_status_of_an_accepted_envelope(sdk):
    route = _mock(
        'billing/integration/sii_boleta/check_xml_document_sent_status',
        _PRO + 'CheckXmlDocumentSentStatusResponse',
        {
            'track_id': 33996918,
            'company': '76192083-9',
            'status': 'EPR',
            'error': False,
            'description': 'Envío procesado',
            'resume': {
                'reported': 1,
                'accepted': 1,
                'rejected': 0,
                'repairs': 0,
            },
            'documents': {
                '39': {
                    'type': 39,
                    'reported': 1,
                    'accepted': 1,
                    'rejected': 0,
                    'repairs': 0,
                },
            },
            'received_at': '2026-11-13T15:27:57-03:00',
            'sender': '16261063-5',
            'retry_after': None,
            'location': None,
            'rate_limit': None,
            'details': [],
        },
    )

    result = sdk.billing.integration.sii_boleta.check_status(
        33996918,
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
        environment=SiiEnvironment.CERTIFICATION,
    )

    sent = _sent(route)
    assert sent['trackId'] == 33996918
    assert sent['company'] == '76192083-9'
    assert sent['request']['options']['environment'] == 1
    assert result.status == 'EPR'
    assert result.error is False
    assert result.resume.accepted == 1
    assert list(result.documents) == [39]
    assert result.documents[39].reported == 1
    assert result.details == []
    assert result.rate_limit is None


@respx.mock
def test_boleta_check_status_without_documents_has_an_empty_mapping(sdk):
    """Sin boletas informadas la API entrega `[]` en vez de un mapa."""
    _mock(
        'billing/integration/sii_boleta/check_xml_document_sent_status',
        _PRO + 'CheckXmlDocumentSentStatusResponse',
        {
            'track_id': 1,
            'company': '76192083-9',
            'status': 'SOK',
            'error': False,
            'description': 'Schema validado',
            'resume': {
                'reported': 0,
                'accepted': 0,
                'rejected': 0,
                'repairs': 0,
            },
            'documents': [],
            'received_at': None,
            'sender': None,
            'retry_after': None,
            'location': None,
            'rate_limit': None,
            'details': [],
        },
    )

    result = sdk.billing.integration.sii_boleta.check_status(
        1,
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
    )

    assert result.documents == {}
    assert result.received_at is None


@respx.mock
def test_boleta_check_status_of_a_rejected_document_has_its_errors(sdk):
    _mock(
        'billing/integration/sii_boleta/check_xml_document_sent_status',
        _PRO + 'CheckXmlDocumentSentStatusResponse',
        {
            'track_id': 33996915,
            'company': '76192083-9',
            'status': 'EPR',
            'error': False,
            'description': 'Envío procesado',
            'resume': {
                'reported': 1,
                'accepted': 0,
                'rejected': 1,
                'repairs': 0,
            },
            'documents': {
                '39': {
                    'type': 39,
                    'reported': 1,
                    'accepted': 0,
                    'rejected': 1,
                    'repairs': 0,
                },
            },
            'received_at': '2026-11-13T15:27:17-03:00',
            'sender': '16261063-5',
            'retry_after': None,
            'location': None,
            'rate_limit': None,
            'details': [
                {
                    'type': 39,
                    'folio': 131269,
                    'status': 'RCH',
                    'description': 'DTE Rechazado',
                    'errors': [
                        {
                            'section': 'DTE',
                            'line': 0,
                            'level': 3,
                            'code': 101,
                            'description': 'Folio ya recibido en el SII',
                            'detail': None,
                        },
                    ],
                },
            ],
        },
    )

    result = sdk.billing.integration.sii_boleta.check_status(
        33996915,
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
    )

    assert result.resume.rejected == 1
    [detail] = result.details
    assert (detail.type, detail.folio, detail.status) == (39, 131269, 'RCH')
    [error] = detail.errors
    assert (error.section, error.level, error.code) == ('DTE', 3, 101)
    assert error.detail is None


@respx.mock
def test_boleta_check_status_of_a_rejected_envelope_has_no_type_nor_folio(
    sdk,
):
    """Un rechazo de carátula no pertenece a ninguna boleta en particular."""
    _mock(
        'billing/integration/sii_boleta/check_xml_document_sent_status',
        _PRO + 'CheckXmlDocumentSentStatusResponse',
        {
            'track_id': 33996902,
            'company': '76192083-9',
            'status': 'RCT',
            'error': True,
            'description': 'Rechazado por error en carátula',
            'resume': {
                'reported': 1,
                'accepted': 0,
                'rejected': 0,
                'repairs': 0,
            },
            'documents': {
                '39': {
                    'type': 39,
                    'reported': 1,
                    'accepted': 0,
                    'rejected': 0,
                    'repairs': 0,
                },
            },
            'received_at': '2026-11-13T15:25:52-03:00',
            'sender': '16261063-5',
            'retry_after': None,
            'location': None,
            'rate_limit': None,
            'details': [
                {
                    'type': None,
                    'folio': None,
                    'status': 'RCH',
                    'description': 'DTE Rechazado',
                    'errors': [
                        {
                            'section': 'CRT',
                            'line': 0,
                            'level': 3,
                            'code': 18,
                            'description': 'RUT Receptor (Caratula) Invalido',
                            'detail': '[66666666-6]',
                        },
                    ],
                },
            ],
        },
    )

    result = sdk.billing.integration.sii_boleta.check_status(
        33996902,
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
    )

    assert result.error is True
    [detail] = result.details
    assert detail.type is None
    assert detail.folio is None
    assert detail.errors[0].detail == '[66666666-6]'


@respx.mock
def test_boleta_validate_document_sends_the_boleta_data(sdk):
    route = _mock(
        'billing/integration/sii_boleta/validate_document',
        _PRO + 'ValidateDocumentResponse',
        {
            'status': 'FAU',
            'description': 'Documento No Recibido por el SII',
            'rate_limit': None,
        },
    )

    result = sdk.billing.integration.sii_boleta.validate_document(
        company_rut='76192083-9',
        document_type=39,
        number=1,
        date='2026-01-02',
        total=1190,
        recipient_rut='66666666-6',
        certificate=_CERTIFICATE,
    )

    sent = _sent(route)
    assert sent['company'] == '76192083-9'
    assert sent['document'] == 39
    assert sent['number'] == 1
    assert sent['date'] == '2026-01-02'
    assert sent['total'] == 1190
    assert sent['recipient'] == '66666666-6'
    assert sent['request']['options']['environment'] == 0
    assert result.status == 'FAU'
    assert result.rate_limit is None


@respx.mock
def test_rtc_check_status_sends_the_track_id(sdk):
    route = _mock(
        'billing/integration/sii_rtc/check_aec_sent_status',
        _CORE_RTC + 'CheckAecSentStatusResponse',
        {
            'track_id': 1234567890,
            'status': '2',
            'description': 'Error: no se encontró información.',
            'error': True,
            'final': False,
        },
    )

    result = sdk.billing.integration.sii_rtc.check_status(
        1234567890,
        certificate=_CERTIFICATE,
        environment=SiiEnvironment.CERTIFICATION,
    )

    sent = _sent(route)
    assert sent['trackId'] == 1234567890
    assert sent['request']['options']['environment'] == 1
    assert (result.status, result.error, result.final) == ('2', True, False)


@respx.mock
def test_rtc_get_assignment_status_with_and_without_the_access_key(sdk):
    route = _mock(
        'billing/integration/sii_rtc/get_assignment_status',
        _CORE_RTC + 'GetAssignmentStatusResponse',
        {
            'assigned': False,
            'status': '2',
            'description': 'Error: no se encontró información.',
            'holder': None,
            'last_annotation': None,
            'collection_rut': None,
            'collection_address': None,
            'sworn_declaration': None,
        },
    )

    result = sdk.billing.integration.sii_rtc.get_assignment_status(
        company_rut='76192083-9',
        document_type=33,
        number=1,
        certificate=_CERTIFICATE,
    )

    sent = _sent(route)
    assert sent['company'] == '76192083-9'
    assert sent['document'] == 33
    assert sent['number'] == 1
    assert sent['assignmentId'] is None
    assert result.assigned is False
    assert result.holder is None

    sdk.billing.integration.sii_rtc.get_assignment_status(
        company_rut='76192083-9',
        document_type=33,
        number=1,
        certificate=_CERTIFICATE,
        assignment_id='clave',
    )
    assert _sent(route)['assignmentId'] == 'clave'


@respx.mock
def test_rtc_get_related_assignment_status_sends_the_related_company(sdk):
    route = _mock(
        'billing/integration/sii_rtc/get_related_assignment_status',
        _CORE_RTC + 'GetAssignmentStatusResponse',
        {
            'assigned': True,
            'status': '0',
            'description': 'Documento cedido',
            'holder': '76192083-9',
            'last_annotation': '2026-11-13',
            'collection_rut': '76192083-9',
            'collection_address': 'Santiago',
            'sworn_declaration': 'Sí',
        },
    )

    result = sdk.billing.integration.sii_rtc.get_related_assignment_status(
        company_rut='76192083-9',
        document_type=34,
        number=5,
        related_company_rut='11222333-9',
        certificate=_CERTIFICATE,
    )

    sent = _sent(route)
    assert sent['relatedCompany'] == '11222333-9'
    assert sent['document'] == 34
    assert result.assigned is True
    assert result.holder == '76192083-9'
    assert result.collection_address == 'Santiago'


def _bag() -> DocumentBag:
    return DocumentBag.from_api(
        {
            'document': {},
            'document_type': {'codigo': 33},
            'document_xml': base64.b64encode(b'<DTE/>').decode(),
            'certificate': {'cert': 'cert-pem', 'pkey': 'key-pem'},
            'emisor': {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
        },
    )


_ENVELOPE_DATA = {'tag': 'EnvioBOLETA', 'xml': 'ZW52', 'documents': []}


@respx.mock
def test_dispatcher_create_without_receptor_rut_sends_no_receptor(sdk):
    route = _mock(
        'billing/document/dispatcher/create',
        _ENVELOPE_CLASS,
        _ENVELOPE_DATA,
    )

    sdk.billing.document.dispatcher.create(_bag())

    assert 'receptor' not in _sent(route)['bag']


@respx.mock
def test_dispatcher_create_sends_the_receptor_of_the_envelope(sdk):
    route = _mock(
        'billing/document/dispatcher/create',
        _ENVELOPE_CLASS,
        _ENVELOPE_DATA,
    )

    sdk.billing.document.dispatcher.create(_bag(), receptor_rut=SII_RUT)

    assert _sent(route)['bag']['receptor'] == {'rut': '60803000-K'}


@respx.mock
def test_dispatcher_create_many_sets_the_receptor_on_the_first_bag_only(sdk):
    route = _mock(
        'billing/document/dispatcher/create_many',
        _ENVELOPE_CLASS,
        _ENVELOPE_DATA,
    )

    sdk.billing.document.dispatcher.create_many(
        [_bag(), _bag()],
        receptor_rut=SII_RUT,
    )

    first, second = _sent(route)['bags']
    assert first['receptor'] == {'rut': '60803000-K'}
    assert 'receptor' not in second


def test_sii_rut_is_the_rut_of_the_sii():
    assert SII_RUT == '60803000-K'


def test_boleta_send_response_requires_the_track_id():
    from libredte_lib_sdk.billing.integration.models import (
        SiiBoletaSendXmlDocumentResponse,
    )

    with pytest.raises(KeyError):
        SiiBoletaSendXmlDocumentResponse.from_api({'status': 'REC'})
