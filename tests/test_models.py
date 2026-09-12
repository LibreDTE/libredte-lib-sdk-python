# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests para los DTO de `libredte_lib_sdk.billing.*`."""

from __future__ import annotations

import base64

from libredte_lib_sdk.billing.document.models import (
    Document,
    DocumentEnvelope,
    RenderResult,
)
from libredte_lib_sdk.billing.identifier.models import Caf
from libredte_lib_sdk.billing.integration.models import (
    CheckXmlDocumentSentStatusResponse,
    SendXmlDocumentResponse,
)
from libredte_lib_sdk.billing.trading_parties.models import (
    Certificate,
    Mandatario,
)


def test_certificate_to_payload_maps_certificate_and_private_key():
    certificate = Certificate(certificate='cert', private_key='key')

    assert certificate.to_payload() == {
        'certificate': 'cert',
        'privateKey': 'key',
    }


def test_certificate_from_api_maps_cert_and_pkey_fields():
    certificate = Certificate.from_api(
        {'cert': '-----BEGIN CERTIFICATE-----', 'pkey': '-----BEGIN KEY-----'},
    )

    assert certificate.certificate == '-----BEGIN CERTIFICATE-----'
    assert certificate.private_key == '-----BEGIN KEY-----'


def test_mandatario_to_payload_omits_email_when_absent():
    mandatario = Mandatario(run='76192083-9', nombre='SASCO SpA')

    assert mandatario.to_payload() == {
        'run': '76192083-9',
        'nombre': 'SASCO SpA',
    }


def test_mandatario_to_payload_includes_email_when_present():
    mandatario = Mandatario(
        run='76192083-9',
        nombre='SASCO SpA',
        email='sasco@example.com',
    )

    assert mandatario.to_payload() == {
        'run': '76192083-9',
        'nombre': 'SASCO SpA',
        'email': 'sasco@example.com',
    }


def test_document_from_api_decodes_xml_and_exposes_timbrado_state():
    xml_base64 = base64.b64encode(b'<DTE/>').decode()
    document = Document.from_api(
        {
            'id': '76192083-9_T033F000000001',
            'datos': {'Encabezado': {}},
            'ted': None,
            'xml': xml_base64,
        },
    )

    assert document.xml_bytes == b'<DTE/>'
    assert document.xml == '<DTE/>'
    assert document.is_timbrado is False


def test_document_is_timbrado_when_ted_is_present():
    document = Document.from_api(
        {
            'id': 'doc-1',
            'datos': {},
            'ted': {'DD': {}},
            'xml': base64.b64encode(b'<DTE/>').decode(),
        },
    )

    assert document.is_timbrado is True


def test_envelope_from_api_exposes_tag_and_decoded_xml():
    envelope = DocumentEnvelope.from_api(
        {'tag': 'EnvioDTE', 'xml': base64.b64encode(b'<EnvioDTE/>').decode()},
    )

    assert envelope.tag == 'EnvioDTE'
    assert envelope.xml == '<EnvioDTE/>'


def _rendering_payload(content: bytes, *, label, copies=1, copy_number=1):
    return {
        'content': base64.b64encode(content).decode(),
        'mimeType': 'application/pdf',
        'filename': f'documento_{label}.pdf',
        'label': label,
        'copies': copies,
        'copyNumber': copy_number,
    }


def test_render_result_from_api_decodes_each_rendering():
    result = RenderResult.from_api(
        {
            'renderings': [
                _rendering_payload(b'%PDF-1.4 tributaria', label='tributaria'),
                _rendering_payload(b'%PDF-1.4 cedible', label='cedible'),
            ],
        },
    )

    assert len(result.renderings) == 2
    assert result.first.label == 'tributaria'
    assert result.first.content_bytes == b'%PDF-1.4 tributaria'
    assert result.renderings[1].content_bytes == b'%PDF-1.4 cedible'


def test_render_result_by_label_filters_multiple_copies():
    result = RenderResult.from_api(
        {
            'renderings': [
                _rendering_payload(
                    b'copy 1',
                    label='tributaria',
                    copies=2,
                    copy_number=1,
                ),
                _rendering_payload(
                    b'copy 2',
                    label='tributaria',
                    copies=2,
                    copy_number=2,
                ),
                _rendering_payload(b'cedible', label='cedible'),
            ],
        },
    )

    tributarias = result.by_label('tributaria')
    assert len(tributarias) == 2
    assert [r.copy_number for r in tributarias] == [1, 2]
    assert tributarias[0].copies == 2
    assert result.by_label('cedible')[0].content_bytes == b'cedible'
    assert result.by_label('inexistente') == ()


def test_caf_from_api_exposes_the_common_fields():
    caf = Caf.from_api(
        {
            'tipoDocumento': 33,
            'folioDesde': 1,
            'folioHasta': 100,
            'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
            'vigente': True,
        },
    )

    assert caf.tipo_documento == 33
    assert caf.folio_desde == 1
    assert caf.folio_hasta == 100
    assert caf.xml == '<AUTORIZACION/>'
    assert caf.raw['vigente'] is True


def test_send_result_reads_track_id():
    assert SendXmlDocumentResponse.from_api({'track_id': 456}).track_id == 456
    assert SendXmlDocumentResponse.from_api({}).track_id is None


def test_sii_status_exposes_raw_and_typed_fields():
    status = CheckXmlDocumentSentStatusResponse.from_api(
        {
            'track_id': 12429807686,
            'status': 'EPR',
            'error': False,
            'description': 'Envio Procesado',
            'resume': {
                'reported': 1,
                'accepted': 1,
                'rejected': 0,
                'repairs': 0,
            },
            'documents': [],
        }
    )

    assert status.raw['track_id'] == 12429807686
    assert status.status == 'EPR'
    assert status.error is False
    assert status.description == 'Envio Procesado'
