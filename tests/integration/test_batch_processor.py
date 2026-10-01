# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentBatchProcessorService`
(`billing.document.batch_processor`).

`parse` devuelve un `DocumentBatch` con una `DocumentBag` por documento del
archivo, ya parseada (todavía sin construir).
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk.exceptions import LibreDteApiError

pytestmark = pytest.mark.live

_HEADER = (
    'TipoDTE;Folio;FchEmis;FchVenc;RUTRecep;RznSocRecep;GiroRecep;Telefono;'
    'CorreoRecep;DirRecep;CmnaRecep;VlrCodigo;IndExe;NmbItem;DscItem;QtyItem;'
    'UnmdItem;PrcItem'
)
_EMISOR = {'rut': '76192083-9', 'razon_social': 'SASCO SpA'}


def _csv(*rows: str) -> str:
    return '\n'.join([_HEADER, *rows, ''])


_ROW = (
    '33;{folio};;;60803000-K;{receptor};Gobierno;;;Santiago;Santiago;;;'
    'Producto;;1;;1000'
)


def test_parse_returns_a_bag_per_document(real_sdk):
    csv = _csv(
        _ROW.format(folio=1, receptor='Cliente Uno'),
        _ROW.format(folio=2, receptor='Cliente Dos'),
    )

    batch = real_sdk.billing.document.batch_processor.parse(
        csv.encode(),
        emisor=_EMISOR,
    )

    assert len(batch.document_bags) == 2
    first, second = batch.document_bags
    assert first.document_parsed['Encabezado']['IdDoc']['Folio'] == 1
    assert second.document_parsed['Encabezado']['IdDoc']['Folio'] == 2
    assert first.document_parsed['Encabezado']['Receptor']['RznSocRecep'] == (
        'Cliente Uno'
    )
    assert (
        first.document_parsed['Encabezado']['Emisor']['RznSoc'] == 'SASCO SpA'
    )
    assert first.document is None
    assert first.is_timbrado is False


def test_parse_converts_a_windows_1252_csv_to_utf8(real_sdk):
    csv = _csv(_ROW.format(folio=1, receptor='Peña Ñandú Ltda'))

    batch = real_sdk.billing.document.batch_processor.parse(
        csv.encode('cp1252'),
    )

    receptor = batch.document_bags[0].document_parsed['Encabezado']['Receptor']
    assert receptor['RznSocRecep'] == 'Peña Ñandú Ltda'


def test_parse_without_complete_leaves_the_emisor_data_out(real_sdk):
    csv = _csv(_ROW.format(folio=1, receptor='Cliente'))

    batch = real_sdk.billing.document.batch_processor.parse(
        csv.encode(),
        emisor=_EMISOR,
        complete=False,
    )

    emisor = batch.document_bags[0].document_parsed['Encabezado']['Emisor']
    assert emisor['RznSoc'] is False


def test_parse_reports_the_row_of_the_error(real_sdk):
    csv = _csv(
        _ROW.format(folio=1, receptor='Cliente'),
        _ROW.format(folio=1, receptor='Repetido'),
    )

    with pytest.raises(LibreDteApiError) as error:
        real_sdk.billing.document.batch_processor.parse(csv.encode())

    assert 'Fila 3' in error.value.detail
