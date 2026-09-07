# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.trading_parties`."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Certificate:
    """
    Certificado digital (firma electrónica) de un mandatario/emisor.

    `certificate`/`private_key` son los únicos campos obligatorios — lo
    único que la API necesita cuando un `Certificate` se usa como
    *entrada* (`to_payload()`, para `build_signed()`,
    `dispatcher.create()`, `sii_dte.send()`, etc.). El resto queda
    poblado cuando el `Certificate` viene *de* la API
    (`create_fake_certificate()`, `system.certificate.loader::load()`).

    `certificate`/`private_key` van siempre en claro (PEM sin
    proteger): esta operación no acepta un PFX ni una clave protegida
    con contraseña. Si el certificado del emisor viene de un archivo
    `.pfx`, `system.certificate.loader::load` hace esa extracción.
    """

    certificate: str
    private_key: str
    rut: str | None = None
    nombre: str | None = None
    email: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    total_days: int | None = None
    expiration_days: int | None = None
    is_active: bool | None = None
    issuer: str | None = None
    modulus: str | None = None
    exponent: str | None = None
    chain: list[Any] | None = None
    raw: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        """Payload esperado por la API para un certificado."""
        return {
            'certificate': self.certificate,
            'privateKey': self.private_key,
        }

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Certificate:
        """
        Construye un `Certificate` desde el `data` que devuelve la API.

        Cubre tanto `createFakeCertificate` como `system.certificate
        .loader::load` — ambas entregan el mismo shape completo (`cert`/
        `pkey` + metadatos). Los campos ausentes quedan en `None`.
        """
        return cls(
            certificate=data['cert'],
            private_key=data['pkey'],
            rut=data.get('id'),
            nombre=data.get('name'),
            email=data.get('email'),
            valid_from=(
                datetime.fromisoformat(data['from'])
                if data.get('from')
                else None
            ),
            valid_until=(
                datetime.fromisoformat(data['to']) if data.get('to') else None
            ),
            total_days=data.get('totalDays'),
            expiration_days=data.get('expirationDays'),
            is_active=data.get('isActive'),
            issuer=data.get('issuer'),
            modulus=data.get('modulus'),
            exponent=data.get('exponent'),
            chain=data.get('chain'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class Mandatario:
    """Mandatario (representante) dueño de un certificado digital."""

    rut: str
    nombre: str
    email: str | None = None

    def to_payload(self) -> dict[str, Any]:
        """Payload esperado por la API para un mandatario."""
        payload: dict[str, Any] = {'run': self.rut, 'nombre': self.nombre}
        if self.email is not None:
            payload['email'] = self.email
        return payload

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Mandatario:
        """Construye un `Mandatario` desde el `data` que devuelve la API."""
        return cls(
            rut=data['run'],
            nombre=data['nombre'],
            email=data.get('email'),
        )
