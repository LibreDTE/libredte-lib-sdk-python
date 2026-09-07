# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Test en vivo para `LibreDteOperationNotFoundError`.

Corre contra el ambiente por defecto (Lib Core, ver `real_sdk` en
`conftest.py`) a propósito: `human_resources.*` no existe ahí — es
justo el caso real que motivó la excepción, y no necesita apuntar a
Lib Pro para confirmarlo.
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk.exceptions import LibreDteOperationNotFoundError

pytestmark = pytest.mark.live


def test_human_resources_operation_raises_operation_not_found_on_core(
    real_sdk,
):
    with pytest.raises(LibreDteOperationNotFoundError) as exc_info:
        real_sdk.human_resources.integration.previred_provider.get_indicadores(
            202412,
        )

    error = exc_info.value
    assert error.status_code == 500
    assert error.operation_id == (
        'human_resources.integration.previred_provider::getIndicadores'
    )
