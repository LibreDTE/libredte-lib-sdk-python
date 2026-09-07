# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.examples`."""

from __future__ import annotations

from ...client import ApiClient
from .models import Example, ExampleSummary


class DocumentExamplesService:
    """
    Ejemplos de documentos reales (`billing.document.examples`).

    Son los mismos casos de prueba, validados, que usa la suite de tests
    de `libredte-lib-core` (`tests/fixtures/yaml/documentos_ok/`) — uno
    por variante de negocio real (descuentos, impuesto adicional, pago a
    crédito, exportación, etc.), no datos inventados por el SDK.
    `Example.input_data` de `get()` se le pasa tal cual a
    `DocumentBuilderService.build_draft()`/`.build_signed()`, típicamente
    reemplazando `Encabezado.IdDoc.Folio` y `Encabezado.Receptor` por los
    propios de quien usa el SDK antes de construir el documento.
    """

    _LIST_OPERATION = 'billing.document.examples::list'
    _GET_OPERATION = 'billing.document.examples::get'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def list(self) -> list[ExampleSummary]:
        """Lista los ejemplos disponibles (`id`, `category`, `case`)."""
        data = self._client.call(self._LIST_OPERATION)
        return [ExampleSummary.from_api(item) for item in data]

    def get(self, example_id: str) -> Example:
        """Entrega los datos completos del ejemplo `example_id`."""
        data = self._client.call(self._GET_OPERATION, id=example_id)
        return Example.from_api(data)
