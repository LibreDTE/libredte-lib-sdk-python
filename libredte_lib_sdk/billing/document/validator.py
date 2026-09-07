# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.validator`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient


class DocumentValidatorService:
    """
    Valida un documento tributario ya construido (`billing.document`).

    `source` es el XML del documento en base64 (ej. `Document.xml_base64`
    de un documento ya construido) — la API acepta también la bolsa o el
    documento ya cargado, pero el SDK solo necesita pasar el XML.
    """

    _VALIDATE_OPERATION = 'billing.document.validator::validate'
    _VALIDATE_SCHEMA_OPERATION = 'billing.document.validator::validateSchema'
    _VALIDATE_SIGNATURE_OPERATION = (
        'billing.document.validator::validateSignature'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def validate(self, source: str) -> None:
        """
        Valida los datos del documento (`source`, XML en base64).

        No devuelve valor: si el documento no es válido, la API levanta
        `LibreDteApiError` (no hay un resultado "inválido" con detalle).
        """
        self._client.call(self._VALIDATE_OPERATION, source=source)

    def validate_schema(self, source: str) -> dict[str, Any]:
        """
        Valida `source` contra el esquema XSD del documento.

        Devuelve el XML ya validado, como `dict` (la representación
        parseada del XML, ej. `DTE.Documento.Encabezado...`) — el SDK no
        la tipa, ya que su forma depende del tipo de documento.
        """
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SCHEMA_OPERATION,
                source=source,
            ),
        )

    def validate_signature(self, source: str) -> dict[str, Any]:
        """
        Valida la firma electrónica del documento.

        Devuelve un `dict` vacío en caso de éxito. Si la firma no es
        válida, la API levanta `LibreDteApiError`.
        """
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
