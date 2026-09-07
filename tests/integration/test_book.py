# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `BookBuilderService`/`BookLoaderService` (`billing.book`).

`loader.load()` normaliza `caratula`/`detalle` — no construye el libro
(eso lo hace `builder.build()`), por lo que `datos` (el libro construido)
siempre viene `None` acá. `auth` solo viene poblado si el emisor incluye
su autorización (`autorizacion_dte`) — ver docstring de `BookBag`.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

_BAG = {
    'tipo': 'libro_ventas',
    'caratula': {
        'RutEmisorLibro': '76192083-9',
        'RutEnvia': '76192083-9',
        'PeriodoTributario': '2024-01',
        'FchResol': '2014-08-22',
        'NroResol': 80,
    },
    'detalle': [
        {
            'TpoDoc': 33,
            'NroDoc': 1,
            'TasaImp': 19,
            'FchDoc': '2024-01-10',
            'RUTDoc': '66666666-6',
            'RznSoc': 'Cliente de Prueba',
            'MntNeto': 100000,
            'MntIVA': 19000,
            'MntTotal': 119000,
        },
    ],
    'emisor': {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
}


def test_builder_build_returns_the_datos_and_the_xml(
    fake_certificate,
    real_sdk,
):
    result = real_sdk.billing.book.builder.build(
        _BAG,
        certificate=fake_certificate,
    )

    caratula = result.datos['LibroCompraVenta']['EnvioLibro']['Caratula']
    assert caratula['RutEmisorLibro'] == '76192083-9'
    assert caratula['TipoOperacion'] == 'VENTA'
    assert '<LibroCompraVenta' in result.xml


def test_builder_build_result_chains_into_validator(
    fake_certificate,
    real_sdk,
):
    built = real_sdk.billing.book.builder.build(
        _BAG,
        certificate=fake_certificate,
    )

    validator = real_sdk.billing.book.validator
    validator.validate_schema(built.xml_base64)
    validator.validate_signature(built.xml_base64)


def test_loader_load_normalizes_caratula_and_detalle(
    fake_certificate,
    real_sdk,
):
    loaded = real_sdk.billing.book.loader.load(
        _BAG, certificate=fake_certificate
    )

    assert loaded.book_type['codigo'] == 'libro_ventas'
    # load() nunca construye el libro, sin importar el input.
    assert loaded.datos is None
    assert loaded.caratula['RutEmisorLibro'] == '76192083-9'
    assert loaded.caratula['TipoOperacion'] == 'VENTA'
    assert loaded.detalle[0]['RUTDoc'] == '66666666-6'


def test_loader_load_resolves_auth_when_emisor_has_autorizacion(
    fake_certificate,
    real_sdk,
):
    bag = {
        **_BAG,
        'emisor': {
            **_BAG['emisor'],
            'autorizacion_dte': {
                'fecha_resolucion': '2014-08-22',
                'numero_resolucion': 80,
            },
        },
    }

    loaded = real_sdk.billing.book.loader.load(
        bag, certificate=fake_certificate
    )

    assert loaded.auth == {'FchResol': '2014-08-22', 'NroResol': 80}
