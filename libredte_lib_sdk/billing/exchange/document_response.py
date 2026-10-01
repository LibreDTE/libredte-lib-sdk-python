# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.exchange.document_response`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient
from ...response_registry import build_response
from ..trading_parties.models import Certificate
from .models import EnvioRecibos, RespuestaEnvio


class DocumentResponseService:
    """
    Genera los XML de respuesta al intercambio de DTE.

    Cubre `EnvioRecibos` (recibo de mercaderías o servicios) y
    `RespuestaDTE` (acuse de recibo del envío o resultado de
    validación).
    """

    _BUILD_ENVIO_RECIBOS_OPERATION = (
        'billing.exchange.document_response::buildEnvioRecibos'
    )
    _BUILD_RESPUESTA_ENVIO_OPERATION = (
        'billing.exchange.document_response::buildRespuestaEnvio'
    )
    _VALIDATE_SCHEMA_OPERATION = (
        'billing.exchange.document_response::validateSchema'
    )
    _VALIDATE_SIGNATURE_OPERATION = (
        'billing.exchange.document_response::validateSignature'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def build_envio_recibos(
        self,
        recibos: list[dict[str, Any]],
        *,
        caratula: dict[str, Any],
        certificate: Certificate,
    ) -> EnvioRecibos:
        """
        Construye el XML `EnvioRecibos` firmado.

        `recibos` es la lista de recibos tal cual el formato SII (cada
        uno con `TipoDoc`/`Folio`/`FchEmis`/`RUTEmisor`/`RUTRecep`/
        `MntTotal`/`Recinto`, y opcionalmente `RutFirma`/`Declaracion`).
        `caratula` trae `RutResponde`/`RutRecibe`.
        """
        response = self._client.call_response(
            self._BUILD_ENVIO_RECIBOS_OPERATION,
            bag={
                'tipo': 'envio_recibos',
                'caratula': caratula,
                'data': recibos,
                'certificate': certificate.to_payload(),
            },
        )
        return build_response(EnvioRecibos, response)

    def build_respuesta_envio(
        self,
        data: dict[str, Any],
        *,
        caratula: dict[str, Any],
        certificate: Certificate,
    ) -> RespuestaEnvio:
        """
        Construye el XML `RespuestaDTE` firmado.

        `data` trae `recepcion_envio` o `resultado_dte` (listas), tal
        cual el formato SII. `caratula` trae `RutResponde`/`RutRecibe`/
        `IdRespuesta`.
        """
        response = self._client.call_response(
            self._BUILD_RESPUESTA_ENVIO_OPERATION,
            bag={
                'tipo': 'respuesta_envio',
                'caratula': caratula,
                'data': data,
                'certificate': certificate.to_payload(),
            },
        )
        return build_response(RespuestaEnvio, response)

    def validate_schema(self, source: str) -> dict[str, Any]:
        """
        Valida `source` contra el esquema XSD del documento de respuesta.

        `source` es el XML del documento de respuesta, en base64.
        """
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SCHEMA_OPERATION,
                source=source,
            ),
        )

    def validate_signature(self, source: str) -> list[dict[str, Any]]:
        """
        Valida cada firma electrónica del documento de respuesta.

        `EnvioRecibos` trae múltiples firmas (una por recibo, más la
        del `SetRecibos`); `RespuestaDTE` trae solo la del nodo
        `Resultado`. En ambos casos se devuelve una lista, un ítem por
        firma.
        """
        return cast(
            'list[dict[str, Any]]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
