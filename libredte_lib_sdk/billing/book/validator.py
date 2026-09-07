# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.book.validator`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient


class BookValidatorService:
    """
    Valida un libro tributario ya construido (`billing.book.validator`).

    `source` es el XML del libro en base64. Devuelve un `dict`/`list`
    vacío en caso de éxito.
    """

    _VALIDATE_SCHEMA_OPERATION = 'billing.book.validator::validateSchema'
    _VALIDATE_SIGNATURE_OPERATION = 'billing.book.validator::validateSignature'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def validate_schema(self, source: str) -> dict[str, Any]:
        """Valida `source` contra el esquema XSD del libro."""
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SCHEMA_OPERATION,
                source=source,
            ),
        )

    def validate_signature(self, source: str) -> dict[str, Any]:
        """
        Valida la firma electrónica del libro.

        El libro tiene una sola firma — devuelve un único `dict`, no
        una lista.
        """
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
