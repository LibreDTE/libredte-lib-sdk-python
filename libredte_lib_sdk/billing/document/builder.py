# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.builder`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from ...response_registry import build_response
from ..common import encode_input_data
from ..trading_parties.models import Certificate
from .models import DocumentBag


class DocumentBuilderService:
    """
    Construye documentos tributarios (`billing.document.builder`).

    El mismo worker de la API sirve tanto para un borrador como para el
    documento timbrado y firmado, según qué datos se le pasen — acá se
    separa en dos métodos explícitos para que la intención de cada
    llamada quede clara en el código que la usa.
    """

    _BUILD_OPERATION = 'billing.document.builder::build'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def build_draft(
        self,
        input_data: str | bytes | dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
    ) -> DocumentBag:
        """
        Emite el borrador de un DTE a partir de datos de entrada.

        `input_data` es el `Encabezado`/`Detalle` (y demás nodos) del
        formato DTE del SII como `dict` — o datos en otro formato
        (XML/YAML, un formulario, etc.), como `bytes` o `str`, junto con
        `options={'parser': {'strategy': '<estrategia>'}}` para indicar
        cómo parsearlos. El contenido de un archivo se debe pasar como
        `bytes` (leído en modo `rb`): se envía sin alterar su
        codificación. Un `str` ya es texto decodificado y se envía en
        UTF-8. Sin `options`, la API asume que `input_data` ya
        viene en el formato DTE del SII (estrategia `default.json`).
        `Encabezado.IdDoc.Folio` es opcional acá — un borrador sin folio
        no falla (queda con folio `0` en `DocumentBag.document_id`, sin
        nodo `Folio` en el XML). Sin CAF ni certificado, el resultado no
        queda timbrado (`DocumentBag.is_timbrado` es `False`).
        """
        bag: dict[str, Any] = {'inputData': encode_input_data(input_data)}
        if options is not None:
            bag['options'] = options

        response = self._client.call_response(self._BUILD_OPERATION, bag=bag)
        return build_response(DocumentBag, response)

    def build_signed(
        self,
        input_data: str | bytes | dict[str, Any],
        *,
        options: dict[str, Any] | None = None,
        caf_xml: str,
        certificate: Certificate,
    ) -> DocumentBag:
        """
        Genera el DTE real, timbrado y firmado.

        `input_data`/`options` funcionan igual que en `build_draft()` —
        acá sí se necesita un `Encabezado.IdDoc.Folio` real, cubierto
        por `caf_xml` (el SDK no asigna folios: eso lo decide quien
        llama, típicamente porque lleva el correlativo). Requiere un CAF
        real (XML tal como lo entrega el SII) y el certificado digital
        del emisor. Para pruebas, ambos se pueden generar con
        `IdentifierComponent.caf_faker` y
        `TradingPartiesComponent.mandatario_manager`.
        """
        bag: dict[str, Any] = {'inputData': encode_input_data(input_data)}
        if options is not None:
            bag['options'] = options
        bag['caf'] = caf_xml
        bag['certificate'] = certificate.to_payload()

        response = self._client.call_response(self._BUILD_OPERATION, bag=bag)
        return build_response(DocumentBag, response)
