# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests en vivo para `DocumentResponseService` (`billing.exchange`)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

_CARATULA_ENVIO_RECIBOS = {
    'RutResponde': '76192083-9',
    'RutRecibe': '88888888-8',
}

_RECIBOS = [
    {
        'TipoDoc': 33,
        'Folio': 1,
        'FchEmis': '2024-01-15',
        'RUTEmisor': '88888888-8',
        'RUTRecep': '76192083-9',
        'MntTotal': 100000,
        'Recinto': 'Oficina central',
        'RutFirma': '76192083-9',
    },
]

_CARATULA_RESPUESTA_ENVIO = {
    'RutResponde': '76192083-9',
    'RutRecibe': '88888888-8',
    'IdRespuesta': 1,
}

_RESULTADO_DTE = {
    'resultado_dte': [
        {
            'TipoDTE': 33,
            'Folio': 1,
            'FchEmis': '2024-01-15',
            'RUTEmisor': '88888888-8',
            'RUTRecep': '76192083-9',
            'MntTotal': 100000,
            'CodEnvio': 1,
            'EstadoDTE': 0,
            'EstadoDTEGlosa': 'ACEPTADO OK',
        },
    ],
}


def test_build_envio_recibos_returns_the_parsed_data_and_the_xml(
    fake_certificate,
    real_sdk,
):
    result = real_sdk.billing.exchange.document_response.build_envio_recibos(
        _RECIBOS,
        caratula=_CARATULA_ENVIO_RECIBOS,
        certificate=fake_certificate,
    )

    caratula = result.datos['EnvioRecibos']['SetRecibos']['Caratula']
    assert caratula['RutRecibe'] == '88888888-8'
    assert '<EnvioRecibos' in result.xml


def test_build_envio_recibos_result_chains_into_validator(
    fake_certificate,
    real_sdk,
):
    service = real_sdk.billing.exchange.document_response
    built = service.build_envio_recibos(
        _RECIBOS,
        caratula=_CARATULA_ENVIO_RECIBOS,
        certificate=fake_certificate,
    )

    service.validate_schema(built.xml_base64)

    results = service.validate_signature(built.xml_base64)
    assert len(results) >= 1


def test_build_respuesta_envio_returns_the_parsed_data_and_the_xml(
    fake_certificate,
    real_sdk,
):
    result = real_sdk.billing.exchange.document_response.build_respuesta_envio(
        _RESULTADO_DTE,
        caratula=_CARATULA_RESPUESTA_ENVIO,
        certificate=fake_certificate,
    )

    assert '<RespuestaDTE' in result.xml


def test_build_respuesta_envio_result_chains_into_validator(
    fake_certificate,
    real_sdk,
):
    service = real_sdk.billing.exchange.document_response
    built = service.build_respuesta_envio(
        _RESULTADO_DTE,
        caratula=_CARATULA_RESPUESTA_ENVIO,
        certificate=fake_certificate,
    )

    service.validate_schema(built.xml_base64)

    results = service.validate_signature(built.xml_base64)
    assert len(results) >= 1
