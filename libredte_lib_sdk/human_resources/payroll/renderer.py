# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `human_resources.payroll.renderer`."""

from __future__ import annotations

from typing import Any

from ...billing.document.models import RenderResult
from ...client import ApiClient
from ...response_registry import build_response


class PayrollRendererService:
    """
    Render de una liquidación de sueldo, en HTML o PDF.

    Devuelve un único archivo renderizado (no soporta copias múltiples
    ni presentaciones alternativas) — mismo `RenderResult`/
    `RenderedDocument` que usa `DocumentRendererService.render()`, ya
    que la API entrega el mismo shape de respuesta para ambos.

    Solo disponible en Lib Pro.
    """

    _RENDER_OPERATION = 'human_resources.payroll.renderer::render'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def render(
        self,
        liquidacion: dict[str, Any] | list[Any],
        *,
        options: dict[str, Any] | None = None,
    ) -> RenderResult:
        """
        Renderiza `liquidacion`.

        `options={'format': 'pdf'}` para PDF; por defecto genera HTML.
        `liquidacion` es el mismo `dict` que devuelve
        `PayrollCalculatorService.calculate()`.
        """
        response = self._client.call_response(
            self._RENDER_OPERATION,
            liquidacion=liquidacion,
            options=options or {},
        )
        return build_response(RenderResult, response)
