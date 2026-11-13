# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.integration.sii_dte`."""

from __future__ import annotations

from ...client import ApiClient
from ...response_registry import build_response
from ..enums import SiiEnvironment
from ..trading_parties.models import Certificate
from .models import (
    CheckXmlDocumentSentStatusResponse,
    RequestXmlDocumentSentStatusByEmailResponse,
    SendXmlDocumentResponse,
    ValidateDocumentResponse,
    ValidateDocumentSignatureResponse,
)
from .request import SiiRequestOptions, build_request


class SiiDteService:
    """
    Envío y consulta de estado ante el SII (`billing.integration.sii_dte`).

    Todas las operaciones autentican contra el SII real con el
    certificado dado; un certificado no válido para el SII (ej. uno
    autofirmado de prueba, como los que genera `TradingPartiesComponent
    .mandatario_manager.create_fake_certificate`) resulta en un
    `LibreDteApiError` (la propia excepción de autenticación del SII,
    accesible vía `.php_class`), no en una excepción distinta.

    Cada método acepta `options` (`SiiRequestOptions`) para ajustar los
    reintentos y los tiempos de la llamada al SII.
    """

    _SEND_OPERATION = 'billing.integration.sii_dte::send_xml_document'
    _STATUS_OPERATION = (
        'billing.integration.sii_dte::check_xml_document_sent_status'
    )
    _VALIDATE_DOCUMENT_OPERATION = (
        'billing.integration.sii_dte::validate_document'
    )
    _VALIDATE_DOCUMENT_SIGNATURE_OPERATION = (
        'billing.integration.sii_dte::validate_document_signature'
    )
    _REQUEST_STATUS_BY_EMAIL_OPERATION = (
        'billing.integration.sii_dte::'
        'request_xml_document_sent_status_by_email'
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
        compress: bool = False,
        retries: int | None = None,
    ) -> SendXmlDocumentResponse:
        """
        Envía el sobre `EnvioDTE` al SII y devuelve su Track ID.

        `envelope_xml_base64` es el XML en base64 del sobre ya armado
        (`DocumentEnvelope.xml_base64` de `DocumentDispatcherService.create`).
        """
        response = self._client.call_response(
            self._SEND_OPERATION,
            request=build_request(certificate, environment, options),
            doc=envelope_xml_base64,
            company=company_rut,
            compress=compress,
            retries=retries,
        )
        return build_response(SendXmlDocumentResponse, response)

    def check_status(
        self,
        track_id: int,
        *,
        certificate: Certificate,
        company_rut: str,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> CheckXmlDocumentSentStatusResponse:
        """Consulta el estado de un envío al SII mediante su Track ID."""
        response = self._client.call_response(
            self._STATUS_OPERATION,
            request=build_request(certificate, environment, options),
            trackId=track_id,
            company=company_rut,
        )
        return build_response(CheckXmlDocumentSentStatusResponse, response)

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
    ) -> ValidateDocumentResponse:
        """
        Confirma si un documento existe en el SII (aceptado o con reparos).

        Valida que el documento exista y que los datos dados (folio,
        fecha, total, receptor) coincidan con lo que el SII tiene
        registrado. `date` en formato `AAAA-MM-DD`.
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
        return build_response(ValidateDocumentResponse, response)

    def validate_document_signature(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        date: str,
        total: int,
        recipient_rut: str,
        signature: str,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> ValidateDocumentSignatureResponse:
        """
        Igual que `validate_document()`, verificando además la firma.

        `signature` es el tag `DTE/Signature/SignatureValue` del XML del
        documento (no el XML completo).
        """
        response = self._client.call_response(
            self._VALIDATE_DOCUMENT_SIGNATURE_OPERATION,
            request=build_request(certificate, environment, options),
            company=company_rut,
            document=document_type,
            number=number,
            date=date,
            total=total,
            recipient=recipient_rut,
            signature=signature,
        )
        return build_response(ValidateDocumentSignatureResponse, response)

    def request_status_by_email(
        self,
        track_id: int,
        *,
        certificate: Certificate,
        company_rut: str,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> RequestXmlDocumentSentStatusByEmailResponse:
        """
        Pide al SII que envíe el estado de un envío por correo.

        El correo de destino es el configurado en el SII para la
        empresa — no se puede indicar acá. El correo del SII incluye
        el detalle de los rechazos.
        """
        response = self._client.call_response(
            self._REQUEST_STATUS_BY_EMAIL_OPERATION,
            request=build_request(certificate, environment, options),
            trackId=track_id,
            company=company_rut,
        )
        return build_response(
            RequestXmlDocumentSentStatusByEmailResponse, response
        )
