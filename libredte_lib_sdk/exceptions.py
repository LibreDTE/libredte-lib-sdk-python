# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Excepciones del SDK de LibreDTE Lib."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class LibreDteSdkError(Exception):
    """Cualquier error propio de `libredte_lib_sdk`."""


class LibreDteConnectionError(LibreDteSdkError):
    """No fue posible completar la conexión HTTP con la API."""


class LibreDteUnmappedResponseError(LibreDteSdkError):
    """
    La clase de respuesta de la API no tiene DTO o no es la esperada.

    Ocurre si la API devolvió una clase sin DTO registrado, o distinta de la
    que esperaba el servicio. Una clase PHP nueva en la API obliga a crear
    su DTO y registrarlo con `response_registry.api_response()`.
    """


class LibreDteApiError(LibreDteSdkError):
    """
    La API de LibreDTE Lib respondió un error para una operación.

    Envuelve el `Problem Details` (RFC 7807) que la API entrega en sus
    respuestas de error: `type`/`title`/`detail`/`instance`/`extensions`.
    `php_class` expone la clase de la excepción PHP real (si la API la
    informó en `extensions.throwable.class`), útil para distinguir
    errores de negocio (ej. `DocumentException`) de errores de
    infraestructura sin tener que parsear `detail`.
    """

    def __init__(
        self,
        *,
        operation_id: str,
        status_code: int,
        title: str,
        detail: str = '',
        problem_type: str = 'about:blank',
        instance: str = '',
        extensions: dict[str, Any] | None = None,
    ) -> None:
        """Guarda el detalle del error tal como lo informó la API."""
        self.operation_id = operation_id
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.problem_type = problem_type
        self.instance = instance or operation_id
        self.extensions = extensions or {}
        message = f'[{operation_id}] {title}'
        if detail:
            message = f'{message}: {detail}'
        super().__init__(message)

    @property
    def php_class(self) -> str | None:
        """Clase PHP real detrás del error, si la API la informó."""
        throwable = self.extensions.get('throwable')
        if isinstance(throwable, dict):
            return throwable.get('class')
        return None

    @property
    def full_message(self) -> str:
        """
        `title` + `detail` + dónde ocurrió, listo para loguear o mostrar.

        Agrega el archivo y línea (`extensions.throwable.file`/`.line`)
        cuando la API los informó, sin necesidad de ir a inspeccionar
        `extensions` a mano cada vez. Si `detail` está vacío o repite
        `title`, no lo duplica; si no hay `file`/`line`, los omite.
        """
        message = self.title
        if self.detail and self.detail != self.title:
            message = f'{message}: {self.detail}'
        throwable = self.extensions.get('throwable')
        if isinstance(throwable, dict):
            file = throwable.get('file')
            line = throwable.get('line')
            if file and line:
                message = f'{message} ({file}:{line})'
        return message

    @classmethod
    def from_problem_details(
        cls,
        *,
        operation_id: str,
        status_code: int,
        body: dict[str, Any],
    ) -> LibreDteApiError:
        """Construye la excepción a partir de un body Problem Details."""
        return cls(
            operation_id=operation_id,
            status_code=status_code,
            title=body.get('title') or 'Error desconocido de la API.',
            detail=body.get('detail') or '',
            problem_type=body.get('type') or 'about:blank',
            instance=body.get('instance') or operation_id,
            extensions=body.get('extensions'),
        )


class LibreDteOperationNotFoundError(LibreDteApiError):
    r"""
    La operación llamada no existe en la instancia de la API consultada.

    Se distingue de un `LibreDteApiError` genérico (parámetros
    inválidos, error de negocio, etc.) para permitir detectar en un
    solo `except` que la operación no está registrada en el ambiente
    configurado, sin parsear `detail`. Se reconoce por `php_class`
    (`Derafu\BackboneDispatcher\Exception\OperationNotFoundException`),
    no por el status HTTP: la API la informa con `500`, igual que
    cualquier otro error de servidor.
    """


