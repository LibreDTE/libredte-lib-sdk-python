# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.trading_parties`: partes comerciales de un DTE."""

from __future__ import annotations

from ...client import ApiClient
from .mandatario_manager import MandatarioManagerService
from .models import Certificate, Mandatario

__all__ = [
    'Certificate',
    'Mandatario',
    'MandatarioManagerService',
    'TradingPartiesComponent',
]


class TradingPartiesComponent:
    """Agrupa los servicios de `billing.trading_parties`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.mandatario_manager = MandatarioManagerService(client)
