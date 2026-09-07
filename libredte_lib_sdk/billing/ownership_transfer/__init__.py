# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.ownership_transfer`: cesión electrónica (factoring)."""

from __future__ import annotations

from ...client import ApiClient
from .aec import AecService
from .models import Aec

__all__ = [
    'Aec',
    'AecService',
    'OwnershipTransferComponent',
]


class OwnershipTransferComponent:
    """Agrupa los servicios de `billing.ownership_transfer`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.aec = AecService(client)
