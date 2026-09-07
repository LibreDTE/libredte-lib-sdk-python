# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Enumeraciones del paquete `billing`."""

from __future__ import annotations

from enum import IntEnum


class SiiEnvironment(IntEnum):
    """
    Ambiente del SII contra el que se opera.

    `PRODUCTION = 0` es el servidor real (`palena.sii.cl`);
    `CERTIFICATION = 1` es el servidor de pruebas (`maullin.sii.cl`).
    Es el default en los servicios que reciben este parámetro
    (`SiiDteService`, `SiiRtcService`, `SiiRcvService`).
    """

    PRODUCTION = 0
    CERTIFICATION = 1
