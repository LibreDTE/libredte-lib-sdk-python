# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests en vivo para `AecService` (`billing.ownership_transfer.aec`)."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

_CEDENTE = {
    'RUT': '76192083-9',
    'RazonSocial': 'SASCO SpA',
    'Direccion': 'Santa Cruz, Chile',
    'eMail': 'cedente@example.com',
    'RUTAutorizado': {'RUT': '76192083-9', 'Nombre': 'Administrador'},
}
_CESIONARIO = {
    'RUT': '76354771-K',
    'RazonSocial': 'Factoring S.A.',
    'Direccion': 'Providencia, Santiago',
    'eMail': 'factoring@example.com',
}
_CESION = {'MontoCesion': 119000, 'UltimoVencimiento': '2024-02-14'}


@pytest.fixture
def built_aec(signed_document, fake_certificate, real_sdk):
    return real_sdk.billing.ownership_transfer.aec.build(
        signed_document.xml_base64,
        cedente=_CEDENTE,
        cesionario=_CESIONARIO,
        cesion=_CESION,
        certificate=fake_certificate,
    )


def test_build_returns_the_parsed_data_and_the_xml(built_aec):
    assert (
        built_aec.datos['DocumentoAEC']['Caratula']['RutCedente']
        == '76192083-9'
    )
    assert '<AEC' in built_aec.xml


def test_build_result_chains_into_validate_schema_and_signature(
    built_aec,
    real_sdk,
):
    worker = real_sdk.billing.ownership_transfer.aec

    worker.validate_schema(built_aec.xml_base64)

    results = worker.validate_signature(built_aec.xml_base64)
    assert len(results) >= 1
