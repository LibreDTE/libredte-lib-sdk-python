# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Paquete `system`: infraestructura de `libredte-lib-core`, no de negocio.

Expone utilidades genéricas de la librería que la app consumidora
necesita para poblar sus propios datos: los catálogos/repositorios
reales (`repository.catalog`, ej. comunas, tipos de documento) y la
carga de certificados digitales reales (`certificate.loader`). Un
subpaquete por componente, cada uno con un `*Component` que agrupa sus
servicios por worker.
"""

from __future__ import annotations

from ..client import ApiClient
from .certificate import CertificateComponent
from .repository import RepositoryComponent

__all__ = ['SystemPackage']


class SystemPackage:
    """Agrupa los componentes del paquete `system` de la API."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los componentes del paquete sobre el `ApiClient` dado."""
        self.repository = RepositoryComponent(client)
        self.certificate = CertificateComponent(client)
