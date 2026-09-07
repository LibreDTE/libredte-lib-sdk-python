# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests en vivo para `DocumentRendererService.render()`.

La API envuelve todo render (texto o binario) en el sobre JSON habitual,
como `data.renderings`: una lista de `{content, mimeType, filename,
label, copies, copyNumber}` con `content` en base64. Sin la opción
`renderings`, genera una única copia `'tributaria'` (default); pasando
`renderings={'tributaria': 2, 'cedible': 1}` (o similar) pide varias
presentaciones y/o copias en una sola llamada.

Reglas de negocio que estos tests verifican:

- Una presentación que no existe (ej. `'noexiste'`) → 500
  (`RendererException`).
- Una presentación que la API no puede generar para ese tipo de
  documento (ej. `'cedible'` en una boleta, que no admite acuse de
  recibo) se **omite en silencio** si se pidió junto con otras que sí
  se pudieron generar — no es un error.
- Si **ninguna** de las presentaciones pedidas se pudo generar (ej.
  pedir *solo* `'cedible'` para una boleta) → 500 (`RendererException`,
  mensaje distinto al de presentación inexistente).

Corre contra la API real (sin mocks) — requiere una API que soporte
`renderings`. Por defecto usa `LIBREDTE_LIB_SDK_BASE_URL`/el default de
`LibreDTE` (ver `README.rst`); para apuntar a otro ambiente:

    make install-dev
    LIBREDTE_LIB_SDK_BASE_URL=https://tu-ambiente/api .venv/bin/pytest \\
        -m live -v tests/integration/test_document_rendering.py
"""

from __future__ import annotations

import pytest

from libredte_lib_sdk.exceptions import LibreDteApiError

pytestmark = pytest.mark.live


def test_html_format_works(draft_document, real_sdk):
    result = real_sdk.billing.document.renderer.render(
        draft_document.xml_base64,
        format='html',
    )

    rendering = result.first
    assert rendering.mime_type == 'text/html'
    assert rendering.label == 'tributaria'
    assert rendering.content_bytes.startswith(b'<html')


def test_pdf_format_works(draft_document, real_sdk):
    result = real_sdk.billing.document.renderer.render(
        draft_document.xml_base64,
        format='pdf',
    )

    rendering = result.first
    assert rendering.mime_type == 'application/pdf'
    assert rendering.filename.endswith('.pdf')
    assert rendering.content_bytes.startswith(b'%PDF-')


def test_default_render_is_a_single_tributaria_copy(draft_document, real_sdk):
    """Sin `renderings`, la API genera una única copia `'tributaria'`."""
    result = real_sdk.billing.document.renderer.render(
        draft_document.xml_base64,
        format='pdf',
    )

    assert len(result.renderings) == 1
    assert result.first.label == 'tributaria'
    assert result.first.copies == 1
    assert result.first.copy_number == 1


def test_multiple_presentations_in_one_call(draft_document, real_sdk):
    """`renderings={'tributaria': 1, 'cedible': 1}` trae ambas."""
    result = real_sdk.billing.document.renderer.render(
        draft_document.xml_base64,
        format='pdf',
        renderings={'tributaria': 1, 'cedible': 1},
    )

    assert {r.label for r in result.renderings} == {'tributaria', 'cedible'}
    for rendering in result.renderings:
        assert rendering.content_bytes.startswith(b'%PDF-')


def test_multiple_copies_of_the_same_presentation(draft_document, real_sdk):
    """`renderings={'tributaria': 2}` trae 2 copias, numeradas 1 y 2."""
    result = real_sdk.billing.document.renderer.render(
        draft_document.xml_base64,
        format='pdf',
        renderings={'tributaria': 2},
    )

    tributarias = result.by_label('tributaria')
    assert len(tributarias) == 2
    assert [r.copy_number for r in tributarias] == [1, 2]
    assert all(r.copies == 2 for r in tributarias)


def test_unsupported_presentation_is_silently_omitted(draft_boleta, real_sdk):
    """
    `'cedible'` en una boleta (no admite acuse de recibo) se omite en
    silencio si se pidió junto a `'tributaria'` — no rompe la llamada.
    """
    result = real_sdk.billing.document.renderer.render(
        draft_boleta.xml_base64,
        format='pdf',
        renderings={'tributaria': 1, 'cedible': 1},
    )

    assert {r.label for r in result.renderings} == {'tributaria'}


def test_unknown_presentation_raises_a_clear_api_error(
    draft_document, real_sdk
):
    with pytest.raises(LibreDteApiError) as exc_info:
        real_sdk.billing.document.renderer.render(
            draft_document.xml_base64,
            format='pdf',
            renderings={'noexiste': 1},
        )

    assert 'no existe' in exc_info.value.detail


def test_no_generatable_presentation_raises_a_clear_api_error(
    draft_boleta,
    real_sdk,
):
    """
    Pedir *solo* `'cedible'` para una boleta no la omite en silencio
    (a diferencia del caso combinado con `'tributaria'`): no queda
    ninguna presentación generable, y la API lo rechaza.
    """
    with pytest.raises(LibreDteApiError) as exc_info:
        real_sdk.billing.document.renderer.render(
            draft_boleta.xml_base64,
            format='pdf',
            renderings={'cedible': 1},
        )

    assert 'ninguna' in exc_info.value.detail.lower()
