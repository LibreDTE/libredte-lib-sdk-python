# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentExamplesService`.

Los ejemplos son los mismos casos de prueba, ya validados, de
`libredte-lib-core` (`tests/fixtures/yaml/documentos_ok/`) — se prueba
que `get()` entrega un `input_data` realmente utilizable por
`DocumentBuilderService`, no solo que la llamada HTTP responde.
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk.billing.trading_parties import Mandatario

pytestmark = pytest.mark.live

_EMISOR = {'rut': '76192083-9', 'razon_social': 'SASCO SpA'}
_MANDATARIO = Mandatario(
    rut='76192083-9',
    nombre='SASCO SpA',
    email='demo@sasco.example',
)


def test_list_returns_many_examples_across_document_types(real_sdk):
    examples = real_sdk.billing.document.examples.list()

    assert len(examples) > 1
    categories = {example.category for example in examples}
    assert len(categories) > 1


def test_get_returns_input_data_and_expected_values(real_sdk):
    first = real_sdk.billing.document.examples.list()[0]

    example = real_sdk.billing.document.examples.get(first.id)

    assert example.id == first.id
    assert 'Encabezado' in example.input_data
    assert 'Detalle' in example.input_data
    assert example.expected


def test_an_example_builds_into_a_real_signed_document(real_sdk):
    """El `input_data` de un ejemplo debe servir tal cual a `build_signed`."""
    b = real_sdk.billing
    example = next(
        e
        for e in b.document.examples.list()
        if e.category == '033_factura_afecta'
    )
    data = b.document.examples.get(example.id)

    caf = b.identifier.caf_faker.create(
        _EMISOR,
        codigo_documento=data.input_data['Encabezado']['IdDoc']['TipoDTE'],
    )
    certificate = b.trading_parties.mandatario_manager.create_fake_certificate(
        _MANDATARIO,
    )

    documento = b.document.builder.build_signed(
        data.input_data,
        caf_xml=caf.xml_base64,
        certificate=certificate,
    )

    assert documento.is_timbrado is True
