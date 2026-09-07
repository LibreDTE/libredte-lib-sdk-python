# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `human_resources.payroll`: cálculo y render de liquidaciones."""

from __future__ import annotations

from ...client import ApiClient
from .calculator import PayrollCalculatorService
from .renderer import PayrollRendererService

__all__ = [
    'PayrollCalculatorService',
    'PayrollComponent',
    'PayrollRendererService',
]


class PayrollComponent:
    """Agrupa los servicios de `human_resources.payroll`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.calculator = PayrollCalculatorService(client)
        self.renderer = PayrollRendererService(client)
