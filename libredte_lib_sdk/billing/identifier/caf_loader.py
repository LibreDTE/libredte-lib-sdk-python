# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.identifier.caf_loader`."""

from __future__ import annotations

from ...client import ApiClient
from .models import Caf


class CafLoaderService:
    """
    Carga un CAF real (`billing.identifier.caf_loader::load`).

    Carga el XML de un CAF real (el que el SII le entrega al emisor) y
    lo entrega como `Caf`, con su folio/vigencia ya resueltos.
    """

    _LOAD_OPERATION = 'billing.identifier.caf_loader::load'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def load(self, xml_base64: str) -> Caf:
        """Carga el CAF cuyo XML (en base64) es `xml_base64`."""
        data = self._client.call(self._LOAD_OPERATION, xml=xml_base64)
        return Caf.from_api(data)
