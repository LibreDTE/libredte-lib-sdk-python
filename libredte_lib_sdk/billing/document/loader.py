# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.loader`."""

from __future__ import annotations

from ...client import ApiClient
from .models import DocumentBag


class DocumentLoaderService:
    """
    Carga un documento tributario completo desde su XML.

    Solo cubre `loadXml` — pensado para reconstruir los datos
    normalizados de un DTE ya emitido (timbrado y firmado) a partir de
    su XML, ej. un documento recibido de un tercero o recuperado de un
    respaldo.
    """

    _LOAD_XML_OPERATION = 'billing.document.loader::loadXml'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def load_xml(self, xml_base64: str) -> DocumentBag:
        """Carga y normaliza el documento cuyo XML (base64) es `xml_base64`."""
        data = self._client.call(self._LOAD_XML_OPERATION, xml=xml_base64)
        return DocumentBag.from_api(data)
