# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentLoaderService` (`billing.document.loader`).

`loadXml` no tenía su shape de respuesta confirmado por ningún fixture
de `libredte-lib-core-dispatcher` (el fixture solo verificaba
`document_type.codigo`). Confirmado en vivo: la respuesta es
genuinamente distinta a `Document` — no trae `xml` ni `id`, solo la
bolsa normalizada (`document`/`document_type`/`document_stamp`/
`document_extra`/`document_auth`), de ahí el DTO propio (`DocumentBag`).
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live


def test_load_xml_normalizes_a_signed_document(signed_document, real_sdk):
    loaded = real_sdk.billing.document.loader.load_xml(
        signed_document.xml_base64,
    )

    assert loaded.datos['Encabezado']['IdDoc']['TipoDTE'] == 33
    assert loaded.document_type['codigo'] == 33
    assert loaded.document_type['es_boleta'] is False
    assert loaded.stamp_xml.startswith('<TED')
