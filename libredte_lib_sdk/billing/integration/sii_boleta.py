# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.integration.sii_boleta`."""

from __future__ import annotations

from ...client import ApiClient
from ...response_registry import build_response
from ..enums import SiiEnvironment
from ..trading_parties.models import Certificate
from .models import (
    SiiBoletaCheckXmlDocumentSentStatusResponse,
    SiiBoletaSendXmlDocumentResponse,
    SiiBoletaValidateDocumentResponse,
)
from .request import SiiRequestOptions, build_request


class SiiBoletaService:
    """
    Envío y consulta de boletas ante el SII (`billing.integration.sii_boleta`).

    El SII recibe las boletas (tipos 39 y 41) por una API distinta a la
    del resto de los DTE: para ellas se usa este servicio y no
    `SiiDteService`. Autentica contra el SII real con el certificado
    dado, igual que `SiiDteService`.

    Solo disponible en Lib Pro: contra una instancia de Lib Core estas
    operaciones no existen y levantan `LibreDteOperationNotFoundError`.

    Cada método acepta `options` (`SiiRequestOptions`) para ajustar los
    reintentos y los tiempos de la llamada al SII.
    """

    _SEND_OPERATION = 'billing.integration.sii_boleta::send_xml_document'
    _STATUS_OPERATION = (
        'billing.integration.sii_boleta::check_xml_document_sent_status'
    )
    _VALIDATE_DOCUMENT_OPERATION = (
        'billing.integration.sii_boleta::validate_document'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def send(
        self,
        envelope_xml_base64: str,
        *,
        certificate: Certificate,
        company_rut: str,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
        retries: int | None = None,
    ) -> SiiBoletaSendXmlDocumentResponse:
        """
        Envía el sobre `EnvioBOLETA` al SII y devuelve su Track ID.

        `envelope_xml_base64` es el XML en base64 del sobre ya armado
        (`DocumentEnvelope.xml_base64` de `DocumentDispatcherService
        .create`), con `receptor_rut=SII_RUT`. Solo acepta el sobre de
        boletas: un `EnvioDTE` se envía con `SiiDteService.send`.
        """
        response = self._client.call_response(
            self._SEND_OPERATION,
            request=build_request(certificate, environment, options),
            doc=envelope_xml_base64,
            company=company_rut,
            retries=retries,
        )
        return build_response(SiiBoletaSendXmlDocumentResponse, response)

    def check_status(
        self,
        track_id: int,
        *,
        certificate: Certificate,
        company_rut: str,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> SiiBoletaCheckXmlDocumentSentStatusResponse:
        """
        Consulta el estado de un envío de boletas mediante su Track ID.

        Mientras el estado no sea final (`REC`, `SOK`, `CRT`, `FOK`,
        `PRD`) se repite la consulta más adelante.
        """
        response = self._client.call_response(
            self._STATUS_OPERATION,
            request=build_request(certificate, environment, options),
            trackId=track_id,
            company=company_rut,
        )
        return build_response(
            SiiBoletaCheckXmlDocumentSentStatusResponse,
            response,
        )

    def validate_document(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        date: str,
        total: int,
        recipient_rut: str,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> SiiBoletaValidateDocumentResponse:
        """
        Consulta al SII si una boleta existe y los datos coinciden.

        `document_type` es `39` (boleta) o `41` (boleta exenta). Aunque
        el SII marca como opcionales la fecha, el total y el receptor,
        el servicio los exige. `date` en formato `AAAA-MM-DD`.
        """
        response = self._client.call_response(
            self._VALIDATE_DOCUMENT_OPERATION,
            request=build_request(certificate, environment, options),
            company=company_rut,
            document=document_type,
            number=number,
            date=date,
            total=total,
            recipient=recipient_rut,
        )
        return build_response(SiiBoletaValidateDocumentResponse, response)
