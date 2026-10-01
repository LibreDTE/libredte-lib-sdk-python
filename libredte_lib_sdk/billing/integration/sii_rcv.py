# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.integration.sii_rcv`."""

from __future__ import annotations

from ...client import ApiClient
from ...response_registry import build_response
from ..enums import SiiEnvironment
from ..trading_parties.models import Certificate
from .models import (
    CheckDocumentAssignabilityResponse,
    GetDocumentSiiReceptionDateResponse,
    ListDocumentEventsResponse,
    SubmitDocumentAcceptanceResponse,
)


class SiiRcvService:
    """
    Registro de Compra y Venta del SII (`billing.integration.sii_rcv`).

    Cubre las 4 operaciones del worker — todo el lado "recibo un
    documento de un tercero" (cesión, recepción, reclamos), no el de
    emitir un DTE propio (eso es `SiiDteService`).
    """

    _CHECK_ASSIGNABILITY_OPERATION = (
        'billing.integration.sii_rcv::checkDocumentAssignability'
    )
    _GET_RECEPTION_DATE_OPERATION = (
        'billing.integration.sii_rcv::getDocumentSiiReceptionDate'
    )
    _LIST_EVENTS_OPERATION = 'billing.integration.sii_rcv::listDocumentEvents'
    _SUBMIT_ACCEPTANCE_OPERATION = (
        'billing.integration.sii_rcv::submitDocumentAcceptance'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def check_document_assignability(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
    ) -> CheckDocumentAssignabilityResponse:
        """Consulta si un documento es cedible (apto para factoring)."""
        response = self._client.call_response(
            self._CHECK_ASSIGNABILITY_OPERATION,
            request={
                'certificate': certificate.to_payload(),
                'options': {'environment': int(environment)},
            },
            company=company_rut,
            document=document_type,
            number=number,
        )
        return build_response(CheckDocumentAssignabilityResponse, response)

    def get_document_sii_reception_date(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
    ) -> GetDocumentSiiReceptionDateResponse:
        """Consulta la fecha de recepción de un documento en el SII."""
        response = self._client.call_response(
            self._GET_RECEPTION_DATE_OPERATION,
            request={
                'certificate': certificate.to_payload(),
                'options': {'environment': int(environment)},
            },
            company=company_rut,
            document=document_type,
            number=number,
        )
        return build_response(GetDocumentSiiReceptionDateResponse, response)

    def list_document_events(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
    ) -> ListDocumentEventsResponse:
        """Lista los eventos (acuses, reclamos, etc.) de un documento."""
        response = self._client.call_response(
            self._LIST_EVENTS_OPERATION,
            request={
                'certificate': certificate.to_payload(),
                'options': {'environment': int(environment)},
            },
            company=company_rut,
            document=document_type,
            number=number,
        )
        return build_response(ListDocumentEventsResponse, response)

    def submit_document_acceptance(
        self,
        *,
        company_rut: str,
        document_type: int,
        number: int,
        action: str,
        certificate: Certificate,
        environment: SiiEnvironment = SiiEnvironment.PRODUCTION,
    ) -> SubmitDocumentAcceptanceResponse:
        """
        Informa al SII la aceptación/reclamo de un documento recibido.

        `action` no se modela como enum cerrado (ej. `'ACD'` acepta
        contenido, `'RCD'` reclama contenido) — la propia API valida
        los valores conocidos.
        """
        response = self._client.call_response(
            self._SUBMIT_ACCEPTANCE_OPERATION,
            request={
                'certificate': certificate.to_payload(),
                'options': {'environment': int(environment)},
            },
            company=company_rut,
            document=document_type,
            number=number,
            action=action,
        )
        return build_response(SubmitDocumentAcceptanceResponse, response)
