# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.book`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common import XmlPayloadMixin


@dataclass(frozen=True, slots=True)
class Book(XmlPayloadMixin):
    """
    Libro tributario construido (`book.builder::build`).

    Genérico entre los 5 tipos de libro (`tipo` del `bag` de entrada) —
    la clave raíz de `datos` varía según cuál se haya construido (ej.
    `libro_ventas`/`libro_compras` traen `{'LibroCompraVenta': {...}}`),
    por eso no se tipa más allá de `dict`. `xml_base64` es el XML
    completo, listo para encadenar a `BookValidatorService`.
    """

    datos: dict[str, Any]
    xml_base64: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Book:
        """Construye un `Book` desde el `data` que devuelve la API."""
        return cls(
            datos={k: v for k, v in data.items() if k != 'xml'},
            xml_base64=data['xml'],
        )


@dataclass(frozen=True, slots=True)
class BookBag:
    """
    Datos de un libro tributario normalizados por `book.loader::load`.

    Esta operación solo normaliza `caratula`/`detalle` a partir de los
    datos de entrada — no construye el libro ni genera su documento
    firmado (eso lo hace `BookBuilderService.build`), por lo que
    `datos` (el libro ya construido) siempre viene `None` acá, sin
    importar los datos de entrada recibidos. `auth` (la autorización
    del emisor del libro) solo viene poblada si esa autorización se
    incluyó junto con los datos del emisor en la solicitud; si no, viene
    `None`.
    """

    datos: dict[str, Any] | None
    book_type: dict[str, Any]
    auth: dict[str, Any] | None
    caratula: dict[str, Any]
    detalle: list[dict[str, Any]]
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BookBag:
        """Construye un `BookBag` desde el `data` que devuelve la API."""
        return cls(
            datos=data.get('book'),
            book_type=data['book_type'],
            auth=data.get('book_auth'),
            caratula=data.get('caratula') or {},
            detalle=data.get('detalle') or [],
            raw=data,
        )
