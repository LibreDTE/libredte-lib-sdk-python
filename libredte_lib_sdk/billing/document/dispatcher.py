# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Servicio para `billing.document.dispatcher`."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

from ...client import ApiClient
from .models import DocumentBag, DocumentEnvelope


class DocumentDispatcherService:
    """Arma y valida el sobre `EnvioDTE` (`billing.document.dispatcher`)."""

    _CREATE_OPERATION = 'billing.document.dispatcher::create'
    _CREATE_MANY_OPERATION = 'billing.document.dispatcher::createMany'
    _LOAD_XML_OPERATION = 'billing.document.dispatcher::loadXml'
    _VALIDATE_OPERATION = 'billing.document.dispatcher::validate'
    _VALIDATE_SCHEMA_OPERATION = 'billing.document.dispatcher::validateSchema'
    _VALIDATE_SIGNATURE_OPERATION = (
        'billing.document.dispatcher::validateSignature'
    )

    def __init__(self, client: ApiClient) -> None:
        """Guarda el `ApiClient` compartido usado para llamar a la API."""
        self._client = client

    def create(self, bag: DocumentBag) -> DocumentEnvelope:
        """
        Envuelve y firma un documento ya timbrado en un sobre `EnvioDTE`.

        `bag` es el `DocumentBag` ya timbrado y firmado que devuelve
        `DocumentBuilderService.build_signed()` — trae `certificate`/
        `emisor` incluidos, no hace falta pasarlos aparte. El sobre
        resultante es lo que se envía al SII (`SiiDteService.send`).
        """
        data = self._client.call(
            self._CREATE_OPERATION,
            bag=self._bag_payload(bag),
        )
        return DocumentEnvelope.from_api(data)

    def create_many(self, bags: Sequence[DocumentBag]) -> DocumentEnvelope:
        """
        Envuelve y firma 2+ documentos ya timbrados en un sobre `EnvioDTE`.

        Igual que `create()`, pero para un sobre que agrupa más de un
        documento — cada `DocumentBag` trae su propio `certificate`/
        `emisor`. El sobre resultante queda firmado con el certificado
        del PRIMER `DocumentBag` (el sobre en sí también se firma, no
        solo cada documento).
        """
        data = self._client.call(
            self._CREATE_MANY_OPERATION,
            bags=[self._bag_payload(bag) for bag in bags],
        )
        return DocumentEnvelope.from_api(data)

    @staticmethod
    def _bag_payload(bag: DocumentBag) -> dict[str, Any]:
        if bag.certificate is None:
            raise ValueError(
                'Este DocumentBag no tiene certificado — ¿se firmó con '
                '`builder.build_signed()`?',
            )
        if bag.emisor is None:
            raise ValueError(
                'Este DocumentBag no tiene emisor — ¿se construyó con '
                '`builder.build_draft/build_signed()` o se cargó con '
                '`loader.load_xml()`?',
            )
        return {
            'xmlDocument': bag.xml_base64,
            'certificate': bag.certificate.to_payload(),
            'emisor': bag.emisor,
        }

    def load_xml(self, xml_base64: str) -> DocumentEnvelope:
        """
        Carga un sobre `EnvioDTE` ya existente desde su XML (base64).

        El `DocumentEnvelope` resultante trae en `documents` una bolsa
        por cada documento tributario que el sobre agrupaba — uno o
        más — y en `caratula` los datos de la carátula ya presente en
        ese XML.
        """
        data = self._client.call(self._LOAD_XML_OPERATION, xml=xml_base64)
        return DocumentEnvelope.from_api(data)

    def validate(self, source: str) -> dict[str, Any]:
        """
        Valida un sobre `EnvioDTE` ya construido (`source`, XML en base64).

        Devuelve el XML del sobre, como `dict` (representación parseada,
        ej. `EnvioDTE.SetDTE.Caratula...`).
        """
        return cast(
            'dict[str, Any]',
            self._client.call(self._VALIDATE_OPERATION, source=source),
        )

    def validate_schema(self, source: str) -> dict[str, Any]:
        """Valida `source` contra el esquema XSD del sobre `EnvioDTE`."""
        return cast(
            'dict[str, Any]',
            self._client.call(
                self._VALIDATE_SCHEMA_OPERATION,
                source=source,
            ),
        )

    def validate_signature(self, source: str) -> list[dict[str, Any]]:
        """
        Valida cada firma electrónica encontrada en el sobre.

        Un sobre trae más de una firma (la del DTE y la del propio
        `EnvioDTE`) — devuelve una lista, un ítem por firma. Cada ítem
        es un `dict` vacío en caso de éxito.
        """
        return cast(
            'list[dict[str, Any]]',
            self._client.call(
                self._VALIDATE_SIGNATURE_OPERATION,
                source=source,
            ),
        )
