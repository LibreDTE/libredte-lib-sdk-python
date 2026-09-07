# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.builder`."""

from __future__ import annotations

from typing import Any

from ...client import ApiClient
from ..trading_parties.models import Certificate
from .models import Document


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

    def build_draft(self, parsed_data: dict[str, Any]) -> Document:
        """
        Emite el borrador de un DTE a partir de datos ya normalizados.

        `parsed_data` es el `Encabezado`/`Detalle` (y demás nodos) del
        formato DTE del SII, incluyendo `Encabezado.IdDoc.Folio` (el SDK
        no asigna folios: eso lo decide quien llama, típicamente porque
        lleva el correlativo). Sin CAF ni certificado, el resultado no
        queda timbrado (`Document.is_timbrado` es `False`).
        """
        data = self._client.call(
            self._BUILD_OPERATION,
            bag={'parsedData': parsed_data},
        )
        return Document.from_api(data)

    def build_signed(
        self,
        parsed_data: dict[str, Any],
        *,
        caf_xml: str,
        certificate: Certificate,
    ) -> Document:
        """
        Genera el DTE real, timbrado y firmado.

        Requiere un CAF real (XML tal como lo entrega el SII, cubriendo
        el folio indicado en `parsed_data`) y el certificado digital del
        emisor. Para pruebas, ambos se pueden generar con
        `IdentifierComponent.caf_faker` y
        `TradingPartiesComponent.mandatario_manager`.
        """
        data = self._client.call(
            self._BUILD_OPERATION,
            bag={
                'parsedData': parsed_data,
                'caf': caf_xml,
                'certificate': certificate.to_payload(),
            },
        )
        return Document.from_api(data)
