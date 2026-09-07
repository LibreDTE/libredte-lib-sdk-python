# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Paquete `human_resources`: recursos humanos (solo Lib Pro).

Solo existe en LibreDTE Lib Pro: contra una instancia de Lib Core toda
operación de `human_resources.*` levanta `LibreDteOperationNotFoundError`.
Un subpaquete por componente, cada uno con un `*Component` que agrupa
sus servicios por worker.
"""

from __future__ import annotations

from ..client import ApiClient
from .integration import IntegrationComponent
from .payroll import PayrollComponent

__all__ = ['HumanResourcesPackage']


class HumanResourcesPackage:
    """Agrupa los componentes del paquete `human_resources` de la API."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los componentes del paquete sobre el `ApiClient` dado."""
        self.integration = IntegrationComponent(client)
        self.payroll = PayrollComponent(client)
