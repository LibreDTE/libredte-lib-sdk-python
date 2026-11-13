# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests (con HTTP mockeado) de las opciones de reintentos y tiempos."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from libredte_lib_sdk.billing.integration import SiiRequestOptions
from libredte_lib_sdk.billing.trading_parties import Certificate

from .conftest import TEST_BASE_URL

_CERTIFICATE = Certificate(certificate='cert-pem', private_key='key-pem')
_CORE = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\'
    'Support\\Response\\'
)
_PRO = (
    'libredte\\lib\\Pro\\Package\\Billing\\Component\\Integration\\'
    'Support\\Response\\SiiBoleta\\'
)
_COMPANY = '76192083-9'

# Un método de cada servicio `sii_*`: operación, clase de la respuesta, el
# `data` mínimo que la construye y cómo se llama.
_CASES = {
    'sii_dte': (
        'billing/integration/sii_dte/check_xml_document_sent_status',
        _CORE + 'SiiDte\\CheckXmlDocumentSentStatusResponse',
        {'status': 'EPR'},
        lambda sdk, options: sdk.billing.integration.sii_dte.check_status(
            1,
            certificate=_CERTIFICATE,
            company_rut=_COMPANY,
            options=options,
        ),
    ),
    'sii_rcv': (
        'billing/integration/sii_rcv/list_document_events',
        _CORE + 'SiiRcv\\ListDocumentEventsResponse',
        [],
        lambda sdk, options: (
            sdk.billing.integration.sii_rcv.list_document_events(
                company_rut=_COMPANY,
                document_type=33,
                number=1,
                certificate=_CERTIFICATE,
                options=options,
            )
        ),
    ),
    'sii_rtc': (
        'billing/integration/sii_rtc/get_related_assignment_status',
        _CORE + 'SiiRtc\\GetAssignmentStatusResponse',
        {},
        lambda sdk, options: (
            sdk.billing.integration.sii_rtc.get_related_assignment_status(
                company_rut=_COMPANY,
                document_type=34,
                number=1,
                related_company_rut=_COMPANY,
                certificate=_CERTIFICATE,
                options=options,
            )
        ),
    ),
    'sii_boleta': (
        'billing/integration/sii_boleta/validate_document',
        _PRO + 'ValidateDocumentResponse',
        {'status': 'DOK'},
        lambda sdk, options: (
            sdk.billing.integration.sii_boleta.validate_document(
                company_rut=_COMPANY,
                document_type=39,
                number=1,
                date='2026-01-02',
                total=1000,
                recipient_rut='66666666-6',
                certificate=_CERTIFICATE,
                options=options,
            )
        ),
    ),
}


def _sent_options(sdk, service: str, options) -> dict:
    path, php_class, data, call = _CASES[service]
    route = respx.post(f'{TEST_BASE_URL}/{path}').mock(
        return_value=httpx.Response(
            200,
            json={'meta': {'data_type': php_class}, 'data': data},
        ),
    )

    call(sdk, options)

    sent = json.loads(route.calls.last.request.content)['parameters']
    return sent['request']['options']


@pytest.mark.parametrize('service', list(_CASES))
@respx.mock
def test_the_options_of_a_call_reach_the_api(sdk, service):
    options = SiiRequestOptions(retries=2, timeout=15, max_duration=90)

    assert _sent_options(sdk, service, options) == {
        'environment': 0,
        'retries': 2,
        'timeout': 15,
        'max_duration': 90,
    }


@pytest.mark.parametrize('service', list(_CASES))
@respx.mock
def test_a_call_without_options_sends_only_the_environment(sdk, service):
    assert _sent_options(sdk, service, None) == {'environment': 0}


@pytest.mark.parametrize('service', list(_CASES))
@respx.mock
def test_only_the_options_given_are_sent(sdk, service):
    options = SiiRequestOptions(timeout=30)

    assert _sent_options(sdk, service, options) == {
        'environment': 0,
        'timeout': 30,
    }
