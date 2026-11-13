# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentValidatorService`/`DocumentDispatcherService`.

Ninguna de estas operaciones toca el SII real (son validación estructural
y de firma dentro de `libredte-lib-core`) — por eso alcanza con un
certificado ficticio (`fake_certificate`) para tener una firma real que
validar, sin necesitar credenciales de un RUT real.

`document.validator::validate_signature`/`document.dispatcher
::validate_signature` no tenían el shape de su respuesta confirmado por
ningún fixture de `libredte-lib-core-dispatcher` (solo se verificaba
éxito, no contenido) — se confirmó acá, en vivo: ambas devuelven vacío
en caso de éxito (un `dict` para el documento, una lista de `dict` para
el sobre, uno por firma).
"""

from __future__ import annotations

import base64

import pytest

from libredte_lib_sdk.exceptions import LibreDteApiError

pytestmark = pytest.mark.live


def test_validator_validate_accepts_a_signed_document(
    signed_document,
    real_sdk,
):
    result = real_sdk.billing.document.validator.validate(
        signed_document.xml_base64,
    )

    assert result is None


def test_validator_validate_schema_returns_the_parsed_dte(
    signed_document,
    real_sdk,
):
    result = real_sdk.billing.document.validator.validate_schema(
        signed_document.xml_base64,
    )

    assert result['DTE']['Documento']['Encabezado']['IdDoc']['TipoDTE'] == '33'


def test_validator_validate_signature_succeeds_on_a_signed_document(
    signed_document,
    real_sdk,
):
    result = real_sdk.billing.document.validator.validate_signature(
        signed_document.xml_base64,
    )

    assert result['valid'] is True
    assert result['error'] is None
    assert 'signer' in result['signature']


def test_validator_validate_signature_reports_a_document_changed_after_signing(
    signed_document,
    real_sdk,
):
    xml = base64.b64decode(signed_document.xml_base64).decode('latin-1')
    assert 'Producto A' in xml
    changed = base64.b64encode(
        xml.replace('Producto A', 'Producto B').encode('latin-1'),
    ).decode()

    result = real_sdk.billing.document.validator.validate_signature(changed)

    assert result['valid'] is False
    assert result['error']


def test_dispatcher_load_xml_rebuilds_the_envelope(signed_envelope, real_sdk):
    envelope = real_sdk.billing.document.dispatcher.load_xml(
        signed_envelope.xml_base64,
    )

    assert envelope.tag == 'EnvioDTE'


def test_dispatcher_validate_returns_the_parsed_envelope(
    signed_envelope,
    real_sdk,
):
    result = real_sdk.billing.document.dispatcher.validate(
        signed_envelope.xml_base64,
    )

    assert (
        result['EnvioDTE']['SetDTE']['Caratula']['RutEmisor'] == '76192083-9'
    )


def test_dispatcher_validate_schema_returns_the_parsed_envelope(
    signed_envelope,
    real_sdk,
):
    result = real_sdk.billing.document.dispatcher.validate_schema(
        signed_envelope.xml_base64,
    )

    assert (
        result['EnvioDTE']['SetDTE']['Caratula']['RutEmisor'] == '76192083-9'
    )


def test_dispatcher_validate_signature_succeeds_on_a_signed_envelope(
    signed_envelope,
    real_sdk,
):
    result = real_sdk.billing.document.dispatcher.validate_signature(
        signed_envelope.xml_base64,
    )

    assert isinstance(result, list)
    assert len(result) >= 1
    assert all(item['valid'] is True for item in result)


def test_validator_validate_rejects_malformed_xml(real_sdk):
    with pytest.raises(LibreDteApiError):
        real_sdk.billing.document.validator.validate(
            'bm8gZXMgdW4gZG9jdW1lbnRv'
        )
