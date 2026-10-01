# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.parser`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from ...response_registry import build_response
from ..common import encode_input_data
from .models import DocumentBag


class DocumentParserService:
    """
    Parsea los datos de entrada de un documento (`billing.document.parser`).

    Solo transforma los datos al formato DTE del SII: no normaliza ni
    construye el documento, no necesita CAF ni certificado.
    """

    _PARSE_OPERATION = 'billing.document.parser::parse'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def parse(
        self,
        input_data: str | bytes | dict[str, Any],
        *,
        strategy: str | None = None,
    ) -> DocumentBag:
        """
        Parsea `input_data` y entrega la bolsa con los datos parseados.

        `input_data` es el documento en el formato DTE del SII como `dict`,
        o datos en otro formato (XML, YAML, un formulario, etc.) como `bytes`
        o `str`. El contenido de un archivo se debe pasar como `bytes` (leído
        en modo `rb`): se envía sin alterar su codificación. Un `str` ya es
        texto decodificado y se envía en UTF-8.

        `strategy` es la estrategia de parseo (ej. `'default.xml'`,
        `'form.lite'`); sin ella la API asume `default.json`.

        El resultado es una `DocumentBag` con `document_parsed`; `document`,
        `document_type` y el XML quedan en `None`.
        """
        bag: dict[str, Any] = {'inputData': encode_input_data(input_data)}
        if strategy is not None:
            bag['options'] = {'parser': {'strategy': strategy}}

        return build_response(
            DocumentBag,
            self._client.call_response(self._PARSE_OPERATION, bag=bag),
        )
