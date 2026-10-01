# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Test en vivo para `LibreDteOperationNotFoundError`.

Llama una operación que no existe en ningún ambiente, así que corre igual
contra Lib Core que contra Lib Pro.
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk.exceptions import LibreDteOperationNotFoundError

pytestmark = pytest.mark.live


def test_unknown_operation_raises_operation_not_found(real_sdk):
    with pytest.raises(LibreDteOperationNotFoundError) as exc_info:
        real_sdk._client.call('billing.document.parser::noExiste')

    error = exc_info.value
    assert error.status_code == 500
    assert error.operation_id == 'billing.document.parser::noExiste'
