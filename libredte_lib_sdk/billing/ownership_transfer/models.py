# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.ownership_transfer`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common import XmlPayloadMixin


@dataclass(frozen=True, slots=True)
class Aec(XmlPayloadMixin):
    """
    AEC (Archivo Electrónico de Cesión) construido (`aec::build`).

    `aec` es la estructura ya parseada (bajo la clave `AEC` en la
    respuesta cruda de la API), `xml_base64` el XML completo — permite
    encadenar a `AecService.validate_schema`/`.validate_signature` o a
    `SiiRtcService.send_aec`.
    """

    aec: dict[str, Any]
    xml_base64: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Aec:
        """Construye un `Aec` desde el `data` que devuelve la API."""
        return cls(aec=data.get('AEC') or {}, xml_base64=data['xml'])
