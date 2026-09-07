# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `human_resources.integration`: indicadores previsionales."""

from __future__ import annotations

from ...client import ApiClient
from .previred_provider import PreviredProviderService

__all__ = [
    'IntegrationComponent',
    'PreviredProviderService',
]


class IntegrationComponent:
    """Agrupa los servicios de `human_resources.integration`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.previred_provider = PreviredProviderService(client)
