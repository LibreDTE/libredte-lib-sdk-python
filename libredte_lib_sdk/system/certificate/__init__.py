# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `system.certificate`: certificados digitales reales."""

from __future__ import annotations

from ...client import ApiClient
from .loader import CertificateLoaderService

__all__ = [
    'CertificateComponent',
    'CertificateLoaderService',
]


class CertificateComponent:
    """Agrupa los servicios de `system.certificate`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.loader = CertificateLoaderService(client)
