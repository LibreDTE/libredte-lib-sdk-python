# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests para `ApiClient`: traduccion de operation_id y manejo de respuesta."""

from __future__ import annotations

import httpx
import pytest
import respx

from libredte_lib_sdk.client import ApiClient
from libredte_lib_sdk.exceptions import (
    LibreDteApiError,
    LibreDteConnectionError,
    LibreDteOperationNotFoundError,
    LibreDteRateLimitError,
)

from .conftest import TEST_BASE_URL


def test_base_url_falls_back_to_the_env_var(monkeypatch):
    monkeypatch.setenv(
        'LIBREDTE_LIB_SDK_BASE_URL',
        'https://pro.libredte.cl/api',
    )

    client = ApiClient()

    assert client._base_url == 'https://pro.libredte.cl/api'


def test_api_token_falls_back_to_the_env_var(monkeypatch):
    monkeypatch.setenv('LIBREDTE_LIB_SDK_TOKEN', 'secret-token')

    client = ApiClient()

    assert client._headers()['Authorization'] == 'Bearer secret-token'


def test_operation_path_translates_dotted_operation_to_a_rest_path():
    path = ApiClient._operation_path('billing.document.builder::build')

    assert path == 'billing/document/builder/build'


@pytest.mark.parametrize(
    'operation_id',
    ['billing.document.builder', 'billing.document::build', 'nope'],
)
def test_operation_path_rejects_a_malformed_operation_id(operation_id):
    with pytest.raises(ValueError, match='operation_id invalido'):
        ApiClient._operation_path(operation_id)


@respx.mock
def test_call_returns_the_data_payload_on_success(api_client):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/builder/build',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {'timestamp': 1.0}, 'data': {'id': 'doc-1'}},
        ),
    )

    result = api_client.call(
        'billing.document.builder::build',
        bag={'parsedData': {}},
    )

    assert result == {'id': 'doc-1'}
    sent_body = route.calls.last.request.content
    assert b'"parameters"' in sent_body
    assert b'"bag"' in sent_body


@respx.mock
def test_call_raises_a_typed_error_for_problem_details(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/builder/build').mock(
        return_value=httpx.Response(
            500,
            json={
                'type': 'about:blank',
                'title': (
                    'libredte\\lib\\Core\\Package\\Billing\\Component'
                    '\\Document\\Exception\\DocumentException'
                ),
                'detail': (
                    'Falta indicar el tipo de documento (TipoDTE) en '
                    'los datos del DTE.'
                ),
                'instance': 'billing.document.builder::build',
                'extensions': {
                    'throwable': {
                        'class': (
                            'libredte\\lib\\Core\\Package\\Billing'
                            '\\Component\\Document\\Exception'
                            '\\DocumentException'
                        ),
                    },
                },
            },
        ),
    )

    with pytest.raises(LibreDteApiError) as exc_info:
        api_client.call('billing.document.builder::build', bag={})

    error = exc_info.value
    assert type(error) is LibreDteApiError
    assert error.status_code == 500
    assert error.operation_id == 'billing.document.builder::build'
    assert 'TipoDTE' in error.detail
    assert error.php_class == (
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Exception\\DocumentException'
    )


@respx.mock
def test_call_raises_operation_not_found_when_the_dispatcher_says_so(
    api_client,
):
    respx.post(
        f'{TEST_BASE_URL}/human_resources/payroll/calculator/calculate',
    ).mock(
        return_value=httpx.Response(
            500,
            json={
                'type': 'about:blank',
                'title': (
                    'Derafu\\BackboneDispatcher\\Exception'
                    '\\OperationNotFoundException'
                ),
                'detail': (
                    'The operation calculate does not exist in '
                    'human_resources.payroll.calculator.'
                ),
                'instance': 'human_resources.payroll.calculator::calculate',
                'extensions': {
                    'throwable': {
                        'class': (
                            'Derafu\\BackboneDispatcher\\Exception'
                            '\\OperationNotFoundException'
                        ),
                    },
                },
            },
        ),
    )

    with pytest.raises(LibreDteOperationNotFoundError) as exc_info:
        api_client.call('human_resources.payroll.calculator::calculate')

    error = exc_info.value
    assert isinstance(error, LibreDteApiError)
    assert error.status_code == 500
    assert error.operation_id == (
        'human_resources.payroll.calculator::calculate'
    )


@respx.mock
def test_call_returns_raw_bytes_for_a_non_json_success_response(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/renderer/render').mock(
        return_value=httpx.Response(
            200,
            content=b'%PDF-1.4 fake pdf bytes',
            headers={'content-type': 'application/pdf'},
        ),
    )

    result = api_client.call(
        'billing.document.renderer::render',
        bag={'xmlDocument': 'ZmFrZQ==', 'options': {}},
    )

    assert result == b'%PDF-1.4 fake pdf bytes'


@respx.mock
def test_call_raises_for_a_non_json_error_response(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/renderer/render').mock(
        return_value=httpx.Response(
            500,
            content=b'Internal Server Error',
            headers={'content-type': 'text/plain'},
        ),
    )

    with pytest.raises(LibreDteApiError) as exc_info:
        api_client.call('billing.document.renderer::render', bag={})

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == 'Internal Server Error'


@respx.mock
def test_call_wraps_a_network_failure(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/builder/build').mock(
        side_effect=httpx.ConnectError('boom'),
    )

    with pytest.raises(LibreDteConnectionError):
        api_client.call('billing.document.builder::build', bag={})


@respx.mock
def test_call_raises_a_rate_limit_error_for_a_429(api_client):
    respx.post(f'{TEST_BASE_URL}/billing/document/builder/build').mock(
        return_value=httpx.Response(
            429,
            json={'detail': 'Too many requests.'},
            headers={
                'Retry-After': '30',
                'X-RateLimit-Limit': '3600',
                'X-RateLimit-Remaining': '0',
            },
        ),
    )

    with pytest.raises(LibreDteRateLimitError) as exc_info:
        api_client.call('billing.document.builder::build', bag={})

    error = exc_info.value
    assert error.status_code == 429
    assert error.detail == 'Too many requests.'
    assert error.retry_after == 30.0
    assert error.limit == 3600
    assert error.remaining == 0
