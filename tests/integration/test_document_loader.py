# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentLoaderService` (`billing.document.loader`).

`loadXml` devuelve la misma `DocumentBag` que `DocumentBuilderService`
(`document`/`document_type`/`document_stamp_base64`/`document_extra`/
`document_auth`/`document_id`/`xml_base64`) — acá se reconstruye a
partir de un documento ya timbrado y firmado, así que además viene con
`is_timbrado` en `True`.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live


def test_load_xml_normalizes_a_signed_document(signed_document, real_sdk):
    loaded = real_sdk.billing.document.loader.load_xml(
        signed_document.xml_base64,
    )

    assert loaded.document['Encabezado']['IdDoc']['TipoDTE'] == 33
    assert loaded.document_type['codigo'] == 33
    assert loaded.document_type['es_boleta'] is False
    assert loaded.document_stamp_base64 is not None
    assert '<DTE' in loaded.xml
    assert loaded.is_timbrado is True
