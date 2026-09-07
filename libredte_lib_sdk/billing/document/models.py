# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
DTO del componente `billing.document`.

`Encabezado`/`Detalle`/etc. se pasan como `dict` tal cual el formato
SII (ver `builder.py`); estas clases tipan solo lo que el SDK arma o
recibe de la API.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

from ..common import XmlPayloadMixin


@dataclass(frozen=True, slots=True)
class Document(XmlPayloadMixin):
    """
    Documento tributario construido.

    Puede ser un borrador, un documento timbrado, o timbrado y firmado —
    lo distingue `is_timbrado` (`ted is not None`), no una subclase
    distinta: es el mismo recurso en distintos estados, según qué datos
    se le hayan pasado a `DocumentBuilderService`.
    """

    id: str
    datos: dict[str, Any]
    ted: dict[str, Any] | None
    xml_base64: str

    @property
    def is_timbrado(self) -> bool:
        """Si el documento ya tiene Timbre Electrónico (TED)."""
        return self.ted is not None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Document:
        """Construye un `Document` desde el `data` que devuelve la API."""
        return cls(
            id=data['id'],
            datos=data.get('datos') or {},
            ted=data.get('ted'),
            xml_base64=data['xml'],
        )


@dataclass(frozen=True, slots=True)
class DocumentBag:
    """
    Bolsa normalizada devuelta por `document.loader::loadXml`.

    No trae el XML del documento ni `id` — solo la bolsa ya
    normalizada: `datos` (`Encabezado`/`Detalle`), `document_type`
    (metadatos del tipo de documento: `codigo`, `nombre`, `categoria`,
    `es_boleta`, etc., sin tipar) y `stamp_xml` (el TED, como XML
    plano, no en base64 ni parseado). Sirve para reconstruir los datos
    de un DTE ya emitido a partir de su XML.
    """

    datos: dict[str, Any]
    document_type: dict[str, Any]
    stamp_xml: str | None
    extra: dict[str, Any] | None
    auth: dict[str, Any] | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentBag:
        """Construye un `DocumentBag` desde el `data` de la API."""
        return cls(
            datos=data['document'],
            document_type=data['document_type'],
            stamp_xml=data.get('document_stamp'),
            extra=data.get('document_extra'),
            auth=data.get('document_auth'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class DocumentEnvelope(XmlPayloadMixin):
    """Sobre `EnvioDTE` construido y firmado, listo para enviar al SII."""

    tag: str
    xml_base64: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentEnvelope:
        """Construye un `DocumentEnvelope` desde el `data` de la API."""
        return cls(tag=data['tag'], xml_base64=data['xml'])


@dataclass(frozen=True, slots=True)
class RenderedDocument:
    """
    Un archivo generado por un renderizador.

    Ej. `DocumentRendererService.render()`, `PayrollRendererService
    .render()`. `content_base64` es el archivo completo en base64 (un PDF, un
    HTML, lo que sea — `mime_type` dice qué es).
    `label` es la presentación pedida en `renderings` (ej.
    `'tributaria'`, `'cedible'`) cuando el renderizador modela más de
    una presentación posible; `None` cuando no aplica (ej. una
    liquidación de sueldo, que siempre es un único archivo).
    `copies`/`copy_number` identifican esta copia entre las pedidas de
    ese mismo `label` (ej. `copies=2, copy_number=1` es la primera de
    2 copias tributarias). El nombre de los campos en la API
    (`content`/`mimeType`/`filename`/`copyNumber`) es camelCase; acá
    quedan en snake_case como el resto del SDK.
    """

    content_base64: str
    mime_type: str
    filename: str
    label: str | None
    copies: int
    copy_number: int

    @property
    def content_bytes(self) -> bytes:
        """Contenido del archivo, decodificado desde base64."""
        return base64.b64decode(self.content_base64)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RenderedDocument:
        """Construye desde un ítem de `data.renderings`."""
        return cls(
            content_base64=data['content'],
            mime_type=data['mimeType'],
            filename=data['filename'],
            label=data.get('label'),
            copies=data['copies'],
            copy_number=data['copyNumber'],
        )


@dataclass(frozen=True, slots=True)
class ExampleSummary:
    """Un ejemplo listado por `DocumentExamplesService.list()`."""

    id: str
    category: str
    case: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ExampleSummary:
        """Construye un `ExampleSummary` desde un ítem de la lista."""
        return cls(
            id=data['id'],
            category=data['category'],
            case=data['case'],
        )


@dataclass(frozen=True, slots=True)
class Example:
    """
    Un ejemplo de documento, tal como lo devuelve `examples::get()`.

    `parsed_data` es directamente el `parsedData` que esperan
    `DocumentBuilderService.build_draft()`/`.build_signed()` — mismo
    `Encabezado`/`Detalle` que usa el resto del SDK, sin transformación.
    `expected` son los valores esperados del caso (totales, etc.) que usa
    la suite de tests de `libredte-lib-core` para validarlo — información
    de referencia, no un dato del documento en sí.
    """

    id: str
    parsed_data: dict[str, Any]
    expected: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Example:
        """Construye un `Example` desde el `data` que devuelve la API."""
        return cls(
            id=data['id'],
            parsed_data=data['example'],
            expected=data.get('expected') or {},
        )


@dataclass(frozen=True, slots=True)
class RenderResult:
    """
    Resultado de un renderizador.

    Ej. `DocumentRendererService.render()`, `PayrollRendererService
    .render()`. `renderings` trae un ítem por copia generada. Para
    `document.renderer`:
    por defecto (sin pedir `renderings` explícito) es un único
    `'tributaria'`; pidiendo más de una presentación y/o copia (ej.
    `renderings={'tributaria': 2, 'cedible': 1}`), trae uno por cada
    copia efectivamente generada — una presentación que la API no pudo
    generar para ese documento (ej. `'cedible'` en un tipo de documento
    sin acuse de recibo) se omite en silencio, no rompe la llamada. Para
    `payroll.renderer` (que no modela presentaciones) siempre trae un
    único elemento, sin `label`.
    `.first` es un atajo para el caso más común (un solo archivo);
    `.by_label()` filtra por presentación cuando se pidió más de una.
    """

    renderings: tuple[RenderedDocument, ...]

    @property
    def first(self) -> RenderedDocument:
        """El primer archivo generado."""
        return self.renderings[0]

    def by_label(self, label: str) -> tuple[RenderedDocument, ...]:
        """Los renderings de una presentación (ej. `'tributaria'`)."""
        return tuple(r for r in self.renderings if r.label == label)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> RenderResult:
        """Construye un `RenderResult` desde el `data` que devuelve la API."""
        return cls(
            renderings=tuple(
                RenderedDocument.from_api(item) for item in data['renderings']
            ),
        )
