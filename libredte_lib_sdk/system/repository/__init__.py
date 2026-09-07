# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `system.repository`: catálogos/repositorios de la biblioteca."""

from __future__ import annotations

from ...client import ApiClient
from .catalog import CatalogService

__all__ = [
    'CatalogService',
    'RepositoryComponent',
]


class RepositoryComponent:
    """Agrupa los servicios de `system.repository`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.catalog = CatalogService(client)
