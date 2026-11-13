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

import base64
import dataclasses
import os
import re
from pathlib import Path

import pytest

from libredte_lib_sdk import LibreDTE
from libredte_lib_sdk.billing.trading_parties import Certificate, Mandatario

_INPUT_DATA = {
    'Encabezado': {
        'IdDoc': {'TipoDTE': 33, 'Folio': 1},
        'Emisor': {
            'RUTEmisor': '76192083-9',
            'RznSoc': 'SASCO SpA',
            'GiroEmis': 'Servicios',
            'Acteco': 620200,
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
        run='76192083-9',
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
def signed_envelope(real_sdk, signed_document):
    """
    Un sobre `EnvioDTE` real, armado a partir de `signed_document`.

    La carátula del sobre necesita `autorizacion_dte` (`FchResol`/
    `NroResol`) — un dato de la relación SII-emisor, no del DTE en sí,
    así que nunca viene poblado en `signed_document.emisor` (`build_
    signed()` no lo pide). Se agrega acá, sobre una copia de la bolsa,
    justo antes de despachar — sin tocar el XML ya firmado del DTE.
    """
    bag = dataclasses.replace(
        signed_document,
        emisor={
            **signed_document.emisor,
            'autorizacion_dte': {
                'fecha_resolucion': '2014-08-22',
                'numero_resolucion': 80,
            },
        },
    )
    return real_sdk.billing.document.dispatcher.create(bag)


@pytest.fixture
def sii_certificate():
    """
    Certificado digital real, para operar contra el SII de certificación.

    Se lee de `LIBREDTE_CERTIFICATE_CERT` y `LIBREDTE_CERTIFICATE_PKEY`
    (PEM; un `\\n` literal vale como salto de línea). Sin ellas el test
    se omite: ninguna otra fixture necesita un certificado real.
    """
    cert = os.environ.get('LIBREDTE_CERTIFICATE_CERT')
    pkey = os.environ.get('LIBREDTE_CERTIFICATE_PKEY')
    if not cert or not pkey:
        pytest.skip(
            'Falta LIBREDTE_CERTIFICATE_CERT / LIBREDTE_CERTIFICATE_PKEY.',
        )

    return Certificate(
        certificate=cert.replace('\\n', '\n'),
        private_key=pkey.replace('\\n', '\n'),
    )


@pytest.fixture
def sii_caf():
    """
    Entrega `(caf_xml_base64, folio_desde, folio_hasta)` de un CAF real.

    Los CAF de certificación están en el directorio `LIBREDTE_CAF_DIR`,
    uno por tipo de documento (`033.xml`, `034.xml`, `039.xml`...). Sin él
    el test se omite.
    """
    directory = os.environ.get('LIBREDTE_CAF_DIR')
    if not directory:
        pytest.skip('Falta LIBREDTE_CAF_DIR.')

    def load(document_type: int) -> tuple[str, int, int]:
        path = Path(directory) / f'{document_type:03d}.xml'
        if not path.is_file():
            pytest.skip(f'No existe el CAF {path}.')
        xml = path.read_bytes()
        folio_desde = int(re.search(rb'<D>(\d+)</D>', xml)[1])
        folio_hasta = int(re.search(rb'<H>(\d+)</H>', xml)[1])

        return base64.b64encode(xml).decode(), folio_desde, folio_hasta

    return load
