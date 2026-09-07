# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Cliente HTTP delgado para la API de LibreDTE Lib (`core.libredte.cl`)."""

from __future__ import annotations

import os
from typing import Any, Self

import httpx

from .exceptions import (
    LibreDteApiError,
    LibreDteConnectionError,
    LibreDteOperationNotFoundError,
    LibreDteRateLimitError,
)

DEFAULT_BASE_URL = 'https://core.libredte.cl/api'
DEFAULT_TIMEOUT = 30.0
_HTTP_TOO_MANY_REQUESTS = 429
_OPERATION_NOT_FOUND_PHP_CLASS = (
    'Derafu\\BackboneDispatcher\\Exception\\OperationNotFoundException'
)


class ApiClient:
    """
    Despacha operaciones contra la API de LibreDTE Lib.

    Traduce un `operation_id` con el formato
    `paquete.componente.worker::operacion` (el mismo que usa
    `libredte-lib-core-dispatcher`) a la ruta HTTP equivalente:
    `POST /{paquete}/{componente}/{worker}/{operacion}`.

    No sabe nada de DTE ni de reglas de negocio: solo hace la llamada
    HTTP y normaliza la respuesta (el `data` del sobre JSON en éxito,
    los bytes crudos si la respuesta no es JSON, o una excepción tipada
    si la API respondió un error). La orquestación vive en
    `billing/*/*.py`.

    Por defecto apunta a `core.libredte.cl`. Es configurable (`base_url`
    o la variable de entorno `LIBREDTE_LIB_SDK_BASE_URL`) para apuntar a
    `pro.libredte.cl` u otro ambiente.
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        api_token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Configura la URL base, autenticación opcional y cliente HTTP."""
        self._base_url = (
            base_url
            or os.environ.get('LIBREDTE_LIB_SDK_BASE_URL')
            or DEFAULT_BASE_URL
        ).rstrip('/')
        self._api_token = api_token or os.environ.get(
            'LIBREDTE_LIB_SDK_TOKEN',
        )
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None

    def close(self) -> None:
        """Cierra la conexión HTTP, si este cliente es dueño de ella."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Self:
        """Permite usar `ApiClient` como context manager."""
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Cierra la conexión HTTP al salir del context manager."""
        self.close()

    def call(self, operation_id: str, **parameters: Any) -> Any:
        """
        Ejecuta `operation_id` con `parameters` y devuelve su resultado.

        `parameters` se manda tal cual como el objeto `parameters` del
        body JSON que espera la API (ej. `bag=...`, `request=...`).
        """
        url = f'{self._base_url}/{self._operation_path(operation_id)}'

        try:
            response = self._client.post(
                url,
                json={'parameters': parameters},
                headers=self._headers(),
            )
        except httpx.RequestError as error:
            raise LibreDteConnectionError(
                f'No fue posible conectar con la API de LibreDTE Lib '
                f'({operation_id}): {error}',
            ) from error

        self._raise_for_rate_limit(operation_id, response)
        return self._parse_response(operation_id, response)

    def _headers(self) -> dict[str, str]:
        headers = {'Accept': 'application/json'}
        if self._api_token:
            headers['Authorization'] = f'Bearer {self._api_token}'
        return headers

    @staticmethod
    def _operation_path(operation_id: str) -> str:
        try:
            namespace, operation = operation_id.split('::', 1)
            package, component, worker = namespace.split('.', 2)
        except ValueError as error:
            raise ValueError(
                f'operation_id invalido: {operation_id!r}. Formato '
                "esperado: 'paquete.componente.worker::operacion'.",
            ) from error
        return f'{package}/{component}/{worker}/{operation}'

    @staticmethod
    def _raise_for_rate_limit(
        operation_id: str,
        response: httpx.Response,
    ) -> None:
        """
        Levanta `LibreDteRateLimitError` si la API frenó la solicitud.

        La API expone `X-RateLimit-Limit`/`X-RateLimit-Remaining` en
        toda respuesta. Se confía solo en el status code (`429`) más los
        headers estándar de HTTP (`Retry-After`, `X-RateLimit-*`), no en
        un shape de body particular.
        """
        if response.status_code != _HTTP_TOO_MANY_REQUESTS:
            return

        def _int_header(name: str) -> int | None:
            value = response.headers.get(name)
            return int(value) if value and value.isdigit() else None

        def _retry_after() -> float | None:
            value = response.headers.get('retry-after')
            if value is None:
                return None
            try:
                return float(value)
            except ValueError:
                return None

        detail = response.text
        try:
            body = response.json()
        except ValueError:
            body = {}
        if isinstance(body, dict) and body.get('detail'):
            detail = body['detail']

        raise LibreDteRateLimitError(
            operation_id=operation_id,
            detail=detail,
            retry_after=_retry_after(),
            limit=_int_header('x-ratelimit-limit'),
            remaining=_int_header('x-ratelimit-remaining'),
        )

    @staticmethod
    def _parse_response(operation_id: str, response: httpx.Response) -> Any:
        content_type = response.headers.get('content-type', '')

        if 'application/json' not in content_type:
            if response.is_error:
                raise LibreDteApiError(
                    operation_id=operation_id,
                    status_code=response.status_code,
                    title='Respuesta de error inesperada (no-JSON).',
                    detail=response.text,
                )
            return response.content

        body = response.json()

        if response.is_success and isinstance(body, dict) and 'data' in body:
            return body['data']

        error_body = body if isinstance(body, dict) else {}
        error_cls = ApiClient._error_class_for(error_body)
        raise error_cls.from_problem_details(
            operation_id=operation_id,
            status_code=response.status_code,
            body=error_body,
        )

    @staticmethod
    def _error_class_for(body: dict[str, Any]) -> type[LibreDteApiError]:
        """
        Elige la subclase de `LibreDteApiError` según `php_class`.

        Devuelve `LibreDteOperationNotFoundError` cuando `php_class` es
        `OperationNotFoundException`; en cualquier otro caso devuelve
        `LibreDteApiError`.
        """
        extensions = body.get('extensions')
        throwable = (
            extensions.get('throwable')
            if isinstance(extensions, dict)
            else None
        )
        php_class = (
            throwable.get('class') if isinstance(throwable, dict) else None
        )

        if php_class == _OPERATION_NOT_FOUND_PHP_CLASS:
            return LibreDteOperationNotFoundError

        return LibreDteApiError
