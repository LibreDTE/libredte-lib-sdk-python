# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `system.repository.catalog`."""

from __future__ import annotations

import builtins
from typing import Any, cast

from ...client import ApiClient


class CatalogService:
    """
    Acceso genérico a los repositorios/catálogos de `libredte-lib-core`.

    El esquema de un elemento depende de qué `repository` se pida (una
    `Comuna` no tiene los mismos campos que un `TipoDocumentoInterface`
    o una `AduanaPais`), así que ningún repositorio se tipa como DTO
    propio: cada método devuelve el `dict`/`list[dict]` tal cual la
    API, listo para poblar tablas propias de quien use el SDK. `list()`
    (sin argumentos) entrega los identificadores de repositorio
    disponibles para usar en `repository`.
    """

    _LIST_OPERATION = 'system.repository.catalog::list'
    _FIND_OPERATION = 'system.repository.catalog::find'
    _FIND_ALL_OPERATION = 'system.repository.catalog::findAll'
    _FIND_BY_OPERATION = 'system.repository.catalog::findBy'
    _FIND_ONE_BY_OPERATION = 'system.repository.catalog::findOneBy'
    _COUNT_OPERATION = 'system.repository.catalog::count'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def list(self) -> builtins.list[str]:
        """Identificadores de los repositorios disponibles."""
        return cast(
            'builtins.list[str]',
            self._client.call(self._LIST_OPERATION),
        )

    def find(
        self,
        repository: str,
        element_id: str | int,
    ) -> dict[str, Any] | None:
        """El elemento de `repository` cuyo identificador es `element_id`."""
        return cast(
            'dict[str, Any] | None',
            self._client.call(
                self._FIND_OPERATION,
                repository=repository,
                id=element_id,
            ),
        )

    def find_all(self, repository: str) -> builtins.list[dict[str, Any]]:
        """Todos los elementos de `repository`."""
        return cast(
            'builtins.list[dict[str, Any]]',
            self._client.call(
                self._FIND_ALL_OPERATION,
                repository=repository,
            ),
        )

    def find_by(
        self,
        repository: str,
        criteria: dict[str, Any] | None = None,
        *,
        order_by: dict[str, str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> builtins.list[dict[str, Any]]:
        """
        Elementos de `repository` que cumplen `criteria`.

        `criteria` es `{'campo': valor}` (o `{'campo': [valor1, valor2]}`
        para coincidencia con cualquiera de varios valores, ej. filtrar
        `TipoDocumentoInterface` por una lista de códigos). `order_by` es
        `{'campo': 'ASC'|'DESC'}`.
        """
        return cast(
            'builtins.list[dict[str, Any]]',
            self._client.call(
                self._FIND_BY_OPERATION,
                repository=repository,
                criteria=criteria or {},
                orderBy=order_by,
                limit=limit,
                offset=offset,
            ),
        )

    def find_one_by(
        self,
        repository: str,
        criteria: dict[str, Any] | None = None,
        *,
        order_by: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        """El primer elemento de `repository` que cumple `criteria`."""
        return cast(
            'dict[str, Any] | None',
            self._client.call(
                self._FIND_ONE_BY_OPERATION,
                repository=repository,
                criteria=criteria or {},
                orderBy=order_by,
            ),
        )

    def count(
        self,
        repository: str,
        criteria: dict[str, Any] | None = None,
    ) -> int:
        """Cuenta los elementos de `repository` que cumplen `criteria`."""
        return cast(
            'int',
            self._client.call(
                self._COUNT_OPERATION,
                repository=repository,
                criteria=criteria or {},
            ),
        )
