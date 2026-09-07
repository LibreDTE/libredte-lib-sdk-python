# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.renderer`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from .models import RenderResult


class DocumentRendererService:
    """
    Renderiza un documento tributario (`billing.document.renderer`).

    Soporta `format='html'` y `format='pdf'`. La API devuelve siempre
    `data.renderings`, una lista de archivos en base64 — ver
    `RenderResult`/`RenderedDocument` en `models.py`.
    """

    _RENDER_OPERATION = 'billing.document.renderer::render'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def render(
        self,
        document_xml_base64: str,
        *,
        format: str = 'pdf',  # noqa: A002
        renderings: dict[str, int] | None = None,
    ) -> RenderResult:
        """
        Genera el PDF (u otro formato soportado por la API) de un documento.

        Sirve tanto para un borrador como para un documento ya timbrado y
        firmado: el resultado depende solo del XML que se le pase (ej.
        `Document.xml_base64`).

        Sin `renderings`, la API genera una única copia `'tributaria'`
        (comportamiento por defecto). `renderings` pide presentaciones y
        cantidad de copias de cada una — ej. `{'tributaria': 1,
        'cedible': 1}` — y la API rechaza (`LibreDteApiError`, 500) una
        presentación que no existe, o si ninguna de las pedidas pudo
        generarse (ej. pedir solo `'cedible'` para un tipo de documento
        sin acuse de recibo). Ver `RenderResult` para cómo se identifica
        cada copia en la respuesta.
        """
        renderer_options: dict[str, Any] = {'format': format}
        if renderings is not None:
            renderer_options['renderings'] = renderings

        data = self._client.call(
            self._RENDER_OPERATION,
            bag={
                'xmlDocument': document_xml_base64,
                'options': {'renderer': renderer_options},
            },
        )
        return RenderResult.from_api(data)
