# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Paquete `billing`: facturación electrónica de Chile.

Organizado igual que la propia API (`paquete.componente.worker::operacion`):
un subpaquete por componente (`document`, `identifier`, `trading_parties`,
`integration`), cada uno con un `*Component` que agrupa sus servicios por
worker. Agregar un worker nuevo (de un componente ya soportado, u otro
componente/paquete de la API) es agregar un archivo y registrarlo en el
`__init__.py` de su componente — no toca nada de lo demás.
"""

from __future__ import annotations

from ..client import ApiClient
from .book import BookComponent
from .document import DocumentComponent
from .exchange import ExchangeComponent
from .identifier import IdentifierComponent
from .integration import IntegrationComponent
from .ownership_transfer import OwnershipTransferComponent
from .trading_parties import TradingPartiesComponent

__all__ = ['BillingPackage']


class BillingPackage:
    """Agrupa los componentes del paquete `billing` de la API."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los componentes del paquete sobre el `ApiClient` dado."""
        self.document = DocumentComponent(client)
        self.identifier = IdentifierComponent(client)
        self.trading_parties = TradingPartiesComponent(client)
        self.integration = IntegrationComponent(client)
        self.ownership_transfer = OwnershipTransferComponent(client)
        self.book = BookComponent(client)
        self.exchange = ExchangeComponent(client)
