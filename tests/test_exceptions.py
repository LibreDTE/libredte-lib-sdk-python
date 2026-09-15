# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests para `libredte_lib_sdk.exceptions`."""

from __future__ import annotations

from libredte_lib_sdk.exceptions import LibreDteApiError


def test_full_message_combines_title_and_detail():
    error = LibreDteApiError(
        operation_id='billing.document.builder::build',
        status_code=500,
        title='Internal Server Error',
        detail='The package billing.document.builder::build does not exist.',
    )

    assert error.full_message == (
        'Internal Server Error: The package billing.document.builder'
        '::build does not exist.'
    )


def test_full_message_skips_detail_when_empty():
    error = LibreDteApiError(
        operation_id='billing.document.builder::build',
        status_code=500,
        title='Error desconocido de la API.',
    )

    assert error.full_message == 'Error desconocido de la API.'


def test_full_message_skips_detail_when_it_repeats_the_title():
    error = LibreDteApiError(
        operation_id='billing.document.builder::build',
        status_code=500,
        title='Mismo texto.',
        detail='Mismo texto.',
    )

    assert error.full_message == 'Mismo texto.'


def test_full_message_appends_file_and_line_when_the_api_reports_them():
    """
    Caso real: `ParserWorker::parse()` envuelve cualquier excepción en
    una `ParserException` — la API informa `title` como la clase PHP
    completa, `detail` como el mensaje real, y `extensions.throwable`
    con dónde se lanzó.
    """
    error = LibreDteApiError(
        operation_id='billing.document.builder::build',
        status_code=500,
        title=(
            'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
            '\\Exception\\ParserException'
        ),
        detail=(
            'round(): Argument #1 ($num) must be of type int|float, '
            'string given'
        ),
        extensions={
            'throwable': {
                'class': (
                    'libredte\\lib\\Core\\Package\\Billing\\Component'
                    '\\Document\\Exception\\ParserException'
                ),
                'file': (
                    'project_dir:vendor/libredte/libredte-lib-core/src/'
                    'Package/Billing/Component/Document/Worker/'
                    'ParserWorker.php'
                ),
                'line': 75,
            },
        },
    )

    assert error.full_message == (
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Exception\\ParserException: round(): Argument #1 ($num) '
        'must be of type int|float, string given (project_dir:vendor/'
        'libredte/libredte-lib-core/src/Package/Billing/Component/'
        'Document/Worker/ParserWorker.php:75)'
    )


def test_full_message_omits_location_when_file_or_line_is_missing():
    error = LibreDteApiError(
        operation_id='billing.document.builder::build',
        status_code=500,
        title='Internal Server Error',
        detail='Algo falló.',
        extensions={'throwable': {'class': 'SomeException'}},
    )

    assert error.full_message == 'Internal Server Error: Algo falló.'
