# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.identifier.caf_validator`."""

from __future__ import annotations

from ...client import ApiClient
from .models import Caf


class CafValidatorService:
    """
    Valida un CAF (`billing.identifier.caf_validator::validate`).

    Valida la firma y las llaves públicas/privadas asociadas al CAF.
    """

    _VALIDATE_OPERATION = 'billing.identifier.caf_validator::validate'

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def validate(self, caf_xml_base64: str) -> Caf:
        """
        Valida el CAF cuyo XML (en base64) es `caf_xml_base64`.

        La API espera el mismo XML en base64 que `CafLoaderService.load`
        (el parámetro de la operación se llama `caf`, no `xml`, pero es
        el mismo dato). Devuelve el `Caf` ya validado si es válido;
        levanta `LibreDteApiError` si no lo es.
        """
        data = self._client.call(self._VALIDATE_OPERATION, caf=caf_xml_base64)
        return Caf.from_api(data)
