# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.identifier.caf_faker`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from .models import Caf


class CafFakerService:
    """
    Genera CAF ficticios (`billing.identifier.caf_faker::create`).

    Solo para pruebas/desarrollo: el CAF resultante no está autorizado
    de verdad por el SII, pero permite ejercitar el timbrado/firma de un
    documento sin depender de un folio real.
    """

    _CREATE_OPERATION = 'billing.identifier.caf_faker::create'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def create(
        self,
        emisor: dict[str, Any],
        *,
        codigo_documento: int,
        folio_desde: int = 1,
        folio_hasta: int | None = None,
    ) -> Caf:
        """
        Genera un CAF ficticio para `emisor` y `codigo_documento`.

        `emisor` es un `dict` con `rut`/`razon_social`, tal como lo
        espera la API. `folio_hasta` por defecto cubre solo
        `folio_desde` (un único folio), igual que hace la API.
        """
        data = self._client.call(
            self._CREATE_OPERATION,
            emisor=emisor,
            codigoDocumento=codigo_documento,
            folioDesde=folio_desde,
            folioHasta=folio_hasta,
        )
        return Caf.from_api(data)
