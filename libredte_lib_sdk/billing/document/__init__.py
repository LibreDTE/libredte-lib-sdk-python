# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Componente `billing.document`: DTE — construcción, sobre y render."""

from __future__ import annotations

from ...client import ApiClient
from .builder import DocumentBuilderService
from .dispatcher import DocumentDispatcherService
from .examples import DocumentExamplesService
from .loader import DocumentLoaderService
from .models import (
    Document,
    DocumentBag,
    DocumentEnvelope,
    Example,
    ExampleSummary,
    RenderedDocument,
    RenderResult,
)
from .renderer import DocumentRendererService
from .validator import DocumentValidatorService

__all__ = [
    'Document',
    'DocumentBag',
    'DocumentBuilderService',
    'DocumentComponent',
    'DocumentDispatcherService',
    'DocumentEnvelope',
    'DocumentExamplesService',
    'DocumentLoaderService',
    'DocumentRendererService',
    'DocumentValidatorService',
    'Example',
    'ExampleSummary',
    'RenderResult',
    'RenderedDocument',
]


class DocumentComponent:
    """Agrupa los servicios de `billing.document`."""

    def __init__(self, client: ApiClient) -> None:
        """Crea los servicios del componente sobre el `ApiClient` dado."""
        self.builder = DocumentBuilderService(client)
        self.dispatcher = DocumentDispatcherService(client)
        self.renderer = DocumentRendererService(client)
        self.examples = DocumentExamplesService(client)
        self.validator = DocumentValidatorService(client)
        self.loader = DocumentLoaderService(client)
