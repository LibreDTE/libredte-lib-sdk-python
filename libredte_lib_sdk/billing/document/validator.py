# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.validator`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient


class DocumentValidatorService:
    """
    Valida un documento tributario ya construido (`billing.document`).

    `source` es el XML del documento en base64 (ej. `DocumentBag.xml_base64`
    de un documento ya construido) — la API acepta también la bolsa o el
    documento ya cargado, pero el SDK solo necesita pasar el XML.
    """

    _VALIDATE_OPERATION = 'billing.document.validator::validate'
    _VALIDATE_SCHEMA_OPERATION = 'billing.document.validator::validate_schema'
    _VALIDATE_SIGNATURE_OPERATION = (
        'billing.document.validator::validate_signature'
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

        Devuelve `{'valid': bool, 'error': str | None, 'signature': {...}}`.
        La API responde con éxito tanto si la firma es válida como si no
        lo es: el resultado está en `valid`, y `error` explica el motivo
        cuando es `False` (por ejemplo, que el contenido se modificó
        después de firmarlo). `signature` trae los datos de la firma
        (`reference`, `signature_method`, `digest_method`, el certificado
        y `signer`, con los datos del certificado del firmante).
        """
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
