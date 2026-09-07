# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.book.builder`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from ..trading_parties.models import Certificate
from .models import Book


class BookBuilderService:
    """Construye un libro tributario (`billing.book.builder`)."""

    _BUILD_OPERATION = 'billing.book.builder::build'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def build(
        self,
        bag: dict[str, Any],
        *,
        certificate: Certificate,
    ) -> Book:
        """
        Construye el libro descrito por `bag`.

        `bag` trae `tipo` (`'libro_ventas'`, `'libro_compras'`,
        `'libro_boletas'`, `'libro_guias'`, `'resumen_ventas_diarias'`,
        sin tipar como enum cerrado), `caratula`, `detalle` y `emisor`,
        tal cual el formato SII.
        """
        data = self._client.call(
            self._BUILD_OPERATION,
            bag={**bag, 'certificate': certificate.to_payload()},
        )
        return Book.from_api(data)
