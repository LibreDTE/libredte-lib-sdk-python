# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
SDK Python para la API de LibreDTE Lib (facturación electrónica Chile).

Expone `LibreDTE`, el punto de entrada del SDK (``sdk = LibreDTE()``).
DTO, servicios, componentes, excepciones y `ApiClient` se importan
desde su propio módulo (`billing.document`, `billing.trading_parties`,
`system.repository`, `human_resources.payroll`, `exceptions`, `client`,
etc.).
"""

from __future__ import annotations

from .sdk import LibreDTE

__all__ = ['LibreDTE']
