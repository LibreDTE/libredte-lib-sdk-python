# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.integration`: integración con el SII."""

from __future__ import annotations

from ...client import ApiClient
from .models import (
    CheckAecSentStatusResponse,
    CheckDocumentAssignabilityResponse,
    CheckXmlDocumentSentStatusResponse,
    DocumentEvent,
    GetAssignmentStatusResponse,
    GetDocumentSiiReceptionDateResponse,
    ListDocumentEventsResponse,
    RequestXmlDocumentSentStatusByEmailResponse,
    SendAecResponse,
    SendXmlDocumentResponse,
    SiiBoletaCheckXmlDocumentSentStatusResponse,
    SiiBoletaDocumentDetail,
    SiiBoletaDocumentError,
    SiiBoletaDocumentResume,
    SiiBoletaRateLimit,
    SiiBoletaResume,
    SiiBoletaSendXmlDocumentResponse,
    SiiBoletaValidateDocumentResponse,
    SubmitDocumentAcceptanceResponse,
    ValidateDocumentResponse,
    ValidateDocumentSignatureResponse,
)
from .request import SiiRequestOptions
from .sii_boleta import SiiBoletaService
from .sii_dte import SiiDteService
from .sii_rcv import SiiRcvService
from .sii_rtc import SiiRtcService

__all__ = [
    'CheckAecSentStatusResponse',
    'CheckDocumentAssignabilityResponse',
    'CheckXmlDocumentSentStatusResponse',
    'DocumentEvent',
    'GetAssignmentStatusResponse',
    'GetDocumentSiiReceptionDateResponse',
    'IntegrationComponent',
    'ListDocumentEventsResponse',
    'RequestXmlDocumentSentStatusByEmailResponse',
    'SendAecResponse',
    'SendXmlDocumentResponse',
    'SiiBoletaCheckXmlDocumentSentStatusResponse',
    'SiiBoletaDocumentDetail',
    'SiiBoletaDocumentError',
    'SiiBoletaDocumentResume',
    'SiiBoletaRateLimit',
    'SiiBoletaResume',
    'SiiBoletaSendXmlDocumentResponse',
    'SiiBoletaService',
    'SiiBoletaValidateDocumentResponse',
    'SiiDteService',
    'SiiRcvService',
    'SiiRequestOptions',
    'SiiRtcService',
    'SubmitDocumentAcceptanceResponse',
    'ValidateDocumentResponse',
    'ValidateDocumentSignatureResponse',
]


class IntegrationComponent:
    """Agrupa los servicios de `billing.integration`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.sii_dte = SiiDteService(client)
        self.sii_boleta = SiiBoletaService(client)
        self.sii_rcv = SiiRcvService(client)
        self.sii_rtc = SiiRtcService(client)
