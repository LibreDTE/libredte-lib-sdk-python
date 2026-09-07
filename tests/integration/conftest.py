# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Fixtures para los tests `live` (golpean la API real de LibreDTE Lib).

Separados de `tests/conftest.py` a propósito: los tests del resto del
paquete son unitarios (mockean HTTP con `respx`, corren offline); estos
son de integración real, sin mocks, y están excluidos por defecto (ver
`pyproject.toml`, marker `live`).
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk import LibreDTE
from libredte_lib_sdk.billing.trading_parties import Mandatario

_INPUT_DATA = {
    'Encabezado': {
        'IdDoc': {'TipoDTE': 33, 'Folio': 1},
        'Emisor': {
            'RUTEmisor': '76192083-9',
            'RznSoc': 'SASCO SpA',
            'GiroEmis': 'Servicios',
            'DirOrigen': 'Santiago',
            'CmnaOrigen': 'Santiago',
        },
        'Receptor': {
            'RUTRecep': '12345678-5',
            'RznSocRecep': 'Cliente de prueba',
            'GiroRecep': 'Giro',
            'DirRecep': 'Santiago',
            'CmnaRecep': 'Santiago',
        },
    },
    'Detalle': [{'NmbItem': 'Producto A', 'QtyItem': 1, 'PrcItem': 1000}],
}

_INPUT_DATA_BOLETA = {
    'Encabezado': {
        'IdDoc': {'TipoDTE': 39, 'Folio': 1},
        'Emisor': {
            'RUTEmisor': '76192083-9',
            'RznSoc': 'SASCO SpA',
            'GiroEmis': 'Servicios',
            'DirOrigen': 'Santiago',
            'CmnaOrigen': 'Santiago',
        },
        'Receptor': {
            'RUTRecep': '12345678-5',
            'RznSocRecep': 'Cliente de prueba',
        },
    },
    'Detalle': [{'NmbItem': 'Producto A', 'QtyItem': 1, 'PrcItem': 1000}],
}


@pytest.fixture
def real_sdk():
    """`LibreDTE` real, sin mocks (URL configurable, ver `README.rst`)."""
    instance = LibreDTE()
    yield instance
    instance.close()


@pytest.fixture
def draft_document(real_sdk):
    """Un borrador real (factura afecta, tipo 33), construido en vivo."""
    return real_sdk.billing.document.builder.build_draft(_INPUT_DATA)


@pytest.fixture
def draft_boleta(real_sdk):
    """
    Un borrador real de boleta (tipo 39), construido en vivo.

    Las boletas no admiten acuse de recibo — sirve para probar que la
    API omite en silencio una presentación `'cedible'` pedida sobre un
    tipo de documento que no la soporta (ver `RenderResult`).
    """
    return real_sdk.billing.document.builder.build_draft(_INPUT_DATA_BOLETA)


@pytest.fixture
def fake_certificate(real_sdk):
    """Certificado ficticio real (autofirmado), generado en vivo."""
    mandatario = Mandatario(
        rut='76192083-9',
        nombre='SASCO SpA',
        email='sasco@example.com',
    )
    service = real_sdk.billing.trading_parties.mandatario_manager
    return service.create_fake_certificate(mandatario)


@pytest.fixture
def signed_document(real_sdk, fake_certificate):
    """
    Un documento real, timbrado y firmado con CAF y certificado ficticios.

    A diferencia de `draft_document` (sin CAF ni certificado), este sí
    tiene una firma electrónica real que validar — lo usan los tests de
    `DocumentValidatorService`/`DocumentDispatcherService`.
    """
    caf = real_sdk.billing.identifier.caf_faker.create(
        {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
        codigo_documento=33,
        folio_desde=1,
        folio_hasta=100,
    )
    return real_sdk.billing.document.builder.build_signed(
        _INPUT_DATA,
        caf_xml=caf.xml_base64,
        certificate=fake_certificate,
    )


@pytest.fixture
def signed_envelope(real_sdk, signed_document, fake_certificate):
    """Un sobre `EnvioDTE` real, armado a partir de `signed_document`."""
    emisor = {
        'rut': '76192083-9',
        'razon_social': 'SASCO SpA',
        'autorizacion_dte': {
            'fecha_resolucion': '2014-08-22',
            'numero_resolucion': 80,
        },
    }
    return real_sdk.billing.document.dispatcher.create(
        signed_document.xml_base64,
        certificate=fake_certificate,
        emisor=emisor,
    )
