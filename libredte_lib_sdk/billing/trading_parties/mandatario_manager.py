# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.trading_parties.mandatario_manager`."""

from __future__ import annotations

from ...client import ApiClient
from .models import Certificate, Mandatario


class MandatarioManagerService:
    """
    Gestión del mandatario (representante) dueño de un certificado.

    `create_fake_certificate()` genera un certificado ficticio para
    pruebas/desarrollo; `create_from_certificate()` hace el camino
    inverso, extrayendo el mandatario (RUT/nombre/correo) desde un
    certificado real ya cargado (ver `system.certificate.loader::load`).
    """

    _CREATE_FAKE_OPERATION = (
        'billing.trading_parties.mandatario_manager::createFakeCertificate'
    )
    _CREATE_FROM_CERTIFICATE_OPERATION = (
        'billing.trading_parties.mandatario_manager::createFromCertificate'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def create_fake_certificate(self, mandatario: Mandatario) -> Certificate:
        """
        Genera un certificado digital ficticio para `mandatario`.

        Únicamente para pruebas/desarrollo: el certificado resultante es
        autofirmado por una CA de prueba de LibreDTE, no sirve para
        autenticar de verdad ante el SII. El `Certificate` resultante ya
        viene con el RUT/nombre/correo/vigencia poblados.
        """
        data = self._client.call(
            self._CREATE_FAKE_OPERATION,
            mandatario=mandatario.to_payload(),
        )
        return Certificate.from_api(data)

    def create_from_certificate(self, certificate: Certificate) -> Mandatario:
        """Extrae el mandatario dueño de `certificate` (RUT/nombre/correo)."""
        data = self._client.call(
            self._CREATE_FROM_CERTIFICATE_OPERATION,
            certificate=certificate.to_payload(),
        )
        return Mandatario.from_api(data)
