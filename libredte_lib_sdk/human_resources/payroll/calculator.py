# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `human_resources.payroll.calculator`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient


class PayrollCalculatorService:
    """
    Cálculo de liquidaciones de sueldo.

    `empleado`/`contrato`/`contexto` son `dict` con el formato que
    espera la API (`Empleado`/`Contrato`/`LiquidacionContexto` de Lib
    Pro). Devuelve la liquidación calculada (haberes, descuentos,
    aportes del empleador y totales) como `dict`, sin tipar.

    Solo disponible en Lib Pro.
    """

    _CALCULATE_OPERATION = 'human_resources.payroll.calculator::calculate'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def calculate(
        self,
        empleado: dict[str, Any],
        contrato: dict[str, Any],
        periodo: int,
        *,
        detalles: list[dict[str, Any]] | None = None,
        contexto: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Liquidación de sueldo de `empleado` para `periodo` (`YYYYMM`)."""
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._CALCULATE_OPERATION,
                empleado=empleado,
                contrato=contrato,
                periodo=periodo,
                detalles=detalles or [],
                contexto=contexto,
            ),
        )
