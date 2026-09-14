# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.book`."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, cast


@dataclass(frozen=True, slots=True)
class BookBag:
    """
    Bolsa de un libro tributario (`book.builder::build`/`book.loader::load`).

    Ambas operaciones devuelven esta misma forma — la diferencia es qué
    tan lejos llegó el procesamiento: `loader.load()` solo normaliza
    `caratula`/`detalle` a partir de los datos de entrada (`book`
    siempre viene `None`, sin importar el input); `builder.build()` sí
    construye y firma el libro, por lo que `book` viene poblado (el
    libro completo — genérico entre los 5 tipos, ej.
    `libro_ventas`/`libro_compras` traen `{'LibroCompraVenta': {...}}`
    junto a su `xml` en base64 — no se tipa más allá de `dict` porque
    la clave raíz varía según el tipo). `book_auth` (la autorización
    del emisor) solo viene poblada si esa autorización se incluyó junto
    con los datos del emisor en la solicitud; si no, viene `None`.

    `xml_base64`/`xml`/`xml_bytes` dan acceso directo al XML del libro
    construido — solo válidos cuando `book` no es `None` (ver
    `is_construido`); listos para encadenar a `BookValidatorService`.
    No usa `XmlPayloadMixin`: acá `xml_base64` es una `@property` (el
    libro puede no estar construido), no un campo simple.
    """

    book: dict[str, Any] | None
    book_type: dict[str, Any]
    book_auth: dict[str, Any] | None
    caratula: dict[str, Any]
    detalle: list[dict[str, Any]]
    raw: dict[str, Any]

    @property
    def is_construido(self) -> bool:
        """Si `book` viene poblado (`builder.build()`, no `loader.load()`)."""
        return self.book is not None

    @property
    def xml_base64(self) -> str:
        """XML del libro construido, en base64 — ver `BookValidatorService`."""
        if self.book is None:
            raise ValueError(
                'Este BookBag no tiene un libro construido — viene de '
                '`loader.load()`, no de `builder.build()`.',
            )
        return cast('str', self.book['xml'])

    @property
    def xml_bytes(self) -> bytes:
        """XML del libro construido, decodificado desde base64."""
        return base64.b64decode(self.xml_base64)

    @property
    def xml(self) -> str:
        """XML del libro construido, como texto (ISO-8859-1)."""
        return self.xml_bytes.decode('iso-8859-1')

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> BookBag:
        """Construye un `BookBag` desde el `data` que devuelve la API."""
        return cls(
            book=data.get('book'),
            book_type=data['book_type'],
            book_auth=data.get('book_auth'),
            caratula=data.get('caratula') or {},
            detalle=data.get('detalle') or [],
            raw=data,
        )
