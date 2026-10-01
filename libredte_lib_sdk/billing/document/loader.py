# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.loader`."""

from __future__ import annotations

from ...client import ApiClient
from ...response_registry import build_response
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
        """
        Carga y normaliza el documento cuyo XML (base64) es `xml_base64`.

        Devuelve la misma `DocumentBag` que `DocumentBuilderService` —
        `document_id`/`xml_base64` reconstruyen lo que ya se le pasó
        acá, `document`/`document_type`/`document_stamp_base64`/etc.
        son el valor agregado real: los datos ya normalizados.
        """
        response = self._client.call_response(
            self._LOAD_XML_OPERATION, xml=xml_base64
        )
        return build_response(DocumentBag, response)
