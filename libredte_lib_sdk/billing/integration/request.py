# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Datos de conexión de una llamada al SII (`request` de la API)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..enums import SiiEnvironment
from ..trading_parties.models import Certificate


@dataclass(frozen=True, slots=True)
class SiiRequestOptions:
    """
    Reintentos y tiempos de una llamada al SII.

    Cada valor es opcional: el que no se indica lo resuelve la API con el
    suyo. La API ajusta cada valor a su rango.

    - `retries`: cantidad máxima de intentos de la llamada, de 1 a 10.
    - `timeout`: segundos máximos de cada intento, de 10 a 60.
    - `max_duration`: segundos máximos de la llamada, sumando sus intentos
      y las pausas entre ellos, de 10 a 300. La autenticación con el SII
      es una llamada aparte, con su propio tiempo.
    """

    retries: int | None = None
    timeout: int | None = None
    max_duration: int | None = None


def build_request(
    certificate: Certificate,
    environment: SiiEnvironment,
    options: SiiRequestOptions | None = None,
) -> dict[str, Any]:
    """Arma el `request` que esperan las operaciones `sii_*` de la API."""
    request_options: dict[str, Any] = {'environment': int(environment)}
    if options is not None:
        for name in ('retries', 'timeout', 'max_duration'):
            value = getattr(options, name)
            if value is not None:
                request_options[name] = value

    return {
        'certificate': certificate.to_payload(),
        'options': request_options,
    }
