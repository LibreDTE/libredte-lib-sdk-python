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
