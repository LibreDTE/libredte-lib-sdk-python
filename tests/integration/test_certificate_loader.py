# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `CertificateLoaderService` (`system.certificate.loader`).

Usa un `.p12` fijo (`tests/fixtures/certificate_112223339.p12`,
contraseña `i_love_libredte`) en vez de generar uno en cada corrida —
así el test no necesita ninguna librería de certificados: solo lee los
bytes del archivo y se los pasa tal cual a la API, igual que subiría el
archivo una persona real.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.live

_FIXTURE_PATH = (
    Path(__file__).parent.parent / 'fixtures' / 'certificate_112223339.p12'
)
_PASSWORD = 'i_love_libredte'


@pytest.fixture
def fake_pkcs12() -> bytes:
    """Bytes crudos del `.p12` de prueba."""
    return _FIXTURE_PATH.read_bytes()


def test_load_extracts_the_holder_and_a_usable_certificate(
    fake_pkcs12: bytes,
    real_sdk,
):
    loaded = real_sdk.system.certificate.loader.load(fake_pkcs12, _PASSWORD)

    assert loaded.id == '11222333-9'
    assert loaded.name == 'Usuario de LibreDTE'
    assert loaded.email == 'correo@example.com'
    assert loaded.is_active is True
    assert loaded.certificate.startswith('-----BEGIN CERTIFICATE-----')


def test_create_from_certificate_matches_load(fake_pkcs12: bytes, real_sdk):
    loaded = real_sdk.system.certificate.loader.load(fake_pkcs12, _PASSWORD)

    mandatario_manager = real_sdk.billing.trading_parties.mandatario_manager
    mandatario = mandatario_manager.create_from_certificate(loaded)

    assert mandatario.run == loaded.id
    assert mandatario.nombre == loaded.name
    assert mandatario.email == loaded.email
