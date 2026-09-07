# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `CafLoaderService`/`CafValidatorService`.

`caf_loader::load` y `caf_validator::validate` esperan el mismo dato: el
XML del CAF en base64 (`caf_faker::create` y `caf_loader::load` devuelven
ese mismo formato en `.xml`). `caf_validator::validate` **no** acepta la
entidad `Caf` completa como `dict` (da 422, "requires string data"),
solo el string base64, aunque el parámetro de la operación se llame
`caf` y no `xml`.
"""

from __future__ import annotations

import base64

import pytest

from libredte_lib_sdk.exceptions import LibreDteApiError

pytestmark = pytest.mark.live

_EMISOR = {'rut': '76192083-9', 'razon_social': 'SASCO SpA'}


@pytest.fixture
def fake_caf(real_sdk):
    return real_sdk.billing.identifier.caf_faker.create(
        _EMISOR,
        codigo_documento=33,
        folio_desde=1,
        folio_hasta=100,
    )


def test_caf_loader_round_trips_a_real_caf_xml(fake_caf, real_sdk):
    """Cargar el XML de un CAF ya generado debe devolver los mismos datos."""
    loaded = real_sdk.billing.identifier.caf_loader.load(fake_caf.xml_base64)

    assert loaded.tipo_documento == fake_caf.tipo_documento
    assert loaded.folio_desde == fake_caf.folio_desde
    assert loaded.folio_hasta == fake_caf.folio_hasta
    assert loaded.raw['emisor']['rut'] == '76192083-9'


def test_caf_validator_accepts_a_valid_caf(fake_caf, real_sdk):
    validated = real_sdk.billing.identifier.caf_validator.validate(
        fake_caf.xml_base64,
    )

    assert validated.raw['vigente'] is True


def test_caf_loader_rejects_malformed_xml(real_sdk):
    garbage = base64.b64encode(b'esto no es un CAF').decode()

    with pytest.raises(LibreDteApiError) as exc_info:
        real_sdk.billing.identifier.caf_loader.load(garbage)

    assert exc_info.value.status_code == 500


def test_caf_validator_rejects_malformed_xml(real_sdk):
    garbage = base64.b64encode(b'esto no es un CAF').decode()

    with pytest.raises(LibreDteApiError) as exc_info:
        real_sdk.billing.identifier.caf_validator.validate(garbage)

    assert exc_info.value.status_code == 500
