# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Fixtures de pytest compartidas."""

from __future__ import annotations

import pytest

from libredte_lib_sdk import LibreDTE
from libredte_lib_sdk.client import ApiClient

TEST_BASE_URL = 'https://core.libredte.cl/api'


@pytest.fixture
def api_client():
    """`ApiClient` de prueba, contra la URL base real (mockeada con respx)."""
    client = ApiClient(TEST_BASE_URL)
    yield client
    client.close()


@pytest.fixture
def sdk():
    """`LibreDTE` de prueba, contra la URL base real (mockeada con respx)."""
    instance = LibreDTE(TEST_BASE_URL)
    yield instance
    instance.close()
