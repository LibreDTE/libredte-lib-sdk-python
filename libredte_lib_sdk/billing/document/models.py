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
from ..identifier.models import Caf
from ..trading_parties.models import Certificate


@dataclass(frozen=True, slots=True)
class DocumentBag:
    """
    Bolsa de un documento tributario.

    Devuelta por `document.builder::build`/`document.loader::loadXml`
    — ambas en esta misma forma. `document`
    (`Encabezado`/`Detalle`, con el merge de `libredte_data.extra.dte`
    si se pasó al renderizar) es la vista "de datos" limpia del
    documento — SIN los campos opcionales no usados (se omiten, no
    quedan en `False`). `document_normalized` es la data cruda tal como
    la usa el builder internamente para generar el XML (con esos
    campos opcionales en `False` en vez de omitidos): es la que hay que
    guardar para poder reconstruir el documento después con
    `options={'normalizer': {'normalize': False}}` sin volver a
    normalizar — usar `document` para eso corrompe la reconstrucción.

    `document_id`/`xml_base64` dan el documento construido completo —
    puede ser un borrador, un documento timbrado, o timbrado y firmado,
    no una subclase distinta: es el mismo recurso en distintos estados
    según qué datos se le hayan pasado a `DocumentBuilderService`. Un
    borrador sin folio asignado tiene folio `0` en `document_id` (ver
    `AbstractDocument::getId()` en la biblioteca), nunca lanza error.

    `document_stamp_base64` es el TED — `None` si el documento aún no
    está timbrado (ver `is_timbrado`). `document_extra` son los campos
    que el tipo de documento no admite en el XML (ej. `TermPagoGlosa`
    en una boleta) pero sí se pasaron como `libredte_data` al construir.
    `document_auth` viene poblado solo si el emisor incluyó su
    autorización SII.

    `options` son las opciones efectivas de la bolsa (`builder`/
    `normalizer`/`parser`/`renderer`/`sanitizer`/`validator`), tal como
    las devuelve la API — vacías (`[]`) para el worker que no recibió
    ninguna al construir/cargar el documento.

    `certificate`/`caf` son `None` salvo que el documento se haya
    construido con ellos (`build_signed`, o un `loadXml` de un XML ya
    firmado/timbrado) — un borrador (`build_draft`) no los trae.
    `emisor`/`receptor` sí están siempre que haya un documento
    construido (`Encabezado.Emisor`/`Encabezado.Receptor` ya
    resueltos como entidad, con todos sus campos — no solo los que
    trae `document`). `timbre` es el TED ya parseado como `dict`
    (`document_stamp_base64` es el mismo dato, pero como XML) — `None`
    si el documento aún no está timbrado.

    No usa `XmlPayloadMixin`: acá `xml_base64` es una `@property` (el
    documento puede no estar construido), no un campo simple.
    """

    document: dict[str, Any]
    document_normalized: dict[str, Any] | None
    document_type: dict[str, Any]
    document_stamp_base64: str | None
    document_extra: dict[str, Any] | None
    document_auth: dict[str, Any] | None
    document_id: str | None
    document_xml_base64: str | None
    options: dict[str, Any]
    certificate: Certificate | None
    emisor: dict[str, Any] | None
    receptor: dict[str, Any] | None
    caf: Caf | None
    timbre: dict[str, Any] | None
    raw: dict[str, Any]

    @property
    def is_timbrado(self) -> bool:
        """Si el documento ya tiene Timbre Electrónico (TED)."""
        return self.document_stamp_base64 is not None

    @property
    def xml_base64(self) -> str:
        """XML completo del documento construido, en base64."""
        if self.document_xml_base64 is None:
            raise ValueError(
                'Este DocumentBag no tiene un documento construido — '
                '¿se llamó a `builder.build_draft/build_signed()` o a '
                '`loader.load_xml()`?',
            )
        return self.document_xml_base64

    @property
    def xml_bytes(self) -> bytes:
        """XML del documento construido, decodificado desde base64."""
        return base64.b64decode(self.xml_base64)

    @property
    def xml(self) -> str:
        """XML del documento construido, como texto (ISO-8859-1)."""
        return self.xml_bytes.decode('iso-8859-1')

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentBag:
        """Construye un `DocumentBag` desde el `data` de la API."""
        return cls(
            document=data['document'],
            document_normalized=data.get('document_normalized'),
            document_type=data['document_type'],
            document_stamp_base64=data.get('document_stamp'),
            document_extra=data.get('document_extra'),
            document_auth=data.get('document_auth'),
            document_id=data.get('document_id'),
            document_xml_base64=data.get('document_xml'),
            options=data.get('options') or {},
            certificate=Certificate.from_api(data['certificate'])
            if data.get('certificate')
            else None,
            emisor=data.get('emisor'),
            receptor=data.get('receptor'),
            caf=Caf.from_api(data['caf']) if data.get('caf') else None,
            timbre=data.get('timbre'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class DocumentEnvelope(XmlPayloadMixin):
    """
    Sobre `EnvioDTE`, ya sea recién construido o cargado desde un XML.

    `documents` trae una bolsa (`DocumentBag`) por cada documento
    tributario que el sobre contiene — uno solo si se armó con
    `create()`, uno o más si se armó con `createMany()` o si se cargó
    con `loadXml()` un sobre que agrupaba varios documentos. `caratula`
    es el `dict` con los datos de la carátula del sobre (`RutEmisor`,
    `RutEnvia`, `RutReceptor`, `FchResol`, `NroResol`, `TmstFirmaEnv`,
    `SubTotDTE`).
    """

    tag: str
    xml_base64: str
    documents: tuple[DocumentBag, ...]
    caratula: dict[str, Any] | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentEnvelope:
        """Construye un `DocumentEnvelope` desde el `data` de la API."""
        return cls(
            tag=data['tag'],
            xml_base64=data['xml'],
            documents=tuple(
                DocumentBag.from_api(item)
                for item in data.get('documents') or []
            ),
            caratula=data.get('caratula'),
        )


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

    `example` se pasa directamente al parámetro `input_data` de
    `DocumentBuilderService.build_draft()`/`.build_signed()` — mismo
    `Encabezado`/`Detalle` que usa el resto del SDK, sin transformación.
    `expected` son los valores esperados del caso (totales, etc.) que usa
    la suite de tests de `libredte-lib-core` para validarlo — información
    de referencia, no un dato del documento en sí.
    """

    id: str
    example: dict[str, Any]
    expected: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> Example:
        """Construye un `Example` desde el `data` que devuelve la API."""
        return cls(
            id=data['id'],
            example=data['example'],
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
