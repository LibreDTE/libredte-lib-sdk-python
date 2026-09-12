# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `CertificateLoaderService` (`system.certificate.loader`).

Arma un PKCS12 en memoria (mismo enfoque que `tests/test_utils.py`, sin
depender de un archivo `.p12` real) a partir de un certificado ficticio
ya generado por `create_fake_certificate` — así el certificado sí trae
RUT/nombre/correo real (el fake de `create_fake_certificate` los
codifica), que es lo que `system.certificate.loader::load` debe poder
extraer.
"""

from __future__ import annotations

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12

from libredte_lib_sdk.billing.trading_parties import Mandatario

pytestmark = pytest.mark.live

_MANDATARIO = Mandatario(
    run='76192083-9',
    nombre='SASCO SpA',
    email='demo@sasco.example',
)
_PASSWORD = 'clave1234'


@pytest.fixture
def fake_pkcs12(real_sdk):
    """Un `.p12` en memoria, con RUT/nombre/correo reales embebidos."""
    mandatario_manager = real_sdk.billing.trading_parties.mandatario_manager
    certificate = mandatario_manager.create_fake_certificate(_MANDATARIO)
    key = serialization.load_pem_private_key(
        certificate.private_key.encode(),
        password=None,
    )
    cert = x509.load_pem_x509_certificate(certificate.certificate.encode())
    return pkcs12.serialize_key_and_certificates(
        b'demo',
        key,
        cert,
        None,
        serialization.BestAvailableEncryption(_PASSWORD.encode()),
    )


def test_load_extracts_the_mandatario_and_a_usable_certificate(
    fake_pkcs12,
    real_sdk,
):
    loaded = real_sdk.system.certificate.loader.load(fake_pkcs12, _PASSWORD)

    assert loaded.id == '76192083-9'
    assert loaded.name == 'SASCO SpA'
    assert loaded.email == 'demo@sasco.example'
    assert loaded.is_active is True
    assert loaded.certificate.startswith('-----BEGIN CERTIFICATE-----')


def test_create_from_certificate_matches_load(fake_pkcs12, real_sdk):
    loaded = real_sdk.system.certificate.loader.load(fake_pkcs12, _PASSWORD)

    mandatario_manager = real_sdk.billing.trading_parties.mandatario_manager
    mandatario = mandatario_manager.create_from_certificate(loaded)

    assert mandatario.run == loaded.id
    assert mandatario.nombre == loaded.name
    assert mandatario.email == loaded.email
