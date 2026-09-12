# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests para los servicios de orquestación, uno por cada worker de la API
que el SDK cubre.

Las respuestas mockeadas siguen la forma real de la API (sobre `{meta,
data}`, nombres de campo en camelCase, XML en base64) — ver el spec
OpenAPI de LibreDTE Lib para el detalle completo de cada operación.
"""

from __future__ import annotations

import base64
import json

import httpx
import respx

from libredte_lib_sdk.billing.enums import SiiEnvironment
from libredte_lib_sdk.billing.trading_parties import Certificate, Mandatario

from .conftest import TEST_BASE_URL

_REAL_SIGNED_DOCUMENT_RESPONSE = {
    'meta': {
        'timestamp': 1787810337.756542,
        'data_type': (
            'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
            '\\Entity\\Document\\FacturaAfecta'
        ),
    },
    'data': {
        'id': '76192083-9_T033F000000001',
        'datos': {
            'Encabezado': {'IdDoc': {'TipoDTE': 33, 'Folio': 1}},
            'Detalle': [{'NroLinDet': 1, 'NmbItem': 'Producto A'}],
        },
        'ted': {'DD': {'RE': '76192083-9'}},
        'xml': base64.b64encode(b'<DTE><!-- timbrado --></DTE>').decode(),
    },
}

_INPUT_DATA = {
    'Encabezado': {
        'IdDoc': {'TipoDTE': 33, 'Folio': 1},
        'Emisor': {'RUTEmisor': '76192083-9', 'RznSoc': 'SASCO SpA'},
        'Receptor': {'RUTRecep': '12345678-5', 'RznSocRecep': 'Cliente'},
    },
    'Detalle': [{'NmbItem': 'Producto A', 'QtyItem': 1, 'PrcItem': 1000}],
}

_CERTIFICATE = Certificate(certificate='cert-pem', private_key='key-pem')


@respx.mock
def test_build_draft_omits_caf_and_certificate_from_the_payload(sdk):
    draft_response = {
        'meta': _REAL_SIGNED_DOCUMENT_RESPONSE['meta'],
        'data': {**_REAL_SIGNED_DOCUMENT_RESPONSE['data'], 'ted': None},
    }
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/builder/build',
    ).mock(return_value=httpx.Response(200, json=draft_response))

    document = sdk.billing.document.builder.build_draft(_INPUT_DATA)

    sent = json.loads(route.calls.last.request.content)
    assert sent['parameters']['bag'].keys() == {'inputData'}
    assert document.id == '76192083-9_T033F000000001'
    assert document.is_timbrado is False


@respx.mock
def test_build_draft_sends_options_when_given(sdk):
    draft_response = {
        'meta': _REAL_SIGNED_DOCUMENT_RESPONSE['meta'],
        'data': {**_REAL_SIGNED_DOCUMENT_RESPONSE['data'], 'ted': None},
    }
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/builder/build',
    ).mock(return_value=httpx.Response(200, json=draft_response))

    sdk.billing.document.builder.build_draft(
        '<DTE>...</DTE>',
        options={'parser': {'strategy': 'default.xml'}},
    )

    sent = json.loads(route.calls.last.request.content)
    bag = sent['parameters']['bag']
    assert bag['inputData'] == '<DTE>...</DTE>'
    assert bag['options'] == {'parser': {'strategy': 'default.xml'}}


@respx.mock
def test_build_signed_includes_caf_and_certificate(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/builder/build',
    ).mock(
        return_value=httpx.Response(200, json=_REAL_SIGNED_DOCUMENT_RESPONSE),
    )

    document = sdk.billing.document.builder.build_signed(
        _INPUT_DATA,
        caf_xml='<AUTORIZACION/>',
        certificate=_CERTIFICATE,
    )

    sent = json.loads(route.calls.last.request.content)
    bag = sent['parameters']['bag']
    assert bag['caf'] == '<AUTORIZACION/>'
    assert bag['certificate'] == {
        'certificate': 'cert-pem',
        'privateKey': 'key-pem',
    }
    assert document.is_timbrado is True


@respx.mock
def test_caf_faker_create_maps_parameters_and_response(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/identifier/caf_faker/create',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'tipoDocumento': 33,
                    'folioDesde': 1,
                    'folioHasta': 100,
                    'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
                },
            },
        ),
    )

    caf = sdk.billing.identifier.caf_faker.create(
        {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
        codigo_documento=33,
        folio_hasta=100,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['codigoDocumento'] == 33
    assert sent['folioDesde'] == 1
    assert sent['folioHasta'] == 100
    assert caf.folio_hasta == 100
    assert caf.xml == '<AUTORIZACION/>'


@respx.mock
def test_caf_loader_load_sends_xml_and_decodes_the_caf(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/identifier/caf_loader/load',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'tipoDocumento': 33,
                    'folioDesde': 1,
                    'folioHasta': 50,
                    'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
                },
            },
        ),
    )

    caf = sdk.billing.identifier.caf_loader.load('ZmFrZQ==')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['xml'] == 'ZmFrZQ=='
    assert caf.folio_desde == 1
    assert caf.folio_hasta == 50


@respx.mock
def test_caf_validator_validate_sends_caf_key_and_decodes_the_caf(sdk):
    """La API llama a este parámetro `caf`, aunque sea el mismo XML."""
    route = respx.post(
        f'{TEST_BASE_URL}/billing/identifier/caf_validator/validate',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'tipoDocumento': 33,
                    'folioDesde': 1,
                    'folioHasta': 50,
                    'xml': base64.b64encode(b'<AUTORIZACION/>').decode(),
                },
            },
        ),
    )

    caf = sdk.billing.identifier.caf_validator.validate('ZmFrZQ==')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['caf'] == 'ZmFrZQ=='
    assert caf.tipo_documento == 33


@respx.mock
def test_mandatario_manager_create_fake_certificate(sdk):
    """
    La API entrega el mismo shape completo que `system.certificate
    .loader::load` (confirmado en vivo) — `Certificate.from_api()` debe
    poblar todo, no solo `certificate`/`private_key`.
    """
    route = respx.post(
        f'{TEST_BASE_URL}/billing/trading_parties/mandatario_manager'
        '/createFakeCertificate',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'id': '76192083-9',
                    'name': 'SASCO SpA',
                    'email': 'sasco@example.com',
                    'from': '2026-09-05T12:00:00',
                    'to': '2027-09-05T12:00:00',
                    'totalDays': 365,
                    'expirationDays': 365,
                    'isActive': True,
                    'issuer': 'Derafu Test Certificate Authority',
                    'modulus': 'MODULUS',
                    'exponent': 'AQAB',
                    'cert': 'CERT-PEM',
                    'chain': [],
                    'pkey': 'PKEY-PEM',
                },
            },
        ),
    )

    service = sdk.billing.trading_parties.mandatario_manager
    certificate = service.create_fake_certificate(
        Mandatario(run='76192083-9', nombre='SASCO SpA'),
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['mandatario']['run'] == '76192083-9'
    assert certificate.certificate == 'CERT-PEM'
    assert certificate.private_key == 'PKEY-PEM'
    assert certificate.id == '76192083-9'
    assert certificate.name == 'SASCO SpA'
    assert certificate.email == 'sasco@example.com'
    assert certificate.is_active is True
    assert certificate.issuer == 'Derafu Test Certificate Authority'


@respx.mock
def test_envelope_create_sends_document_certificate_and_emisor(sdk):
    envelope_xml = base64.b64encode(b'<EnvioDTE/>').decode()
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/dispatcher/create',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'tag': 'EnvioDTE', 'xml': envelope_xml},
            },
        ),
    )
    emisor = {
        'rut': '76192083-9',
        'razon_social': 'SASCO SpA',
        'autorizacion_dte': {
            'fecha_resolucion': '2014-08-22',
            'numero_resolucion': 80,
        },
    }

    envelope = sdk.billing.document.dispatcher.create(
        'ZG9jdW1lbnRv',
        certificate=_CERTIFICATE,
        emisor=emisor,
    )

    sent = json.loads(route.calls.last.request.content)
    bag = sent['parameters']['bag']
    assert bag['xmlDocument'] == 'ZG9jdW1lbnRv'
    assert bag['emisor']['autorizacion_dte']['numero_resolucion'] == 80
    assert envelope.tag == 'EnvioDTE'
    assert envelope.xml == '<EnvioDTE/>'


@respx.mock
def test_sii_send_defaults_to_the_production_environment(sdk):
    """El default debe ser el mismo que el de la propia API (`PRODUCTION`)."""
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_dte/sendXmlDocument',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'track_id': 123}},
        ),
    )

    result = sdk.billing.integration.sii_dte.send(
        'ZW52ZWxvcGU=',
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['request']['options']['environment'] == 0
    assert sent['doc'] == 'ZW52ZWxvcGU='
    assert sent['company'] == '76192083-9'
    assert result.track_id == 123


@respx.mock
def test_sii_send_honors_an_explicit_production_environment(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_dte/sendXmlDocument',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'track_id': 1}},
        ),
    )

    sdk.billing.integration.sii_dte.send(
        'ZG9j',
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
        environment=SiiEnvironment.PRODUCTION,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['request']['options']['environment'] == 0


@respx.mock
def test_sii_check_status_sends_the_track_id_and_company(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_dte'
        '/checkXmlDocumentSentStatus',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'status': 'OK'}},
        ),
    )

    status = sdk.billing.integration.sii_dte.check_status(
        123,
        certificate=_CERTIFICATE,
        company_rut='76192083-9',
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['trackId'] == 123
    assert sent['company'] == '76192083-9'
    assert status.status == 'OK'


def _rendering_response(content: bytes, *, label='tributaria', **extra):
    payload = {
        'content': base64.b64encode(content).decode(),
        'mimeType': 'application/pdf',
        'filename': f'documento_{label}.pdf',
        'label': label,
        'copies': 1,
        'copyNumber': 1,
    }
    payload.update(extra)
    return payload


@respx.mock
def test_renderer_render_sends_base64_xml_and_decodes_the_rendering(sdk):
    """
    `data.renderings` es una lista: por defecto trae un único elemento
    (`'tributaria'`), `content` en base64 como el resto de la API.
    """
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/renderer/render',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'renderings': [_rendering_response(b'%PDF-1.4 ...')],
                },
            },
        ),
    )

    result = sdk.billing.document.renderer.render('ZG9jdW1lbnRv')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['bag']['xmlDocument'] == 'ZG9jdW1lbnRv'
    assert sent['bag']['options'] == {'renderer': {'format': 'pdf'}}
    assert result.first.mime_type == 'application/pdf'
    assert result.first.label == 'tributaria'
    assert result.first.content_bytes == b'%PDF-1.4 ...'


@respx.mock
def test_renderer_render_sends_renderings_when_given(sdk):
    """Pedir varias presentaciones/copias manda `renderer.renderings`."""
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/renderer/render',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'renderings': [
                        _rendering_response(
                            b'tributaria copy 1',
                            label='tributaria',
                            copies=2,
                            copyNumber=1,
                        ),
                        _rendering_response(
                            b'tributaria copy 2',
                            label='tributaria',
                            copies=2,
                            copyNumber=2,
                        ),
                        _rendering_response(b'cedible', label='cedible'),
                    ],
                },
            },
        ),
    )

    result = sdk.billing.document.renderer.render(
        'ZG9jdW1lbnRv',
        renderings={'tributaria': 2, 'cedible': 1},
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['bag']['options']['renderer']['renderings'] == {
        'tributaria': 2,
        'cedible': 1,
    }
    assert len(result.renderings) == 3
    tributarias = result.by_label('tributaria')
    assert [r.copy_number for r in tributarias] == [1, 2]
    assert result.by_label('cedible')[0].content_bytes == b'cedible'


@respx.mock
def test_renderer_render_omits_renderings_key_by_default(sdk):
    """Sin `renderings` explícito, no se manda esa clave (default API)."""
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/renderer/render',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'renderings': [_rendering_response(b'ok')]},
            },
        ),
    )

    sdk.billing.document.renderer.render('ZG9jdW1lbnRv')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert 'renderings' not in sent['bag']['options']['renderer']
    assert 'libredteData' not in sent['bag']


@respx.mock
def test_renderer_render_sends_libredte_data_when_given(sdk):
    """`libredte_data` viaja como `bag.libredteData` cuando se indica."""
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/renderer/render',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'renderings': [_rendering_response(b'ok')]},
            },
        ),
    )

    sdk.billing.document.renderer.render(
        'ZG9jdW1lbnRv',
        libredte_data={'extra': {'historial': ['evento 1']}},
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['bag']['libredteData'] == {
        'extra': {'historial': ['evento 1']},
    }


@respx.mock
def test_document_examples_list_maps_summaries(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/examples/list',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': [
                    {
                        'id': '033_factura_afecta/033_001_simple',
                        'category': '033_factura_afecta',
                        'case': '033_001_simple',
                    },
                ],
            },
        ),
    )

    examples = sdk.billing.document.examples.list()

    assert route.calls.last.request is not None
    assert examples[0].id == '033_factura_afecta/033_001_simple'
    assert examples[0].category == '033_factura_afecta'
    assert examples[0].case == '033_001_simple'


@respx.mock
def test_document_examples_get_sends_id_and_splits_expected(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/examples/get',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'id': '033_factura_afecta/033_001_simple',
                    'example': _INPUT_DATA,
                    'expected': {
                        'Encabezado': {'Totales': {'MntTotal': 1190}},
                    },
                },
            },
        ),
    )

    example = sdk.billing.document.examples.get(
        '033_factura_afecta/033_001_simple',
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['id'] == '033_factura_afecta/033_001_simple'
    assert example.example == _INPUT_DATA
    assert example.expected['Encabezado']['Totales']['MntTotal'] == 1190


@respx.mock
def test_mandatario_manager_create_from_certificate(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/trading_parties/mandatario_manager'
        '/createFromCertificate',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'run': '76192083-9',
                    'nombre': 'SASCO SpA',
                    'email': 'demo@sasco.example',
                },
            },
        ),
    )

    service = sdk.billing.trading_parties.mandatario_manager
    mandatario = service.create_from_certificate(_CERTIFICATE)

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['certificate'] == {
        'certificate': 'cert-pem',
        'privateKey': 'key-pem',
    }
    assert mandatario.run == '76192083-9'
    assert mandatario.nombre == 'SASCO SpA'
    assert mandatario.email == 'demo@sasco.example'


@respx.mock
def test_repository_catalog_find_sends_repository_and_id(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/system/repository/catalog/find',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'codigo': 'SANTIAGO', 'nombre': 'SANTIAGO'},
            },
        ),
    )

    repository = (
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Entity\\Comuna'
    )
    result = sdk.system.repository.catalog.find(repository, 'SANTIAGO')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['repository'] == repository
    assert sent['id'] == 'SANTIAGO'
    assert result == {'codigo': 'SANTIAGO', 'nombre': 'SANTIAGO'}


@respx.mock
def test_repository_catalog_find_one_by_sends_criteria_and_order(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/system/repository/catalog/findOneBy',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'codigo': 33, 'nombre_corto': 'Factura'},
            },
        ),
    )

    repository = (
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Contract\\TipoDocumentoInterface'
    )
    result = sdk.system.repository.catalog.find_one_by(
        repository,
        criteria={'codigo': 33},
        order_by={'codigo': 'ASC'},
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['repository'] == repository
    assert sent['criteria'] == {'codigo': 33}
    assert sent['orderBy'] == {'codigo': 'ASC'}
    assert result == {'codigo': 33, 'nombre_corto': 'Factura'}


@respx.mock
def test_repository_catalog_find_by_sends_criteria_and_order(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/system/repository/catalog/findBy',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': [{'codigo': 33, 'nombre_corto': 'Factura'}],
            },
        ),
    )

    repository = (
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Contract\\TipoDocumentoInterface'
    )
    result = sdk.system.repository.catalog.find_by(
        repository,
        criteria={'codigo': [33, 39]},
        order_by={'codigo': 'ASC'},
        limit=10,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['repository'] == repository
    assert sent['criteria'] == {'codigo': [33, 39]}
    assert sent['orderBy'] == {'codigo': 'ASC'}
    assert sent['limit'] == 10
    assert result == [{'codigo': 33, 'nombre_corto': 'Factura'}]


@respx.mock
def test_repository_catalog_list_returns_repository_ids(sdk):
    respx.post(
        f'{TEST_BASE_URL}/system/repository/catalog/list',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': [
                    'libredte\\lib\\Core\\Package\\Billing\\Component'
                    '\\Document\\Entity\\Comuna',
                ],
            },
        ),
    )

    repositories = sdk.system.repository.catalog.list()

    assert repositories == [
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Entity\\Comuna',
    ]


@respx.mock
def test_certificate_loader_load_sends_base64_and_decodes_metadata(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/system/certificate/loader/load',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'id': '76192083-9',
                    'name': 'SASCO SpA',
                    'email': 'demo@sasco.example',
                    'from': '2026-09-04T23:55:14',
                    'to': '2027-09-04T23:55:14',
                    'totalDays': 365,
                    'expirationDays': 365,
                    'isActive': True,
                    'issuer': 'Derafu Test Certificate Authority',
                    'modulus': 'MODULUS',
                    'exponent': 'AQAB',
                    'cert': 'CERT-PEM',
                    'chain': [],
                    'pkey': 'PKEY-PEM',
                },
            },
        ),
    )

    loaded = sdk.system.certificate.loader.load(b'contenido-del-p12', 'clave')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['certificate']['password'] == 'clave'
    assert (
        base64.b64decode(sent['certificate']['data']) == b'contenido-del-p12'
    )
    assert loaded.id == '76192083-9'
    assert loaded.name == 'SASCO SpA'
    assert loaded.email == 'demo@sasco.example'
    assert loaded.is_active is True
    assert loaded.certificate == 'CERT-PEM'
    assert loaded.private_key == 'PKEY-PEM'
    assert loaded.total_days == 365
    assert loaded.expiration_days == 365
    assert loaded.issuer == 'Derafu Test Certificate Authority'
    assert loaded.modulus == 'MODULUS'
    assert loaded.exponent == 'AQAB'
    assert loaded.chain == []


@respx.mock
def test_document_validator_validate_sends_source_and_returns_none(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/validator/validate',
    ).mock(return_value=httpx.Response(200, json={'meta': {}, 'data': {}}))

    result = sdk.billing.document.validator.validate('ZG9jdW1lbnRv')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['source'] == 'ZG9jdW1lbnRv'
    assert result is None


@respx.mock
def test_document_validator_validate_schema_returns_the_parsed_xml(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/document/validator/validateSchema',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'DTE': {'Documento': {'Encabezado': {}}}},
            },
        ),
    )

    result = sdk.billing.document.validator.validate_schema('ZG9jdW1lbnRv')

    assert result == {'DTE': {'Documento': {'Encabezado': {}}}}


@respx.mock
def test_document_validator_validate_signature_returns_the_raw_result(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/document/validator/validateSignature',
    ).mock(return_value=httpx.Response(200, json={'meta': {}, 'data': {}}))

    result = sdk.billing.document.validator.validate_signature('ZG9jdW1lbnRv')

    assert result == {}


@respx.mock
def test_dispatcher_load_xml_returns_an_envelope(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/dispatcher/loadXml',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'tag': 'EnvioDTE',
                    'xml': base64.b64encode(b'<EnvioDTE/>').decode(),
                },
            },
        ),
    )

    envelope = sdk.billing.document.dispatcher.load_xml('PERAZG==')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['xml'] == 'PERAZG=='
    assert envelope.tag == 'EnvioDTE'


@respx.mock
def test_dispatcher_validate_returns_the_parsed_envelope(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/document/dispatcher/validate',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'EnvioDTE': {'SetDTE': {'Caratula': {}}}},
            },
        ),
    )

    result = sdk.billing.document.dispatcher.validate('c29icmU=')

    assert result == {'EnvioDTE': {'SetDTE': {'Caratula': {}}}}


@respx.mock
def test_dispatcher_validate_schema_returns_the_parsed_envelope(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/document/dispatcher/validateSchema',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'EnvioDTE': {'SetDTE': {'Caratula': {}}}},
            },
        ),
    )

    result = sdk.billing.document.dispatcher.validate_schema('c29icmU=')

    assert result == {'EnvioDTE': {'SetDTE': {'Caratula': {}}}}


@respx.mock
def test_dispatcher_validate_signature_returns_a_list_of_raw_results(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/document/dispatcher/validateSignature',
    ).mock(
        return_value=httpx.Response(200, json={'meta': {}, 'data': [{}, {}]}),
    )

    result = sdk.billing.document.dispatcher.validate_signature('c29icmU=')

    assert result == [{}, {}]


@respx.mock
def test_sii_dte_validate_document_sends_parameters_and_decodes_result(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_dte/validateDocument',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'received': False,
                    'status': 'FNA',
                    'description': 'Folio no autorizado',
                },
            },
        ),
    )

    result = sdk.billing.integration.sii_dte.validate_document(
        company_rut='76192083-9',
        document_type=33,
        number=999999999,
        date='2025-01-01',
        total=1000,
        recipient_rut='23456789-6',
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['company'] == '76192083-9'
    assert sent['document'] == 33
    assert sent['recipient'] == '23456789-6'
    assert result.received is False
    assert result.status == 'FNA'
    assert result.description == 'Folio no autorizado'


@respx.mock
def test_sii_dte_validate_document_signature_sends_signature(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_dte'
        '/validateDocumentSignature',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'received': False, 'status': 'FNA'},
            },
        ),
    )

    sdk.billing.integration.sii_dte.validate_document_signature(
        company_rut='76192083-9',
        document_type=33,
        number=999999999,
        date='2025-01-01',
        total=1000,
        recipient_rut='23456789-6',
        signature='firma',
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['signature'] == 'firma'


@respx.mock
def test_sii_dte_request_status_by_email_sends_track_id(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_dte'
        '/requestXmlDocumentSentStatusByEmail',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'status': 'ERR', 'description': 'No autorizado'},
            },
        ),
    )

    result = sdk.billing.integration.sii_dte.request_status_by_email(
        123,
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
        company_rut='76192083-9',
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['trackId'] == 123
    assert result.status == 'ERR'
    assert result.description == 'No autorizado'


@respx.mock
def test_sii_rtc_send_aec_returns_a_send_result(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_rtc/sendAec',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'track_id': 456}},
        ),
    )

    result = sdk.billing.integration.sii_rtc.send_aec(
        'QUVDeG1s',
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
        company_rut='76192083-9',
        email_notif='cedente@example.com',
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['doc'] == 'QUVDeG1s'
    assert sent['emailNotif'] == 'cedente@example.com'
    assert sent['request']['options']['environment'] == 0
    assert result.track_id == 456


@respx.mock
def test_sii_rcv_check_document_assignability_returns_codigo_and_glosa(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_rcv'
        '/checkDocumentAssignability',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'codigo': '0', 'glosa': 'OK'}},
        ),
    )

    result = sdk.billing.integration.sii_rcv.check_document_assignability(
        company_rut='76192083-9',
        document_type=33,
        number=999999999,
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    assert result.codigo == '0'
    assert result.glosa == 'OK'


@respx.mock
def test_sii_rcv_get_document_sii_reception_date_parses_the_datetime(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_rcv'
        '/getDocumentSiiReceptionDate',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'fecha_recepcion_sii': '2025-01-02 10:30:00'},
            },
        ),
    )

    result = sdk.billing.integration.sii_rcv.get_document_sii_reception_date(
        company_rut='76192083-9',
        document_type=33,
        number=999999999,
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    assert result.fecha_recepcion_sii.isoformat() == '2025-01-02T10:30:00'
    assert result.raw == {'fecha_recepcion_sii': '2025-01-02 10:30:00'}


@respx.mock
def test_sii_rcv_list_document_events_returns_typed_events(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_rcv/listDocumentEvents',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': [
                    {
                        'codigo': '0',
                        'glosa': 'Envío Recibido Conforme',
                        'responsable': '76192083-9',
                        'fecha': '2025-01-02 10:30:00',
                    },
                ],
            },
        ),
    )

    result = sdk.billing.integration.sii_rcv.list_document_events(
        company_rut='76192083-9',
        document_type=33,
        number=999999999,
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    assert len(result.events) == 1
    assert result.events[0].codigo == '0'
    assert result.events[0].glosa == 'Envío Recibido Conforme'
    assert result.events[0].responsable == '76192083-9'


@respx.mock
def test_sii_rcv_submit_document_acceptance_sends_action(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/integration/sii_rcv'
        '/submitDocumentAcceptance',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'codigo': '0', 'glosa': 'OK'}},
        ),
    )

    result = sdk.billing.integration.sii_rcv.submit_document_acceptance(
        company_rut='76192083-9',
        document_type=33,
        number=999999999,
        action='ACD',
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['action'] == 'ACD'
    assert result.codigo == '0'


@respx.mock
def test_aec_build_sends_cedente_cesionario_cesion(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/ownership_transfer/aec/build',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'AEC': {
                        'DocumentoAEC': {
                            'Caratula': {'RutCedente': '76192083-9'},
                        },
                    },
                    'xml': 'PEFFQz48L0FFQz4=',
                },
            },
        ),
    )

    cedente = {
        'RUT': '76192083-9',
        'RazonSocial': 'SASCO SpA',
        'Direccion': 'Santa Cruz, Chile',
        'eMail': 'cedente@example.com',
        'RUTAutorizado': {'RUT': '76192083-9', 'Nombre': 'Administrador'},
    }
    cesionario = {
        'RUT': '76354771-K',
        'RazonSocial': 'Factoring S.A.',
        'Direccion': 'Providencia, Santiago',
        'eMail': 'factoring@example.com',
    }
    cesion = {'MontoCesion': 119000, 'UltimoVencimiento': '2024-02-14'}
    certificate = Certificate(certificate='cert-pem', private_key='key-pem')

    result = sdk.billing.ownership_transfer.aec.build(
        'RFRFeG1s',
        cedente=cedente,
        cesionario=cesionario,
        cesion=cesion,
        certificate=certificate,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']['bag']
    assert sent['source'] == 'RFRFeG1s'
    assert sent['cedente']['RUTAutorizado'] == {
        'RUT': '76192083-9',
        'Nombre': 'Administrador',
    }
    assert sent['cesionario']['RazonSocial'] == 'Factoring S.A.'
    assert sent['cesion']['MontoCesion'] == 119000
    assert result.aec['DocumentoAEC']['Caratula']['RutCedente'] == (
        '76192083-9'
    )
    assert result.xml_base64 == 'PEFFQz48L0FFQz4='
    assert result.xml == '<AEC></AEC>'


@respx.mock
def test_aec_validate_schema_returns_the_parsed_xml(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/ownership_transfer/aec/validateSchema',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'AEC': {'DocumentoAEC': {}}}},
        ),
    )

    result = sdk.billing.ownership_transfer.aec.validate_schema('QUVDeG1s')

    assert result == {'AEC': {'DocumentoAEC': {}}}


@respx.mock
def test_aec_validate_signature_returns_a_list_of_raw_results(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/ownership_transfer/aec/validateSignature',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': [{}, {}, {}]},
        ),
    )

    result = sdk.billing.ownership_transfer.aec.validate_signature('QUVDeG1s')

    assert result == [{}, {}, {}]


@respx.mock
def test_document_loader_load_xml_decodes_the_full_bag(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/document/loader/loadXml',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'document': {'Encabezado': {}},
                    'document_extra': None,
                    'document_stamp': '<TED/>',
                    'document_auth': None,
                    'document_type': {'codigo': 33, 'nombre': 'Factura'},
                    'options': {},
                },
            },
        ),
    )

    result = sdk.billing.document.loader.load_xml('RFRFeG1s')

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['xml'] == 'RFRFeG1s'
    assert result.document == {'Encabezado': {}}
    assert result.document_type == {'codigo': 33, 'nombre': 'Factura'}
    assert result.document_stamp == '<TED/>'
    assert result.document_extra is None
    assert result.document_auth is None


_BOOK_BAG = {
    'tipo': 'libro_ventas',
    'caratula': {
        'RutEmisorLibro': '76192083-9',
        'PeriodoTributario': '2024-01',
    },
    'detalle': [
        {
            'TpoDoc': 33,
            'NroDoc': 1,
            'TasaImp': 19,
            'FchDoc': '2024-01-10',
            'RUTDoc': '66666666-6',
            'RznSoc': 'Cliente de Prueba',
            'MntNeto': 100000,
            'MntIVA': 19000,
            'MntTotal': 119000,
        },
    ],
    'emisor': {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
}


@respx.mock
def test_book_builder_build_sends_bag_and_certificate(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/book/builder/build',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'LibroCompraVenta': {
                        'EnvioLibro': {
                            'Caratula': {'TipoOperacion': 'VENTA'},
                        },
                    },
                    'xml': (
                        'PExpYnJvQ29tcHJhVmVudGE+PC9MaWJyb0NvbXByYVZlbnRhPg=='
                    ),
                },
            },
        ),
    )

    result = sdk.billing.book.builder.build(
        _BOOK_BAG,
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    sent = json.loads(route.calls.last.request.content)['parameters']['bag']
    assert sent['tipo'] == 'libro_ventas'
    assert sent['certificate'] == {
        'certificate': 'cert-pem',
        'privateKey': 'key-pem',
    }
    assert (
        result.datos['LibroCompraVenta']['EnvioLibro']['Caratula'][
            'TipoOperacion'
        ]
        == 'VENTA'
    )
    assert result.xml_base64 == (
        'PExpYnJvQ29tcHJhVmVudGE+PC9MaWJyb0NvbXByYVZlbnRhPg=='
    )


@respx.mock
def test_book_loader_load_decodes_book_type_caratula_and_detalle(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/book/loader/load',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'book': None,
                    'book_auth': None,
                    'book_type': {
                        'codigo': 'libro_ventas',
                        'nombre': 'Libro de ventas',
                    },
                    'caratula': {
                        'RutEmisorLibro': '76192083-9',
                        'TipoOperacion': 'VENTA',
                    },
                    'detalle': [{'TpoDoc': 33, 'NroDoc': 1}],
                    'options': {},
                },
            },
        ),
    )

    result = sdk.billing.book.loader.load(
        _BOOK_BAG,
        certificate=Certificate(certificate='cert-pem', private_key='key-pem'),
    )

    # `book`/`book_auth` siempre vienen `None` desde `load()` (no
    # construye el libro) — ver docstring de `BookBag`.
    assert result.book is None
    assert result.book_auth is None
    assert result.book_type == {
        'codigo': 'libro_ventas',
        'nombre': 'Libro de ventas',
    }
    assert result.caratula == {
        'RutEmisorLibro': '76192083-9',
        'TipoOperacion': 'VENTA',
    }
    assert result.detalle == [{'TpoDoc': 33, 'NroDoc': 1}]


@respx.mock
def test_book_validator_validate_schema_returns_the_parsed_xml(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/book/validator/validateSchema',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {'LibroCompraVenta': {'EnvioLibro': {}}},
            },
        ),
    )

    result = sdk.billing.book.validator.validate_schema('TGlicm8=')

    assert result == {'LibroCompraVenta': {'EnvioLibro': {}}}


@respx.mock
def test_book_validator_validate_signature_returns_a_raw_result(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/book/validator/validateSignature',
    ).mock(return_value=httpx.Response(200, json={'meta': {}, 'data': {}}))

    result = sdk.billing.book.validator.validate_signature('TGlicm8=')

    assert result == {}


@respx.mock
def test_document_response_build_envio_recibos_sends_caratula_and_recibos(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/exchange/document_response'
        '/buildEnvioRecibos',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'EnvioRecibos': {
                        'SetRecibos': {
                            'Caratula': {'RutRecibe': '88888888-8'},
                        },
                    },
                    'xml': 'PEVudmlvUmVjaWJvcy8+',
                },
            },
        ),
    )

    recibos = [
        {
            'TipoDoc': 33,
            'Folio': 1,
            'FchEmis': '2024-01-15',
            'RUTEmisor': '88888888-8',
            'RUTRecep': '76192083-9',
            'MntTotal': 100000,
            'Recinto': 'Oficina central',
        },
    ]
    caratula = {'RutResponde': '76192083-9', 'RutRecibe': '88888888-8'}

    result = sdk.billing.exchange.document_response.build_envio_recibos(
        recibos,
        caratula=caratula,
        certificate=_CERTIFICATE,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']['bag']
    assert sent['tipo'] == 'envio_recibos'
    assert sent['caratula'] == caratula
    assert sent['data'] == recibos
    assert result.datos == {
        'EnvioRecibos': {
            'SetRecibos': {'Caratula': {'RutRecibe': '88888888-8'}},
        },
    }
    assert result.xml_base64 == 'PEVudmlvUmVjaWJvcy8+'


@respx.mock
def test_document_response_build_respuesta_envio_sends_caratula_and_data(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/billing/exchange/document_response'
        '/buildRespuestaEnvio',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'RespuestaDTE': {'Resultado': {}},
                    'xml': 'PFJlc3B1ZXN0YURURS8+',
                },
            },
        ),
    )

    data = {
        'resultado_dte': [
            {
                'TipoDTE': 33,
                'Folio': 1,
                'FchEmis': '2024-01-15',
                'RUTEmisor': '88888888-8',
                'RUTRecep': '76192083-9',
                'MntTotal': 100000,
                'CodEnvio': 1,
                'EstadoDTE': 0,
                'EstadoDTEGlosa': 'ACEPTADO OK',
            },
        ],
    }
    caratula = {
        'RutResponde': '76192083-9',
        'RutRecibe': '88888888-8',
        'IdRespuesta': 1,
    }

    result = sdk.billing.exchange.document_response.build_respuesta_envio(
        data,
        caratula=caratula,
        certificate=_CERTIFICATE,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']['bag']
    assert sent['tipo'] == 'respuesta_envio'
    assert sent['caratula'] == caratula
    assert sent['data'] == data
    assert result.datos == {'RespuestaDTE': {'Resultado': {}}}
    assert result.xml_base64 == 'PFJlc3B1ZXN0YURURS8+'


@respx.mock
def test_document_response_validate_schema_returns_the_parsed_xml(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/exchange/document_response/validateSchema',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'SetRecibos': {}}},
        ),
    )

    result = sdk.billing.exchange.document_response.validate_schema(
        'U2V0UmVjaWJvcw==',
    )

    assert result == {'SetRecibos': {}}


@respx.mock
def test_document_response_validate_signature_returns_a_list(sdk):
    respx.post(
        f'{TEST_BASE_URL}/billing/exchange/document_response'
        '/validateSignature',
    ).mock(return_value=httpx.Response(200, json={'meta': {}, 'data': [{}]}))

    result = sdk.billing.exchange.document_response.validate_signature(
        'U2V0UmVjaWJvcw==',
    )

    assert result == [{}]


@respx.mock
def test_previred_provider_get_indicadores_sends_periodo(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/human_resources/integration/previred_provider'
        '/getIndicadores',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'periodo': 202412,
                    'periodo_anterior': 202411,
                    'periodo_siguiente': 202501,
                    'indicadores': {'moneda': {'CLF': 38416.69}},
                },
            },
        ),
    )

    result = sdk.human_resources.integration.previred_provider.get_indicadores(
        202412,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent == {'periodo': 202412}
    assert result['periodo'] == 202412
    assert result['indicadores']['moneda']['CLF'] == 38416.69


@respx.mock
def test_payroll_calculator_calculate_sends_all_parameters(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/human_resources/payroll/calculator/calculate',
    ).mock(
        return_value=httpx.Response(
            200,
            json={'meta': {}, 'data': {'totales': {'liquido': 1000000}}},
        ),
    )

    empleado = {'run': 12345678, 'dv': '5', 'nombre': 'Juan'}
    contrato = {'tipo': 'I', 'sueldoBase': 1350000}

    result = sdk.human_resources.payroll.calculator.calculate(
        empleado,
        contrato,
        202412,
        detalles=[{'monto': 1000}],
        contexto={'tasaSeguroAccidente': 0.0095},
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['empleado'] == empleado
    assert sent['contrato'] == contrato
    assert sent['periodo'] == 202412
    assert sent['detalles'] == [{'monto': 1000}]
    assert sent['contexto'] == {'tasaSeguroAccidente': 0.0095}
    assert result == {'totales': {'liquido': 1000000}}


@respx.mock
def test_payroll_calculator_calculate_defaults_detalles_and_contexto(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/human_resources/payroll/calculator/calculate',
    ).mock(return_value=httpx.Response(200, json={'meta': {}, 'data': {}}))

    sdk.human_resources.payroll.calculator.calculate(
        {'run': 1},
        {'sueldoBase': 1},
        202412,
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['detalles'] == []
    assert sent['contexto'] is None


@respx.mock
def test_payroll_renderer_render_sends_liquidacion_and_options(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/human_resources/payroll/renderer/render',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'renderings': [
                        _rendering_response(
                            b'%PDF-1.4 ...',
                            label=None,
                            filename='liquidacion.pdf',
                        ),
                    ],
                },
            },
        ),
    )

    result = sdk.human_resources.payroll.renderer.render(
        {'totales': {'liquido': 1000000}},
        options={'format': 'pdf'},
    )

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['liquidacion'] == {'totales': {'liquido': 1000000}}
    assert sent['options'] == {'format': 'pdf'}
    assert result.first.label is None
    assert result.first.content_bytes == b'%PDF-1.4 ...'


@respx.mock
def test_payroll_renderer_render_defaults_options_to_empty_dict(sdk):
    route = respx.post(
        f'{TEST_BASE_URL}/human_resources/payroll/renderer/render',
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                'meta': {},
                'data': {
                    'renderings': [
                        _rendering_response(
                            b'<html></html>',
                            label=None,
                            mimeType='text/html',
                            filename='liquidacion.html',
                        ),
                    ],
                },
            },
        ),
    )

    sdk.human_resources.payroll.renderer.render({'foo': 'bar'})

    sent = json.loads(route.calls.last.request.content)['parameters']
    assert sent['options'] == {}
