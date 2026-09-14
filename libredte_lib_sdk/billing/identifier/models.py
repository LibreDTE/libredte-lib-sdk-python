# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.identifier`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..common import XmlPayloadMixin
from ..enums import SiiEnvironment


@dataclass(frozen=True, slots=True)
class Caf(XmlPayloadMixin):
    """
    CAF (Código de Autorización de Folios) de un emisor.

    Expone todos los campos que devuelve la API — es el estado real del
    CAF al momento de la consulta (`vigente`/`meses_autorizacion`
    dependen de la fecha en que se pidió, no son un valor fijo). `.raw`
    igual se conserva con el `dict` completo, por si la API agrega algo
    nuevo que este DTO todavía no tipa.
    """

    id: str
    emisor: dict[str, str]
    tipo_documento: int
    folio_desde: int
    folio_hasta: int
    cantidad_folios: int
    fecha_autorizacion: str
    fecha_vencimiento: str | None
    meses_autorizacion: float
    vigente: bool
    vence: bool
    idk: int
    ambiente: SiiEnvironment | None
    certificacion: int | None
    public_key: str
    private_key: str
    xml_base64: str
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Caf:
        """Construye un `Caf` desde el `data` que devuelve la API."""
        ambiente = data.get('ambiente')
        return cls(
            id=data['id'],
            emisor=data['emisor'],
            tipo_documento=data['tipoDocumento'],
            folio_desde=data['folioDesde'],
            folio_hasta=data['folioHasta'],
            cantidad_folios=data['cantidadFolios'],
            fecha_autorizacion=data['fechaAutorizacion'],
            fecha_vencimiento=data.get('fechaVencimiento'),
            meses_autorizacion=data['mesesAutorizacion'],
            vigente=data['vigente'],
            vence=data['vence'],
            idk=data['idk'],
            ambiente=SiiEnvironment(ambiente)
            if ambiente is not None
            else None,
            # Mismo valor que `ambiente`, ya resuelto a `int` — la API lo
            # entrega redundante así (`Caf::getCertificacion()` en
            # libredte-lib-core es literalmente `getEnvironment()?->value`),
            # se mantiene igual acá para no diverger del shape real.
            certificacion=data.get('certificacion'),
            public_key=data['publicKey'],
            private_key=data['privateKey'],
            xml_base64=data['xml'],
            raw=data,
        )
