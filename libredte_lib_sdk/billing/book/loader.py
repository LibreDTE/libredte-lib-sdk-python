# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.book.loader`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from ..trading_parties.models import Certificate
from .models import BookBag


class BookLoaderService:
    """Carga y normaliza los datos de un libro (`billing.book.loader`)."""

    _LOAD_OPERATION = 'billing.book.loader::load'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def load(
        self,
        bag: dict[str, Any],
        *,
        certificate: Certificate,
    ) -> BookBag:
        """
        Normaliza `caratula`/`detalle` de `bag` en un `BookBag`.

        `bag` trae `tipo`/`caratula`/`detalle`/`emisor`, tal cual el
        formato SII. `BookBag.datos` siempre viene `None` (no construye
        el libro); `BookBag.auth` viene poblado solo si
        `bag['emisor']` incluye `autorizacion_dte`.
        """
        data = self._client.call(
            self._LOAD_OPERATION,
            bag={**bag, 'certificate': certificate.to_payload()},
        )
        return BookBag.from_api(data)
