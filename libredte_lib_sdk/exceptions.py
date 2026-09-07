# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Excepciones del SDK de LibreDTE Lib."""

from __future__ import annotations

from typing import Any


class LibreDteSdkError(Exception):
    """Cualquier error propio de `libredte_lib_sdk`."""


class LibreDteConnectionError(LibreDteSdkError):
    """No fue posible completar la conexión HTTP con la API."""


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


class LibreDteRateLimitError(LibreDteApiError):
    """
    La API rechazó la llamada por exceso de solicitudes (HTTP 429).

    `retry_after` trae el valor del header `Retry-After` en segundos
    (`None` si la API no lo informó). `limit`/`remaining` traen
    `X-RateLimit-Limit`/`X-RateLimit-Remaining` cuando la API los
    informa. No hay retry/backoff automático: quien llame decide si
    reintentar, y cuándo, con esta información.
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
        retry_after: float | None = None,
        limit: int | None = None,
        remaining: int | None = None,
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
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
