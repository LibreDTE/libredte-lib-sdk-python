# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.integration.sii_rtc`."""

from __future__ import annotations

from ...client import ApiClient
from ..enums import SiiEnvironment
from ..trading_parties.models import Certificate
from .models import SendAecResponse


class SiiRtcService:
    """
    Envía un AEC al SII (Registro de Transferencia de Créditos).

    Solo cubre `sendAec`, para el AEC (Archivo Electrónico de Cesión)
    armado por `OwnershipTransferComponent.aec.build()`.
    """

    _SEND_AEC_OPERATION = 'billing.integration.sii_rtc::sendAec'

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
        retries: int | None = None,
    ) -> SendAecResponse:
        """
        Envía el AEC (XML en base64) al SII y devuelve su Track ID.

        `company_rut` es el RUT del cedente. `email_notif` es el correo
        al que el SII notificará el resultado del procesamiento del AEC
        (obligatorio para la API, no configurable desde otro lugar).
        """
        data = self._client.call(
            self._SEND_AEC_OPERATION,
            request={
                'certificate': certificate.to_payload(),
                'options': {'environment': int(environment)},
            },
            doc=aec_xml_base64,
            company=company_rut,
            emailNotif=email_notif,
            retries=retries,
        )
        return SendAecResponse.from_api(data)
