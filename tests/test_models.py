# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""Tests para los DTO de `libredte_lib_sdk.billing.*`."""

from __future__ import annotations

import base64

import pytest

from libredte_lib_sdk.billing.document.models import (
    DocumentBag,
    DocumentEnvelope,
    RenderResult,
)
from libredte_lib_sdk.billing.enums import SiiEnvironment
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


def test_document_bag_from_api_decodes_xml_and_exposes_timbrado_state():
    xml_base64 = base64.b64encode(b'<DTE/>').decode()
    bag = DocumentBag.from_api(
        {
            'document': {'Encabezado': {}},
            'document_type': {'codigo': 33},
            'document_stamp': None,
            'document_extra': None,
            'document_auth': None,
            'document_id': '76192083-9_T033F000000001',
            'document_xml': xml_base64,
        },
    )

    assert bag.xml_bytes == b'<DTE/>'
    assert bag.xml == '<DTE/>'
    assert bag.is_timbrado is False


def test_document_bag_is_timbrado_when_document_stamp_is_present():
    stamp_base64 = base64.b64encode(b'<TED><DD/></TED>').decode()
    bag = DocumentBag.from_api(
        {
            'document': {},
            'document_type': {'codigo': 33},
            'document_stamp': stamp_base64,
            'document_extra': None,
            'document_auth': None,
            'document_id': 'doc-1',
            'document_xml': base64.b64encode(b'<DTE/>').decode(),
        },
    )

    assert bag.is_timbrado is True
    assert bag.document_stamp_base64 == stamp_base64


def test_document_bag_xml_base64_raises_when_nothing_was_built():
    bag = DocumentBag.from_api(
        {
            'document': {},
            'document_type': {'codigo': 33},
            'document_stamp': None,
            'document_extra': None,
            'document_auth': None,
        },
    )

    assert bag.document_id is None
    with pytest.raises(ValueError, match='no tiene un documento construido'):
        _ = bag.xml_base64


def test_envelope_from_api_exposes_tag_and_decoded_xml():
    envelope = DocumentEnvelope.from_api(
        {'tag': 'EnvioDTE', 'xml': base64.b64encode(b'<EnvioDTE/>').decode()},
    )

    assert envelope.tag == 'EnvioDTE'
    assert envelope.xml == '<EnvioDTE/>'
    assert envelope.documents == ()
    assert envelope.caratula is None


def test_envelope_from_api_exposes_documents_and_caratula():
    caratula = {'RutEmisor': '76192083-9', 'NroResol': '0'}
    envelope = DocumentEnvelope.from_api(
        {
            'tag': 'EnvioDTE',
            'xml': base64.b64encode(b'<EnvioDTE/>').decode(),
            'documents': [
                {
                    'document': {'Encabezado': {}},
                    'document_type': {'codigo': 33},
                    'document_stamp': None,
                    'document_extra': None,
                    'document_auth': None,
                },
            ],
            'caratula': caratula,
        },
    )

    assert len(envelope.documents) == 1
    assert envelope.documents[0].document_type == {'codigo': 33}
    assert envelope.caratula == caratula


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
            'id': 'CAF33D1H100',
            'emisor': {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
            'tipoDocumento': 33,
            'folioDesde': 1,
            'folioHasta': 100,
            'cantidadFolios': 100,
            'fechaAutorizacion': '2026-01-01',
            'fechaVencimiento': '2026-06-30',
            'mesesAutorizacion': 2.17,
            'vigente': True,
            'vence': True,
            'idk': 300,
            'ambiente': 0,
            'certificacion': 0,
            'publicKey': '-----BEGIN PUBLIC KEY-----',
            'privateKey': '-----BEGIN PRIVATE KEY-----',
            'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
        },
    )

    assert caf.id == 'CAF33D1H100'
    assert caf.emisor == {'rut': '76192083-9', 'razon_social': 'SASCO SpA'}
    assert caf.tipo_documento == 33
    assert caf.folio_desde == 1
    assert caf.folio_hasta == 100
    assert caf.cantidad_folios == 100
    assert caf.fecha_autorizacion == '2026-01-01'
    assert caf.fecha_vencimiento == '2026-06-30'
    assert caf.meses_autorizacion == 2.17
    assert caf.vigente is True
    assert caf.vence is True
    assert caf.idk == 300
    assert caf.ambiente is SiiEnvironment.PRODUCTION
    assert caf.certificacion == 0
    assert caf.public_key == '-----BEGIN PUBLIC KEY-----'
    assert caf.private_key == '-----BEGIN PRIVATE KEY-----'
    assert caf.xml == '<AUTORIZACION/>'
    assert caf.raw['vigente'] is True


def test_caf_from_api_ambiente_is_none_for_a_fake_caf():
    """`CafFaker` emite IDK 666 — no corresponde a ningún ambiente real."""
    caf = Caf.from_api(
        {
            'id': 'CAF33D1H1',
            'emisor': {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
            'tipoDocumento': 33,
            'folioDesde': 1,
            'folioHasta': 1,
            'cantidadFolios': 1,
            'fechaAutorizacion': '2026-01-01',
            'fechaVencimiento': '2026-06-30',
            'mesesAutorizacion': 2.17,
            'vigente': True,
            'vence': True,
            'idk': 666,
            'ambiente': None,
            'certificacion': None,
            'publicKey': '-----BEGIN PUBLIC KEY-----',
            'privateKey': '-----BEGIN PRIVATE KEY-----',
            'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
        },
    )

    assert caf.ambiente is None
    assert caf.certificacion is None


def test_caf_from_api_ambiente_as_object_uses_its_value():
    """La API a veces serializa el enum de PHP como `{name, value}`."""
    caf = Caf.from_api(
        {
            'id': 'CAF33D1H100',
            'emisor': {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
            'tipoDocumento': 33,
            'folioDesde': 1,
            'folioHasta': 100,
            'cantidadFolios': 100,
            'fechaAutorizacion': '2026-01-01',
            'fechaVencimiento': '2026-06-30',
            'mesesAutorizacion': 2.17,
            'vigente': True,
            'vence': True,
            'idk': 100,
            'ambiente': {'name': 'STAGING', 'value': 1},
            'certificacion': 1,
            'publicKey': '-----BEGIN PUBLIC KEY-----',
            'privateKey': '-----BEGIN PRIVATE KEY-----',
            'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
        },
    )

    assert caf.ambiente is SiiEnvironment.CERTIFICATION


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
