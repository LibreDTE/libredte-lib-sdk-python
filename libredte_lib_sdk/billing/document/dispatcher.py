# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.dispatcher`."""

from __future__ import annotations

from typing import Any, cast

from ...client import ApiClient
from ..trading_parties.models import Certificate
from .models import DocumentEnvelope


class DocumentDispatcherService:
    """Arma y valida el sobre `EnvioDTE` (`billing.document.dispatcher`)."""

    _CREATE_OPERATION = 'billing.document.dispatcher::create'
    _LOAD_XML_OPERATION = 'billing.document.dispatcher::loadXml'
    _VALIDATE_OPERATION = 'billing.document.dispatcher::validate'
    _VALIDATE_SCHEMA_OPERATION = 'billing.document.dispatcher::validateSchema'
    _VALIDATE_SIGNATURE_OPERATION = (
        'billing.document.dispatcher::validateSignature'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def create(
        self,
        document_xml_base64: str,
        *,
        certificate: Certificate,
        emisor: dict[str, Any],
    ) -> DocumentEnvelope:
        """
        Envuelve y firma un documento ya timbrado en un sobre `EnvioDTE`.

        `document_xml_base64` es el XML en base64 del documento a
        envolver — típicamente `Document.xml_base64` de un documento ya
        timbrado y firmado (`DocumentBuilderService.build_signed`). El
        sobre resultante es lo que se envía al SII (`SiiDteService.send`).

        `emisor` es un `dict` con `rut`/`razon_social`/
        `autorizacion_dte` (esta última con `fecha_resolucion`/
        `numero_resolucion`), tal como lo espera la API.
        """
        data = self._client.call(
            self._CREATE_OPERATION,
            bag={
                'xmlDocument': document_xml_base64,
                'certificate': certificate.to_payload(),
                'emisor': emisor,
            },
        )
        return DocumentEnvelope.from_api(data)

    def load_xml(self, xml_base64: str) -> DocumentEnvelope:
        """
        Carga un sobre `EnvioDTE` ya existente desde su XML (base64).

        Caso de uso típico: reprocesar un sobre ya guardado, o normalizar
        un DTE suelto recibido de un tercero (la API arma un sobre nuevo
        a partir de él).
        """
        data = self._client.call(self._LOAD_XML_OPERATION, xml=xml_base64)
        return DocumentEnvelope.from_api(data)

    def validate(self, source: str) -> dict[str, Any]:
        """
        Valida un sobre `EnvioDTE` ya construido (`source`, XML en base64).

        Devuelve el XML del sobre, como `dict` (representación parseada,
        ej. `EnvioDTE.SetDTE.Caratula...`).
        """
        return cast(
            'dict[str, Any]',
            self._client.call(self._VALIDATE_OPERATION, source=source),
        )

    def validate_schema(self, source: str) -> dict[str, Any]:
        """Valida `source` contra el esquema XSD del sobre `EnvioDTE`."""
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SCHEMA_OPERATION,
                source=source,
            ),
        )

    def validate_signature(self, source: str) -> list[dict[str, Any]]:
        """
        Valida cada firma electrónica encontrada en el sobre.

        Un sobre trae más de una firma (la del DTE y la del propio
        `EnvioDTE`) — devuelve una lista, un ítem por firma. Cada ítem
        es un `dict` vacío en caso de éxito.
        """
        return cast(
            'list[dict[str, Any]]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
