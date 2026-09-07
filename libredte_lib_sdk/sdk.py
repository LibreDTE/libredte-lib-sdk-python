# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Punto de entrada único del SDK: `LibreDTE`."""

from __future__ import annotations

from typing import Self

import httpx

from .billing import BillingPackage
from .client import DEFAULT_TIMEOUT, ApiClient
from .human_resources import HumanResourcesPackage
from .system import SystemPackage


class LibreDTE:
    """
    Fachada del SDK: agrupa los paquetes de la API.

    `billing`/`system` funcionan contra cualquier instancia; `human_
    resources` solo existe en Lib Pro (ver `HumanResourcesPackage`).

    Uso típico (ver `README.rst` para el detalle de cada DTO):

    .. code-block:: python

        sdk = LibreDTE()
        doc, ident, tp, sii = (
            sdk.billing.document,
            sdk.billing.identifier,
            sdk.billing.trading_parties,
            sdk.billing.integration,
        )

        borrador = doc.builder.build_draft(input_data)

        caf = ident.caf_faker.create(emisor, codigo_documento=33)
        certificate = tp.mandatario_manager.create_fake_certificate(
            mandatario,
        )
        documento = doc.builder.build_signed(
            input_data, caf_xml=caf.xml_base64, certificate=certificate,
        )
        sobre = doc.dispatcher.create(
            documento.xml_base64, certificate=certificate, emisor=emisor_dto,
        )
        envio = sii.sii_dte.send(
            sobre.xml_base64, certificate=certificate, company_rut=rut,
        )
        estado = sii.sii_dte.check_status(
            envio.track_id, certificate=certificate, company_rut=rut,
        )

        pdf = doc.renderer.render(documento.xml_base64).first
        pdf_bytes = pdf.content_bytes
    """

    def __init__(
        self,
        base_url: str | None = None,
        *,
        api_token: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Crea el `ApiClient` compartido y los paquetes que lo usan."""
        self._client = ApiClient(
            base_url,
            api_token=api_token,
            timeout=timeout,
            http_client=http_client,
        )
        self.billing = BillingPackage(self._client)
        self.system = SystemPackage(self._client)
        self.human_resources = HumanResourcesPackage(self._client)

    def close(self) -> None:
        """Cierra la conexión HTTP subyacente."""
        self._client.close()

    def __enter__(self) -> Self:
        """Permite usar `LibreDTE` como context manager."""
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Cierra la conexión HTTP al salir del context manager."""
        self.close()
