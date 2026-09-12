# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.integration`."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class SendXmlDocumentResponse:
    """Resultado del envío de un DTE al SII (`sendXmlDocument`)."""

    track_id: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SendXmlDocumentResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            track_id=data.get('track_id'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class SendAecResponse:
    """Resultado del envío de un AEC al SII (`sii_rtc::sendAec`)."""

    track_id: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SendAecResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            track_id=data.get('track_id'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class CheckXmlDocumentSentStatusResponse:
    """
    Estado de revisión de un envío al SII (`checkXmlDocumentSentStatus`).

    La respuesta trae `track_id`, `status` (código crudo del SII, ej.
    `'EPR'`), `error` (bool), `description` (glosa), `resume`
    (`reported`/`accepted`/`rejected`/`repairs`) y `documents` — las dos
    últimas, y `track_id`, solo disponibles vía `.raw` si se necesitan
    sin tipar.
    """

    status: str | None
    error: bool | None
    description: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> CheckXmlDocumentSentStatusResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            status=data.get('status'),
            error=data.get('error'),
            description=data.get('description'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class ValidateDocumentResponse:
    """Resultado de confirmar un documento en el SII (`validateDocument`)."""

    received: bool | None
    status: str | None
    description: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> ValidateDocumentResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            received=data.get('received'),
            status=data.get('status'),
            description=data.get('description'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class ValidateDocumentSignatureResponse:
    """
    Confirma un documento y su firma en el SII.

    Operación `validateDocumentSignature`.
    """

    received: bool | None
    status: str | None
    description: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> ValidateDocumentSignatureResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            received=data.get('received'),
            status=data.get('status'),
            description=data.get('description'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class RequestXmlDocumentSentStatusByEmailResponse:
    """
    Confirmación de la solicitud de estado por correo.

    `requestXmlDocumentSentStatusByEmail` no trae `received`.
    """

    status: str | None
    description: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> RequestXmlDocumentSentStatusByEmailResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            status=data.get('status'),
            description=data.get('description'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class CheckDocumentAssignabilityResponse:
    """Resultado `{codigo, glosa}` de `checkDocumentAssignability`."""

    codigo: str | None
    glosa: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> CheckDocumentAssignabilityResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            codigo=data.get('codigo'),
            glosa=data.get('glosa'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class SubmitDocumentAcceptanceResponse:
    """Resultado `{codigo, glosa}` de `submitDocumentAcceptance`."""

    codigo: str | None
    glosa: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> SubmitDocumentAcceptanceResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            codigo=data.get('codigo'),
            glosa=data.get('glosa'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class GetDocumentSiiReceptionDateResponse:
    """
    Fecha de recepción de un DTE en el SII (`getDocumentSiiReceptionDate`).

    Si el documento consultado no tiene fecha de recepción registrada,
    la API levanta `LibreDteApiError` — `fecha_recepcion_sii` nunca es
    `None`.
    """

    fecha_recepcion_sii: datetime
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> GetDocumentSiiReceptionDateResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            fecha_recepcion_sii=datetime.fromisoformat(
                data['fecha_recepcion_sii'],
            ),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class DocumentEvent:
    """Un evento del historial de un DTE en el RCV del SII."""

    codigo: str
    glosa: str
    responsable: str
    fecha: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> DocumentEvent:
        """Construye un `DocumentEvent` desde el `data` que devuelve la API."""
        return cls(
            codigo=data['codigo'],
            glosa=data['glosa'],
            responsable=data['responsable'],
            fecha=data['fecha'],
        )


@dataclass(frozen=True, slots=True)
class ListDocumentEventsResponse:
    """
    Historial de eventos de un DTE en el RCV del SII (`listDocumentEvents`).

    La API devuelve la lista de eventos directamente, sin envoltorio.
    """

    events: list[DocumentEvent]

    @classmethod
    def from_api(
        cls,
        data: list[dict[str, Any]],
    ) -> ListDocumentEventsResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(events=[DocumentEvent.from_api(item) for item in data])
