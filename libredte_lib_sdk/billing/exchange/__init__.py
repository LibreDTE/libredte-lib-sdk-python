# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.exchange`: respuesta al intercambio de DTE."""

from __future__ import annotations

from ...client import ApiClient
from .document_response import DocumentResponseService
from .models import EnvioRecibos, RespuestaEnvio

__all__ = [
    'DocumentResponseService',
    'EnvioRecibos',
    'ExchangeComponent',
    'RespuestaEnvio',
]


class ExchangeComponent:
    """Agrupa los servicios de `billing.exchange`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.document_response = DocumentResponseService(client)
