# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.integration.sii_rtc`."""

from __future__ import annotations

from ...client import ApiClient
from ...response_registry import build_response
from ..enums import SiiEnvironment
from ..trading_parties.models import Certificate
from .models import (
    CheckAecSentStatusResponse,
    GetAssignmentStatusResponse,
    SendAecResponse,
)
from .request import SiiRequestOptions, build_request


class SiiRtcService:
    """
    Envía un AEC al SII y consulta cesiones (Registro de Créditos).

    `send_aec` envía el AEC (Archivo Electrónico de Cesión) armado por
    `OwnershipTransferComponent.aec.build()`; `check_status` consulta su
    estado; `get_assignment_status` y `get_related_assignment_status`
    consultan el estado de la cesión de un documento.

    Cada método acepta `options` (`SiiRequestOptions`) para ajustar los
    reintentos y los tiempos de la llamada al SII.
    """

    _SEND_AEC_OPERATION = 'billing.integration.sii_rtc::send_aec'
    _CHECK_STATUS_OPERATION = (
        'billing.integration.sii_rtc::check_aec_sent_status'
    )
    _ASSIGNMENT_STATUS_OPERATION = (
        'billing.integration.sii_rtc::get_assignment_status'
    )
    _RELATED_ASSIGNMENT_STATUS_OPERATION = (
        'billing.integration.sii_rtc::get_related_assignment_status'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def send_aec(
        self,
        aec_xml_base64: str,
        *,
        certificate: Certificate,
        company_rut: str,
        email_notif: str,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
        retries: int | None = None,
    ) -> SendAecResponse:
        """
        Envía el AEC (XML en base64) al SII y devuelve su Track ID.

        `company_rut` es el RUT del cedente. `email_notif` es el correo
        al que el SII notificará el resultado del procesamiento del AEC
        (obligatorio para la API, no configurable desde otro lugar).
        """
        response = self._client.call_response(
            self._SEND_AEC_OPERATION,
            request=build_request(certificate, environment, options),
            doc=aec_xml_base64,
            company=company_rut,
            emailNotif=email_notif,
            retries=retries,
        )
        return build_response(SendAecResponse, response)

    def check_status(
        self,
        track_id: int,
        *,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> CheckAecSentStatusResponse:
        """
        Consulta el estado de un AEC enviado, mediante su Track ID.

        Mientras `final` sea `False` se repite la consulta más adelante.
        """
        response = self._client.call_response(
            self._CHECK_STATUS_OPERATION,
            request=build_request(certificate, environment, options),
            trackId=track_id,
        )
        return build_response(CheckAecSentStatusResponse, response)

    def get_assignment_status(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        certificate: Certificate,
        assignment_id: str | None = None,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> GetAssignmentStatusResponse:
        """
        Consulta si un documento está cedido y, con la clave, su cesión.

        `company_rut` es el RUT del emisor del documento y
        `document_type` es `33` o `34`. `assignment_id` es la clave de
        acceso a la información de la cesión: sin ella la respuesta solo
        informa si el documento está cedido.
        """
        response = self._client.call_response(
            self._ASSIGNMENT_STATUS_OPERATION,
            request=build_request(certificate, environment, options),
            company=company_rut,
            document=document_type,
            number=number,
            assignmentId=assignment_id,
        )
        return build_response(GetAssignmentStatusResponse, response)

    def get_related_assignment_status(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        related_company_rut: str,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
        options: SiiRequestOptions | None = None,
    ) -> GetAssignmentStatusResponse:
        """
        Consulta la cesión de un documento como empresa relacionada.

        `related_company_rut` es el RUT de la empresa vinculada con la
        cesión, ya sea como tenedor o como receptor del documento.
        """
        response = self._client.call_response(
            self._RELATED_ASSIGNMENT_STATUS_OPERATION,
            request=build_request(certificate, environment, options),
            company=company_rut,
            document=document_type,
            number=number,
            relatedCompany=related_company_rut,
        )
        return build_response(GetAssignmentStatusResponse, response)
