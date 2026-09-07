# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.integration`: integración con el SII."""

from __future__ import annotations

from ...client import ApiClient
from .models import (
    CheckDocumentAssignabilityResponse,
    CheckXmlDocumentSentStatusResponse,
    DocumentEvent,
    GetDocumentSiiReceptionDateResponse,
    ListDocumentEventsResponse,
    RequestXmlDocumentSentStatusByEmailResponse,
    SendAecResponse,
    SendXmlDocumentResponse,
    SubmitDocumentAcceptanceResponse,
    ValidateDocumentResponse,
    ValidateDocumentSignatureResponse,
)
from .sii_dte import SiiDteService
from .sii_rcv import SiiRcvService
from .sii_rtc import SiiRtcService

__all__ = [
    'CheckDocumentAssignabilityResponse',
    'CheckXmlDocumentSentStatusResponse',
    'DocumentEvent',
    'GetDocumentSiiReceptionDateResponse',
    'IntegrationComponent',
    'ListDocumentEventsResponse',
    'RequestXmlDocumentSentStatusByEmailResponse',
    'SendAecResponse',
    'SendXmlDocumentResponse',
    'SiiDteService',
    'SiiRcvService',
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
        self.sii_rcv = SiiRcvService(client)
        self.sii_rtc = SiiRtcService(client)
