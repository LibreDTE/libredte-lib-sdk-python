# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""DTO del componente `billing.integration`."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ...response_registry import api_response


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiDte\\SendXmlDocumentResponse',
)
@dataclass(frozen=True, slots=True)
class SendXmlDocumentResponse:
    """Resultado del envío de un DTE al SII (`send_xml_document`)."""

    track_id: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SendXmlDocumentResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            track_id=data.get('track_id'),
            raw=data,
        )


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiRtc\\SendAecResponse',
)
@dataclass(frozen=True, slots=True)
class SendAecResponse:
    """Resultado del envío de un AEC al SII (`sii_rtc::send_aec`)."""

    track_id: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SendAecResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            track_id=data.get('track_id'),
            raw=data,
        )


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiDte\\CheckXmlDocumentSentStatusResponse',
)
@dataclass(frozen=True, slots=True)
class CheckXmlDocumentSentStatusResponse:
    """
    Estado de revisión de un envío al SII (`check_xml_document_sent_status`).

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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiDte\\ValidateDocumentResponse',
)
@dataclass(frozen=True, slots=True)
class ValidateDocumentResponse:
    """Resultado de confirmar un documento en el SII (`validate_document`)."""

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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiDte\\ValidateDocumentSignatureResponse',
)
@dataclass(frozen=True, slots=True)
class ValidateDocumentSignatureResponse:
    """
    Confirma un documento y su firma en el SII.

    Operación `validate_document_signature`.
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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiDte\\RequestXmlDocumentSentStatusByEmailResponse',
)
@dataclass(frozen=True, slots=True)
class RequestXmlDocumentSentStatusByEmailResponse:
    """
    Confirmación de la solicitud de estado por correo.

    `request_xml_document_sent_status_by_email` no trae `received`.
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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiRcv\\CheckDocumentAssignabilityResponse',
)
@dataclass(frozen=True, slots=True)
class CheckDocumentAssignabilityResponse:
    """Resultado `{codigo, glosa}` de `check_document_assignability`."""

    codigo: int | None
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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiRcv\\SubmitDocumentAcceptanceResponse',
)
@dataclass(frozen=True, slots=True)
class SubmitDocumentAcceptanceResponse:
    """Resultado `{codigo, glosa}` de `submit_document_acceptance`."""

    codigo: int | None
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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiRcv\\GetDocumentSiiReceptionDateResponse',
)
@dataclass(frozen=True, slots=True)
class GetDocumentSiiReceptionDateResponse:
    """
    Fecha de recepción de un DTE en el SII (`get_document_sii_reception_date`).

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


