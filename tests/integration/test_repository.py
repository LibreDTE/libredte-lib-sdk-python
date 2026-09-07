# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `CatalogService` (`system.repository.catalog`).

`Comuna` y `TipoDocumentoInterface` (a través de su FQCN) son los
repositorios que consume `seed_demo` de `libredte-slim` — se prueba con
esos dos, no con los 17 disponibles.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

_COMUNA_REPOSITORY = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
    '\\Entity\\Comuna'
)
_TIPO_DOCUMENTO_REPOSITORY = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
    '\\Contract\\TipoDocumentoInterface'
)


def test_list_includes_the_repositories_seed_demo_needs(real_sdk):
    repositories = real_sdk.system.repository.catalog.list()

    assert _COMUNA_REPOSITORY in repositories
    assert _TIPO_DOCUMENTO_REPOSITORY in repositories


def test_comuna_codigo_is_the_comuna_name_not_a_numeric_sii_code(real_sdk):
    comunas = real_sdk.system.repository.catalog.find_all(_COMUNA_REPOSITORY)

    assert len(comunas) > 300
    santiago = next(c for c in comunas if c['codigo'] == 'SANTIAGO')
    assert santiago['nombre'] == 'SANTIAGO'


def test_find_returns_the_element_matching_the_id(real_sdk):
    comuna = real_sdk.system.repository.catalog.find(
        _COMUNA_REPOSITORY, 'SANTIAGO'
    )

    assert comuna['codigo'] == 'SANTIAGO'
    assert comuna['nombre'] == 'SANTIAGO'


def test_find_one_by_returns_the_first_match_or_none(real_sdk):
    tipos = real_sdk.system.repository.catalog.find_one_by(
        _TIPO_DOCUMENTO_REPOSITORY,
        criteria={'codigo': 33},
    )
    assert tipos['nombre_corto'] == 'Factura'

    sin_match = real_sdk.system.repository.catalog.find_one_by(
        _TIPO_DOCUMENTO_REPOSITORY,
        criteria={'codigo': -1},
    )
    assert sin_match is None


def test_find_by_filters_tipo_documento_to_the_electronic_codes(real_sdk):
    codigos_electronicos = [33, 34, 39, 41, 46, 52, 56, 61, 110, 111, 112]

    tipos = real_sdk.system.repository.catalog.find_by(
        _TIPO_DOCUMENTO_REPOSITORY,
        criteria={'codigo': codigos_electronicos},
    )

    assert {t['codigo'] for t in tipos} == set(codigos_electronicos)
    factura = next(t for t in tipos if t['codigo'] == 33)
    assert factura['nombre_corto'] == 'Factura'


def test_count_matches_find_all_length(real_sdk):
    count = real_sdk.system.repository.catalog.count(_COMUNA_REPOSITORY)
    comunas = real_sdk.system.repository.catalog.find_all(_COMUNA_REPOSITORY)

    assert count == len(comunas)
