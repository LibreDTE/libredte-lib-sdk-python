# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.identifier`: folios de documentos tributarios."""

from __future__ import annotations

from ...client import ApiClient
from .caf_faker import CafFakerService
from .caf_loader import CafLoaderService
from .caf_validator import CafValidatorService
from .models import Caf

__all__ = [
    'Caf',
    'CafFakerService',
    'CafLoaderService',
    'CafValidatorService',
    'IdentifierComponent',
]


class IdentifierComponent:
    """Agrupa los servicios de `billing.identifier`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.caf_faker = CafFakerService(client)
        self.caf_loader = CafLoaderService(client)
        self.caf_validator = CafValidatorService(client)
