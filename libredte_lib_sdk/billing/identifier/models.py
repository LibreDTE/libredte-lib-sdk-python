# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.identifier`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common import XmlPayloadMixin


@dataclass(frozen=True, slots=True)
class Caf(XmlPayloadMixin):
    """
    CAF (Código de Autorización de Folios) de un emisor.

    Expone los campos más usados directamente; `.raw` trae el `dict`
    completo que devuelve la API (incluye además, entre otros, la
    llave RSA del CAF y si está vigente) por si algo más específico
    hace falta más adelante.
    """

    tipo_documento: int
    folio_desde: int
    folio_hasta: int
    xml_base64: str
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Caf:
        """Construye un `Caf` desde el `data` que devuelve la API."""
        return cls(
            tipo_documento=data['tipoDocumento'],
            folio_desde=data['folioDesde'],
            folio_hasta=data['folioHasta'],
            xml_base64=data['xml'],
            raw=data,
        )
