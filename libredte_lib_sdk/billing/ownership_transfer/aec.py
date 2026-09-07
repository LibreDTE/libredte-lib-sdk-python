# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.ownership_transfer.aec`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient
from ..trading_parties.models import Certificate
from .models import Aec


class AecService:
    """
    Construye y valida un AEC (`billing.ownership_transfer.aec`).

    AEC = Archivo Electrónico de Cesión: cede un DTE (factoring) o
    re-cede un AEC ya construido — `source` en `build()` acepta ambos
    (el XML de un DTE, o el de un AEC ya construido, en base64; la API
    distingue cuál es por la etiqueta raíz del XML).
    """

    _BUILD_OPERATION = 'billing.ownership_transfer.aec::build'
    _VALIDATE_SCHEMA_OPERATION = (
        'billing.ownership_transfer.aec::validateSchema'
    )
    _VALIDATE_SIGNATURE_OPERATION = (
        'billing.ownership_transfer.aec::validateSignature'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def build(
        self,
        source: str,
        *,
        cedente: dict[str, Any],
        cesionario: dict[str, Any],
        cesion: dict[str, Any],
        certificate: Certificate,
    ) -> Aec:
        """
        Construye el AEC completo (`DTECedido`, `Cesion` y `AEC` raíz).

        `source` es el XML en base64 del DTE a ceder (primera cesión) o
        de un AEC ya construido (re-cesión). `cedente` trae `RUT`/
        `RazonSocial`/`Direccion`/`eMail`/`RUTAutorizado` (esta última
        con `RUT`/`Nombre`); `cesionario` trae `RUT`/`RazonSocial`/
        `Direccion`/`eMail`; `cesion` trae `MontoCesion`/
        `UltimoVencimiento` — todos tal como los espera la API.
        """
        data = self._client.call(
            self._BUILD_OPERATION,
            bag={
                'source': source,
                'cedente': cedente,
                'cesionario': cesionario,
                'cesion': cesion,
                'certificate': certificate.to_payload(),
            },
        )
        return Aec.from_api(data)

    def validate_schema(self, source: str) -> dict[str, Any]:
        """Valida `source` (XML del AEC, en base64) contra su esquema XSD."""
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SCHEMA_OPERATION,
                source=source,
            ),
        )

    def validate_signature(self, source: str) -> list[dict[str, Any]]:
        """
        Valida cada firma electrónica del AEC.

        El AEC trae múltiples firmas (`DTECedido`, `Cesion`, `AEC`) —
        devuelve una lista, un ítem por firma.
        """
        return cast(
            'list[dict[str, Any]]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