@dataclass(frozen=True, slots=True)
class RateLimit:
    """
    Cifras de uno de los límites de la API: el tope y lo que queda.

    Cada una es `None` cuando la API no la informó.
    """

    limit: int | None
    remaining: int | None


@dataclass(frozen=True, slots=True)
class RateLimitInfo:
    """
    Lo que la API informa de un rechazo por exceso de solicitudes.

    Cada dato es `None` cuando la API no lo informó.

    - `retry_after`: segundos que informa `Retry-After`.
    - `reset_at`: hora en que se libera el límite (`X-RateLimit-Reset`),
      en segundos desde el epoch.
    - `policy`: cuál límite se agotó (`X-RateLimit-Policy`, por ejemplo
      `ip`).
    - `quota`: cifras del cupo del usuario.
    - `ip`: cifras del límite por IP.
    """

    retry_after: float | None = None
    reset_at: float | None = None
    policy: str | None = None
    quota: RateLimit | None = None
    ip: RateLimit | None = None


class LibreDteRateLimitError(LibreDteApiError):
    """
    La API rechazó la llamada por exceso de solicitudes (HTTP 429).

    Todo dato es `None` cuando la API no lo informa:

    - `retry_after`: el valor de `Retry-After`, en segundos.
    - `reset_at`: la hora en que se libera el límite
      (`X-RateLimit-Reset`), en segundos desde el epoch.
    - `policy`: cuál límite se agotó (`X-RateLimit-Policy`, por ejemplo
      `ip`).
    - `limit`/`remaining`: el cupo del usuario
      (`X-RateLimit-Limit`/`X-RateLimit-Remaining`). Solo existe cuando
      la solicitud va autenticada, y un 429 por IP sale antes de llegar
      a él.
    - `ip_limit`/`ip_remaining`: el límite por IP
      (`X-RateLimit-IP-Limit`/`X-RateLimit-IP-Remaining`).

    No hay retry/backoff automático: quien llame decide si reintentar,
    y cuándo, con esta información.
    """

    def __init__(
        self,
        *,
        operation_id: str,
        status_code: int = 429,
        title: str = 'Límite de solicitudes excedido.',
        detail: str = '',
        problem_type: str = 'about:blank',
        instance: str = '',
        extensions: dict[str, Any] | None = None,
        rate_limit: RateLimitInfo | None = None,
    ) -> None:
        """Guarda el detalle del error de rate limit, con sus headers."""
        super().__init__(
            operation_id=operation_id,
            status_code=status_code,
            title=title,
            detail=detail,
            problem_type=problem_type,
            instance=instance,
            extensions=extensions,
        )
        self.rate_limit = rate_limit or RateLimitInfo()

    @property
    def retry_after(self) -> float | None:
        """Segundos que informa `Retry-After`."""
        return self.rate_limit.retry_after

    @property
    def reset_at(self) -> float | None:
        """Hora en que se libera el límite, en segundos desde el epoch."""
        return self.rate_limit.reset_at

    @property
    def policy(self) -> str | None:
        """Cuál límite se agotó (`X-RateLimit-Policy`)."""
        return self.rate_limit.policy

    @property
    def limit(self) -> int | None:
        """Tope del cupo del usuario (`X-RateLimit-Limit`)."""
        quota = self.rate_limit.quota
        return quota.limit if quota else None

    @property
    def remaining(self) -> int | None:
        """Lo que queda del cupo del usuario (`X-RateLimit-Remaining`)."""
        quota = self.rate_limit.quota
        return quota.remaining if quota else None

    @property
    def ip_limit(self) -> int | None:
        """Tope del límite por IP (`X-RateLimit-IP-Limit`)."""
        ip = self.rate_limit.ip
        return ip.limit if ip else None

    @property
    def ip_remaining(self) -> int | None:
        """Lo que queda del límite por IP (`X-RateLimit-IP-Remaining`)."""
        ip = self.rate_limit.ip
        return ip.remaining if ip else None
