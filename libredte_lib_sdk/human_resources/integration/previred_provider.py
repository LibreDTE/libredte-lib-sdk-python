# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `human_resources.integration.previred_provider`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient


class PreviredProviderService:
    """
    Indicadores previsionales (Previred) para calcular liquidaciones.

    Entrega un `dict` con `periodo`/`periodo_anterior`/
    `periodo_siguiente`/`indicadores` (una entrada por cada tipo de
    indicador: AFC, AFP, salud, etc.), sin tipar como DTO.

    Las tasas son fracciones (0.10 es 10%) y todos los montos están
    siempre en CLP. Cada indicador, excepto `moneda`, trae `vigencia`
    (período YYYYMM desde el que rige el dato) y sus datos agrupados en
    `tasas`, `topes` o `montos`; las dimensiones van anidadas (por
    ejemplo `afc.tasas.plazo_indefinido.empleador`). Las colecciones son
    mapas por código con `codigo` y `glosa` (`afp.instituciones`,
    `asignacion_familiar.tramos`). `moneda` es un mapa por código
    (`CLF`, `UTM`, `UTA`) con `valor`; `CLF` incluye además
    `valor_periodo_anterior`.

    Solo disponible en Lib Pro: contra una instancia de Lib Core esta
    operación no existe — levanta `LibreDteOperationNotFoundError`.
    """

    _GET_INDICADORES_OPERATION = (
        'human_resources.integration.previred_provider::getIndicadores'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def get_indicadores(self, periodo: int) -> dict[str, Any]:
        """Indicadores previsionales vigentes para `periodo` (`YYYYMM`)."""
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._GET_INDICADORES_OPERATION,
                periodo=periodo,
            ),
        )
