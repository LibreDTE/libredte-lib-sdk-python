# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Test en vivo para `LibreDteOperationNotFoundError`.

Pensado para Lib Core: `human_resources.*` no existe ahí — es justo el
caso real que motivó la excepción. Se salta a sí mismo si `real_sdk`
apunta a otro ambiente (ej. Lib Pro, vía `LIBREDTE_LIB_SDK_BASE_URL`),
donde `human_resources.*` sí existe y no aplica.
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk.client import DEFAULT_BASE_URL
from libredte_lib_sdk.exceptions import LibreDteOperationNotFoundError

pytestmark = pytest.mark.live


def test_human_resources_operation_raises_operation_not_found_on_core(
    real_sdk,
):
    if real_sdk.base_url != DEFAULT_BASE_URL:
        pytest.skip('human_resources.* no existe solo en Lib Core.')

    with pytest.raises(LibreDteOperationNotFoundError) as exc_info:
        real_sdk.human_resources.integration.previred_provider.get_indicadores(
            202412,
        )

    error = exc_info.value
    assert error.status_code == 500
    assert error.operation_id == (
        'human_resources.integration.previred_provider::getIndicadores'
    )
