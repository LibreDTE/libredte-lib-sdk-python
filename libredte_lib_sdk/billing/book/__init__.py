# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.book`: libros tributarios (ventas/compras/RVD/etc.)."""

from __future__ import annotations

from ...client import ApiClient
from .builder import BookBuilderService
from .loader import BookLoaderService
from .models import Book, BookBag
from .validator import BookValidatorService

__all__ = [
    'Book',
    'BookBag',
    'BookBuilderService',
    'BookComponent',
    'BookLoaderService',
    'BookValidatorService',
]


class BookComponent:
    """Agrupa los servicios de `billing.book`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.builder = BookBuilderService(client)
        self.loader = BookLoaderService(client)
        self.validator = BookValidatorService(client)
