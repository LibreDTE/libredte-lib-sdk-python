# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.exchange`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common import XmlPayloadMixin


@dataclass(frozen=True, slots=True)
class EnvioRecibos(XmlPayloadMixin):
    """
    XML `EnvioRecibos` construido (`document_response::buildEnvioRecibos`).

    Recibo de mercaderías o servicios prestados por un proveedor.
    `datos` es la estructura ya parseada, `xml_base64` el XML completo
    — permite encadenar a `validate_schema`/`validate_signature`.
    """

    datos: dict[str, Any]
    xml_base64: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> EnvioRecibos:
        """Construye un `EnvioRecibos` desde el `data` que devuelve la API."""
        return cls(
            datos={k: v for k, v in data.items() if k != 'xml'},
            xml_base64=data['xml'],
        )


@dataclass(frozen=True, slots=True)
class RespuestaEnvio(XmlPayloadMixin):
    """
    XML `RespuestaDTE` construido (`document_response::buildRespuestaEnvio`).

    Acuse de recibo del envío (`RecepcionEnvio`) o resultado de
    validación por documento (`ResultadoDTE`), según los datos
    entregados.
    """

    datos: dict[str, Any]
    xml_base64: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RespuestaEnvio:
        """Construye un `RespuestaEnvio` desde el `data` de la API."""
        return cls(
            datos={k: v for k, v in data.items() if k != 'xml'},
            xml_base64=data['xml'],
        )
