# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `system.certificate.loader`."""

from __future__ import annotations

import base64

from ...billing.trading_parties.models import Certificate
from ...client import ApiClient


class CertificateLoaderService:
    """
    Carga un certificado digital real (`system.certificate.loader::load`).

    Recibe el archivo `.p12`/`.pfx` tal cual (bytes crudos) y su
    contraseña; la API desempaqueta el certificado y extrae RUT/nombre/
    correo.
    """

    _LOAD_OPERATION = 'system.certificate.loader::load'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def load(self, data: bytes, password: str) -> Certificate:
        """Carga el certificado de `data`, protegido con `password`."""
        result = self._client.call(
            self._LOAD_OPERATION,
            certificate={
                'data': base64.b64encode(data).decode(),
                'password': password,
            },
        )
        return Certificate.from_api(result)
