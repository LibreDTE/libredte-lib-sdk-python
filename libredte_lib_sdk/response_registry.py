# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Registro de las clases de respuesta de la API y el DTO que las representa.

La API informa en `meta.data_type` la clase PHP de cada resultado. Cada DTO
declara la suya con `@api_response(...)`, junto a su `from_api()`: así la
clase PHP queda a la vista donde se define el DTO, y el servicio no decide
qué DTO usar, lo decide la respuesta.

Este módulo no importa ningún DTO (se registran ellos aquí), para no crear
ciclos de importación.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar, cast

from .client import ApiResponse
from .exceptions import LibreDteUnmappedResponseError


class _ResponseDto(Protocol):
    """Un DTO que se construye a partir del `data` de la API."""

    @classmethod
    def from_api(cls, data: Any) -> Any:
        """Construye el DTO desde el `data` que devuelve la API."""


_Dto = TypeVar('_Dto', bound=_ResponseDto)

_REGISTRY: dict[str, type[_ResponseDto]] = {}


def api_response(php_class: str) -> Callable[[type[_Dto]], type[_Dto]]:
    """
    Registra el DTO decorado como representante de una clase PHP de la API.

    `php_class` es el nombre completo de la clase, tal como llega en
    `meta.data_type`.
    """

    def register(dto: type[_Dto]) -> type[_Dto]:
        if php_class in _REGISTRY:
            raise ValueError(
                f'La clase de la API {php_class} ya está registrada para '
                f'{_REGISTRY[php_class].__name__}.',
            )
        _REGISTRY[php_class] = dto
        return dto

    return register


def build_response(expected: type[_Dto], response: ApiResponse) -> _Dto:
    """
    Construye el DTO de una respuesta, según la clase que informó la API.

    `expected` es el DTO que el servicio espera devolver: no elige el DTO (lo
    elige `response.data_type`), solo verifica que coincida y tipa el
    resultado.

    :raises LibreDteUnmappedResponseError: Si la clase de la respuesta no
        tiene DTO registrado o es distinta de la esperada.
    """
    dto = _REGISTRY.get(response.data_type or '')
    if dto is None:
        raise LibreDteUnmappedResponseError(
            f'La API devolvió la clase {response.data_type!r}, que no tiene '
            f'un DTO registrado en el SDK.',
        )
    if dto is not expected:
        raise LibreDteUnmappedResponseError(
            f'La API devolvió la clase {response.data_type!r} '
            f'({dto.__name__}), pero se esperaba {expected.__name__}.',
        )

    return cast(_Dto, expected.from_api(response.data))
