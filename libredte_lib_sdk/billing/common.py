# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Utilidades compartidas entre los componentes de `billing`."""

from __future__ import annotations

import base64


class XmlPayloadMixin:
    """
    Mixin para un DTO cuyo dato principal es un XML en base64.

    Espera un atributo `xml_base64: str` en la clase concreta (`Document`,
    `DocumentEnvelope`, `Caf`, ...) y expone `xml_bytes`/`xml` sobre él,
    para no repetir esta misma conversión en cada DTO.
    """

    __slots__ = ()

    xml_base64: str

    @property
    def xml_bytes(self) -> bytes:
        """XML decodificado desde base64."""
        return base64.b64decode(self.xml_base64)

    @property
    def xml(self) -> str:
        """XML como texto (ISO-8859-1, la codificación que usa el SII)."""
        return self.xml_bytes.decode('iso-8859-1')