@api_response(
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\Support\\Response\\SiiRcv\\ListDocumentEventsResponse',
)
@dataclass(frozen=True, slots=True)
class ListDocumentEventsResponse:
    """
    Historial de eventos de un DTE en el RCV del SII (`list_document_events`).

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


_PHP_RTC = (
    'libredte\\lib\\Core\\Package\\Billing\\Component\\Integration\\'
    'Support\\Response\\SiiRtc'
)
_PHP_BOLETA = (
    'libredte\\lib\\Pro\\Package\\Billing\\Component\\Integration\\'
    'Support\\Response\\SiiBoleta'
)


@api_response(f'{_PHP_RTC}\\CheckAecSentStatusResponse')
@dataclass(frozen=True, slots=True)
class CheckAecSentStatusResponse:
    """
    Estado de un AEC enviado al SII (`sii_rtc.check_aec_sent_status`).

    `status` es el código del SII, `description` su explicación, `error`
    indica si es un error y `final` si es un estado final (si no lo es,
    se repite la consulta más adelante).
    """

    track_id: int | None
    status: str | None
    description: str | None
    error: bool | None
    final: bool | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> CheckAecSentStatusResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            track_id=data.get('track_id'),
            status=data.get('status'),
            description=data.get('description'),
            error=data.get('error'),
            final=data.get('final'),
            raw=data,
        )


@api_response(f'{_PHP_RTC}\\GetAssignmentStatusResponse')
@dataclass(frozen=True, slots=True)
class GetAssignmentStatusResponse:
    """
    Estado de la cesión de un documento en el SII.

    Respuesta de `sii_rtc.get_assignment_status` y de
    `sii_rtc.get_related_assignment_status`. `assigned` indica si el
    documento está cedido. `holder`, `last_annotation`, `collection_rut`,
    `collection_address` y `sworn_declaration` son `None` cuando el SII
    no los informa (siempre, sin la clave de acceso a la cesión).
    """

    assigned: bool | None
    status: str | None
    description: str | None
    holder: str | None
    last_annotation: str | None
    collection_rut: str | None
    collection_address: str | None
    sworn_declaration: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> GetAssignmentStatusResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            assigned=data.get('assigned'),
            status=data.get('status'),
            description=data.get('description'),
            holder=data.get('holder'),
            last_annotation=data.get('last_annotation'),
            collection_rut=data.get('collection_rut'),
            collection_address=data.get('collection_address'),
            sworn_declaration=data.get('sworn_declaration'),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class SiiBoletaRateLimit:
    """
    Límite de solicitudes de la API de boletas del SII.

    `limit` son las solicitudes permitidas por ventana, `remaining` las
    que quedan y `reset` los segundos hasta que la ventana se reinicia.
    """

    limit: int
    remaining: int
    reset: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiiBoletaRateLimit:
        """Construye desde el `rate_limit` que devuelve la API."""
        return cls(
            limit=data['limit'],
            remaining=data['remaining'],
            reset=data['reset'],
        )


def _rate_limit(data: dict[str, Any]) -> SiiBoletaRateLimit | None:
    rate_limit = data.get('rate_limit')

    return SiiBoletaRateLimit.from_api(rate_limit) if rate_limit else None


def _received_at(data: dict[str, Any]) -> datetime | None:
    received_at = data.get('received_at')

    return datetime.fromisoformat(received_at) if received_at else None


@dataclass(frozen=True, slots=True)
class SiiBoletaResume:
    """Cantidad de boletas de un envío: informadas, aceptadas, etc."""

    reported: int
    accepted: int
    rejected: int
    repairs: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiiBoletaResume:
        """Construye desde el `resume` que devuelve la API."""
        return cls(
            reported=data['reported'],
            accepted=data['accepted'],
            rejected=data['rejected'],
            repairs=data['repairs'],
        )


@dataclass(frozen=True, slots=True)
class SiiBoletaDocumentResume:
    """Cantidad de boletas de un envío para un tipo de boleta."""

    type: int
    reported: int
    accepted: int
    rejected: int
    repairs: int

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiiBoletaDocumentResume:
        """Construye desde un ítem de `documents` que devuelve la API."""
        return cls(
            type=data['type'],
            reported=data['reported'],
            accepted=data['accepted'],
            rejected=data['rejected'],
            repairs=data['repairs'],
        )


@dataclass(frozen=True, slots=True)
class SiiBoletaDocumentError:
    """Un error del SII en una boleta rechazada o con reparos."""

    section: str
    line: int | None
    level: int
    code: int
    description: str
    detail: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiiBoletaDocumentError:
        """Construye desde un ítem de `errors` que devuelve la API."""
        return cls(
            section=data['section'],
            line=data.get('line'),
            level=data['level'],
            code=data['code'],
            description=data['description'],
            detail=data.get('detail'),
        )


@dataclass(frozen=True, slots=True)
class SiiBoletaDocumentDetail:
    """
    Detalle de una boleta rechazada o con reparos en un envío.

    `type` y `folio` son `None` cuando el SII rechaza el envío completo
    (por ejemplo, un error en la carátula) y no una boleta en particular.
    """

    type: int | None
    folio: int | None
    status: str
    description: str
    errors: list[SiiBoletaDocumentError]

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> SiiBoletaDocumentDetail:
        """Construye desde un ítem de `details` que devuelve la API."""
        return cls(
            type=data.get('type'),
            folio=data.get('folio'),
            status=data['status'],
            description=data['description'],
            errors=[
                SiiBoletaDocumentError.from_api(item)
                for item in data.get('errors') or []
            ],
        )


@api_response(f'{_PHP_BOLETA}\\SendXmlDocumentResponse')
@dataclass(frozen=True, slots=True)
class SiiBoletaSendXmlDocumentResponse:
    """
    Resultado del envío de boletas al SII (`sii_boleta.send_xml_document`).

    `status` es el estado inicial del envío (`REC`: recibido). `received_at`,
    `rut_sender`, `rut_company`, `retry_after` (segundos sugeridos antes de
    consultar el estado), `location` y `rate_limit` son `None` cuando el SII
    no los informa.
    """

    track_id: int
    status: str
    received_at: datetime | None
    rut_sender: str | None
    rut_company: str | None
    retry_after: int | None
    location: str | None
    rate_limit: SiiBoletaRateLimit | None
    file: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls, data: dict[str, Any]
    ) -> SiiBoletaSendXmlDocumentResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            track_id=data['track_id'],
            status=data['status'],
            received_at=_received_at(data),
            rut_sender=data.get('rut_sender'),
            rut_company=data.get('rut_company'),
            retry_after=data.get('retry_after'),
            location=data.get('location'),
            rate_limit=_rate_limit(data),
            file=data.get('file'),
            raw=data,
        )


@api_response(f'{_PHP_BOLETA}\\CheckXmlDocumentSentStatusResponse')
@dataclass(frozen=True, slots=True)
class SiiBoletaCheckXmlDocumentSentStatusResponse:
    """
    Estado de un envío de boletas al SII.

    Respuesta de `sii_boleta.check_xml_document_sent_status`.

    `status` es el código del estado (`REC`, `SOK`, `EPR`, `RCT`, etc.),
    `description` su significado y `error` indica si es un rechazo. Un
    estado como `REC` o `SOK` no es el final: se repite la consulta.
    `resume` suma las boletas del envío y `documents` las entrega por tipo
    de boleta (vacío mientras el SII no informa cantidades). `details`
    trae el detalle de las boletas rechazadas o con reparos.
    """

    track_id: int
    company: str | None
    status: str
    error: bool
    description: str
    resume: SiiBoletaResume
    documents: dict[int, SiiBoletaDocumentResume]
    received_at: datetime | None
    sender: str | None
    retry_after: int | None
    location: str | None
    rate_limit: SiiBoletaRateLimit | None
    details: list[SiiBoletaDocumentDetail]
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        data: dict[str, Any],
    ) -> SiiBoletaCheckXmlDocumentSentStatusResponse:
        """Construye desde el `data` que devuelve la API."""
        # Sin boletas informadas la API entrega `[]` en vez de un mapa.
        documents = data.get('documents') or {}

        return cls(
            track_id=data['track_id'],
            company=data.get('company'),
            status=data['status'],
            error=data['error'],
            description=data['description'],
            resume=SiiBoletaResume.from_api(data['resume']),
            documents={
                int(type_): SiiBoletaDocumentResume.from_api(item)
                for type_, item in documents.items()
            },
            received_at=_received_at(data),
            sender=data.get('sender'),
            retry_after=data.get('retry_after'),
            location=data.get('location'),
            rate_limit=_rate_limit(data),
            details=[
                SiiBoletaDocumentDetail.from_api(item)
                for item in data.get('details') or []
            ],
            raw=data,
        )


@api_response(f'{_PHP_BOLETA}\\ValidateDocumentResponse')
@dataclass(frozen=True, slots=True)
class SiiBoletaValidateDocumentResponse:
    """
    Resultado de validar una boleta en el SII (`sii_boleta.validate_document`).

    `status` es el código del SII (`DOK`: recibida y con los datos
    coincidentes, `DNK`: recibida pero con datos distintos, `FAU`: no
    recibida) y `description` su significado.
    """

    status: str
    description: str | None
    rate_limit: SiiBoletaRateLimit | None
    raw: dict[str, Any]

    @classmethod
    def from_api(
        cls, data: dict[str, Any]
    ) -> SiiBoletaValidateDocumentResponse:
        """Construye desde el `data` que devuelve la API."""
        return cls(
            status=data['status'],
            description=data.get('description'),
            rate_limit=_rate_limit(data),
            raw=data,
        )
