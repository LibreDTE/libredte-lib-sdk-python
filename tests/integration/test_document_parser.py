# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentParserService` (`billing.document.parser`).

`parse` devuelve la `DocumentBag` con `document_parsed`; nada de lo que
requiere construir el documento (`document`, `document_type`, XML).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

_DTE = {
    'Encabezado': {'IdDoc': {'TipoDTE': 33, 'Folio': 1}},
    'Detalle': [{'NmbItem': 'Servicio', 'QtyItem': 1, 'PrcItem': 10000}],
}


def test_parse_returns_the_parsed_data_of_a_json_document(real_sdk):
    bag = real_sdk.billing.document.parser.parse(_DTE)

    assert bag.document_parsed['Encabezado']['IdDoc']['Folio'] == 1
    assert bag.document_parsed['Detalle'][0]['NmbItem'] == 'Servicio'
    assert bag.document is None
    assert bag.document_type is None
    assert bag.is_timbrado is False


def test_parse_keeps_the_encoding_of_bytes_with_their_declaration(real_sdk):
    xml = (
        '<?xml version="1.0" encoding="ISO-8859-1"?>'
        '<DTE><Documento><Encabezado><Emisor>'
        '<GiroEmis>Tecnología, Informática</GiroEmis>'
        '</Emisor></Encabezado></Documento></DTE>'
    ).encode('iso-8859-1')

    bag = real_sdk.billing.document.parser.parse(xml, strategy='default.xml')

    giro = bag.document_parsed['Encabezado']['Emisor']['GiroEmis']
    assert giro == 'Tecnología, Informática'
