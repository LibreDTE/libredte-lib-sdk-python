# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `human_resources.*` — requieren Lib Pro.

A diferencia del resto de la suite `live` (que corre contra el
`core.libredte.cl` por defecto), estos tests necesitan apuntar a una
instancia de Lib Pro: `human_resources.*` no existe en Lib Core (ver
`test_operation_not_found.py`). Correrlos con
`LIBREDTE_LIB_SDK_BASE_URL` apuntando a esa instancia, ej.:

.. code-block:: bash

    LIBREDTE_LIB_SDK_BASE_URL=http://localhost:9000/api \
        .venv/bin/pytest -m live -v tests/integration/test_human_resources.py
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.live

_EMPLEADO = {
    'run': 12345678,
    'dv': '5',
    'nombre': 'Juan',
    'apellidoPaterno': 'Perez',
    'fechaNacimiento': '1990-01-01',
    'contactoPersonal': {
        'correo': 'juan.perez@example.com',
        'telefono': '+56 9 12345678',
        'direccion': 'Calle 123',
        'comuna': 13101,
    },
    'contactoEmpresa': {
        'correo': 'juan.perez@example.com',
        'direccion': 'Calle 123',
        'comuna': 13101,
    },
    'previsionInstitucion': '03',
    'saludInstitucion': '04',
    'saludMonto': 1.62,
    'saludMoneda': 2,
}
_CONTRATO = {
    'tipo': 'I',
    'fechaInicio': '2016-08-01',
    'sueldoBase': 1350000,
    'rol': 'Desarrollador',
}


def test_previred_provider_get_indicadores_returns_real_indicadores(real_sdk):
    indicadores = (
        real_sdk.human_resources.integration.previred_provider.get_indicadores(
            202412
        )
    )

    assert indicadores['periodo'] == 202412
    assert indicadores['periodo_anterior'] == 202411
    assert indicadores['periodo_siguiente'] == 202501
    assert 'moneda' in indicadores['indicadores']
    assert indicadores['indicadores']['moneda']['CLF'] > 0


def test_payroll_calculator_calculate_computes_a_real_liquidacion(real_sdk):
    liquidacion = real_sdk.human_resources.payroll.calculator.calculate(
        _EMPLEADO,
        _CONTRATO,
        202412,
        contexto={'tasaSeguroAccidente': 0.0095},
    )

    assert (
        liquidacion['identificacion_empleado']['datos_personales']['run']
        == '12345678-5'
    )
    assert liquidacion['totales']


def test_payroll_renderer_render_renders_a_real_liquidacion(real_sdk):
    """
    `render()` recibe tal cual el `dict` que devuelve `calculate()` —
    mismo flujo real que encadena `libredte-lib-pro`. Devuelve un
    `RenderResult` (mismo DTO que `document.renderer::render()`, sin
    `label`: la liquidación de sueldo no modela presentaciones múltiples.
    """
    liquidacion = real_sdk.human_resources.payroll.calculator.calculate(
        _EMPLEADO,
        _CONTRATO,
        202412,
        contexto={'tasaSeguroAccidente': 0.0095},
    )

    html = real_sdk.human_resources.payroll.renderer.render(liquidacion)
    assert html.first.mime_type == 'text/html'
    assert html.first.label is None
    assert b'<html' in html.first.content_bytes

    pdf = real_sdk.human_resources.payroll.renderer.render(
        liquidacion, options={'format': 'pdf'}
    )
    assert pdf.first.mime_type == 'application/pdf'
    assert pdf.first.content_bytes.startswith(b'%PDF')
