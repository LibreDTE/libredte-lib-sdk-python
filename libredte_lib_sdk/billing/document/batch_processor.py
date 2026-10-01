# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.batch_processor`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from ...response_registry import build_response
from ..common import encode_content
from .models import DocumentBatch


class DocumentBatchProcessorService:
    """
    Parsea un lote de documentos de una emisión masiva.

    Solo cubre `parse`: entrega los documentos parseados, sin construirlos
    (sin folios, CAF ni certificado).
    """

    _PARSE_OPERATION = 'billing.document.batch_processor::parse'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def parse(
        self,
        input_data: str | bytes,
        *,
        emisor: dict[str, Any] | None = None,
        strategy: str | None = None,
        complete: bool | None = None,
    ) -> DocumentBatch:
        """
        Parsea el archivo de un lote y entrega las bolsas de sus documentos.

        `input_data` es el contenido del archivo (CSV, XLSX, etc.). Se debe
        pasar como `bytes` (leído en modo `rb`): se envía sin alterar. Un
        `str` ya es texto decodificado y se envía en UTF-8.

        `emisor` es un `dict` con `rut`/`razon_social` (y demás datos del
        emisor): con `complete` activo (por defecto) se usan para completar
        los datos del emisor de cada documento.

        `strategy` es la estrategia del archivo (`'spreadsheet.csv'` por
        defecto; `'spreadsheet.xlsx'` solo existe en Lib Pro). `complete`
        indica si se completan los datos del documento con los del emisor
        (por defecto la API lo hace).

        Un error en el archivo lanza `LibreDteApiError` indicando la fila
        (ej. ``Fila 3: ...``).
        """
        batch: dict[str, Any] = {'inputData': encode_content(input_data)}
        if emisor is not None:
            batch['emisor'] = emisor

        options: dict[str, Any] = {}
        if strategy is not None:
            options['strategy'] = strategy
        if complete is not None:
            options['complete'] = complete
        if options:
            batch['options'] = {'batch_processor': options}

        return build_response(
            DocumentBatch,
            self._client.call_response(self._PARSE_OPERATION, batch=batch),
        )
