# Copyright (C) 2026 LibreDTE <https://www.libredte.cl>
# SPDX-License-Identifier: MIT

"""
Tests `live` contra el SII de certificación, con un certificado real.

Envían documentos de verdad al ambiente de certificación del SII (no al de
producción) y consultan su estado, así que necesitan el certificado de
`LIBREDTE_CERTIFICATE_CERT`/`LIBREDTE_CERTIFICATE_PKEY` y los CAF de
certificación de `LIBREDTE_CAF_DIR` (ver las fixtures `sii_certificate` y
`sii_caf`). Sin ellos se omiten.

El emisor es `76192083-9` y su autorización de certificación es la
resolución `0` del `2019-12-23`. Cada ejecución usa un folio al azar dentro
del rango del CAF; si el SII ya lo había recibido, se prueba con otro.

`sii_rtc.get_related_assignment_status` solo se prueba con tiempos acotados:
en certificación el servicio del SII no responde y deja la llamada colgada.
"""

from __future__ import annotations

import dataclasses
import datetime
import random
import time
from zoneinfo import ZoneInfo

import pytest

from libredte_lib_sdk.billing.common import SII_RUT
from libredte_lib_sdk.billing.enums import SiiEnvironment
from libredte_lib_sdk.billing.integration import SiiRequestOptions
from libredte_lib_sdk.exceptions import LibreDteApiError

pytestmark = pytest.mark.live

_COMPANY = '76192083-9'
_CERTIFICATION = SiiEnvironment.CERTIFICATION
_AUTORIZACION_DTE = {
    'fecha_resolucion': '2019-12-23',
    'numero_resolucion': 0,
}
_EMISOR = {
    'RUTEmisor': _COMPANY,
    'RznSoc': 'SASCO SpA',
    'GiroEmis': 'Servicios',
    'Acteco': 620200,
    'DirOrigen': 'Santiago',
    'CmnaOrigen': 'Santiago',
}
_RECEPTOR_SII = {
    'RUTRecep': SII_RUT,
    'RznSocRecep': 'Servicio de Impuestos Internos',
    'GiroRecep': 'Gobierno',
    'DirRecep': 'Santiago',
    'CmnaRecep': 'Santiago',
}
_RECEPTOR_BOLETA = {
    'RUTRecep': '66666666-6',
    'RznSocRecep': 'Cliente de prueba',
}
# Estados del SII en los que el envío todavía se está procesando. El `-11`
# ("Error de Proceso") es lo que informa el SII de un track que todavía no
# registra, como el que se acaba de enviar.
_IN_PROGRESS = {'REC', 'PRD', 'SOK', 'CRT', 'FOK', 'FPR', '-11'}
# El SII rechaza un folio ya recibido con el 100 (mismos datos del documento) o
# con el 101 (datos distintos).
_DUPLICATED_FOLIO_CODES = {100, 101}
_CHILE = ZoneInfo('America/Santiago')
_ATTEMPTS = 5
_POLLS = 10
_POLL_SECONDS = 10


def _sii_envelope(sdk, certificate, caf, document_type, folio, **document):
    """Arma el documento firmado y su sobre con el SII como receptor."""
    xml_base64, _, _ = caf
    data = {
        'Encabezado': {
            'IdDoc': {'TipoDTE': document_type, 'Folio': folio},
            'Emisor': _EMISOR,
            'Receptor': document['receptor'],
        },
        'Detalle': document['detalle'],
    }
    bag = sdk.billing.document.builder.build_signed(
        data,
        caf_xml=xml_base64,
        certificate=certificate,
    )
    bag = dataclasses.replace(
        bag,
        emisor={**bag.emisor, 'autorizacion_dte': _AUTORIZACION_DTE},
    )
    envelope = sdk.billing.document.dispatcher.create(
        bag,
        receptor_rut=SII_RUT,
    )

    return bag, envelope


def _today() -> str:
    return datetime.datetime.now(_CHILE).date().isoformat()


def _wait_for_final_status(check):
    status = check()
    for _ in range(_POLLS):
        if status.status not in _IN_PROGRESS:
            break
        time.sleep(_POLL_SECONDS)
        status = check()

    return status


def _send_until_accepted(send, check, folios):
    """
    Envía y consulta hasta que el SII acepta algún folio.

    Un folio que el SII ya había recibido se rechaza con el código 101:
    se prueba con otro. Devuelve el estado final y el folio.
    """
    status = None
    folio = None
    for folio in random.sample(folios, _ATTEMPTS):
        track_id = send(folio)
        status = _wait_for_final_status(lambda t=track_id: check(t))
        rejected_codes = _error_codes(status)
        if rejected_codes.isdisjoint(_DUPLICATED_FOLIO_CODES):
            break

    return status, folio


def _error_codes(status) -> set[int]:
    details = getattr(status, 'details', None) or []

    return {error.code for detail in details for error in detail.errors}


def test_a_boleta_is_accepted_by_the_sii_and_its_status_is_queried(
    real_sdk,
    sii_certificate,
    sii_caf,
):
    caf = sii_caf(39)
    _, desde, hasta = caf
    boleta = real_sdk.billing.integration.sii_boleta

    def send(folio):
        _, envelope = _sii_envelope(
            real_sdk,
            sii_certificate,
            caf,
            39,
            folio,
            receptor=_RECEPTOR_BOLETA,
            detalle=[{'NmbItem': 'Producto A', 'QtyItem': 1, 'PrcItem': 1000}],
        )
        assert envelope.tag == 'EnvioBOLETA'
        assert envelope.caratula['RutReceptor'] == SII_RUT
        sent = boleta.send(
            envelope.xml_base64,
            certificate=sii_certificate,
            company_rut=_COMPANY,
            environment=_CERTIFICATION,
        )
        assert sent.status == 'REC'
        assert sent.rut_company == _COMPANY
        assert sent.received_at is not None

        return sent.track_id

    def check(track_id):
        return boleta.check_status(
            track_id,
            certificate=sii_certificate,
            company_rut=_COMPANY,
            environment=_CERTIFICATION,
        )

    status, folio = _send_until_accepted(
        send,
        check,
        list(range(max(desde, hasta - 500), hasta + 1)),
    )

    assert status.error is False
    assert status.status == 'EPR'
    assert status.resume.accepted == 1
    assert status.documents[39].accepted == 1
    assert status.details == []

    # En una boleta el precio ya incluye el IVA: el total es el neto dado.
    validation = boleta.validate_document(
        company_rut=_COMPANY,
        document_type=39,
        number=folio,
        date=_today(),
        total=1000,
        recipient_rut='66666666-6',
        certificate=sii_certificate,
        environment=_CERTIFICATION,
    )
    assert validation.status == 'DOK'


def test_a_boleta_with_a_repeated_folio_is_reported_with_its_error(
    real_sdk,
    sii_certificate,
    sii_caf,
):
    """
    Un folio ya recibido por el SII se informa en `details`.

    Reenviar el mismo XML lo rechaza el SII al subirlo, así que cada envío
    arma su propio XML, con otra fecha de firma, y el folio es el mismo.
    """
    caf = sii_caf(39)
    _, desde, hasta = caf
    boleta = real_sdk.billing.integration.sii_boleta

    # Se envía dos veces el mismo folio: la segunda es la rechazada.
    folio = random.randint(max(desde, hasta - 500), hasta)
    track_ids = []
    for _ in range(2):
        _, envelope = _sii_envelope(
            real_sdk,
            sii_certificate,
            caf,
            39,
            folio,
            receptor=_RECEPTOR_BOLETA,
            detalle=[{'NmbItem': 'Producto A', 'QtyItem': 1, 'PrcItem': 1000}],
        )
        sent = boleta.send(
            envelope.xml_base64,
            certificate=sii_certificate,
            company_rut=_COMPANY,
            environment=_CERTIFICATION,
        )
        track_ids.append(sent.track_id)
        # La fecha de firma tiene resolución de segundos: el segundo XML debe
        # salir distinto del primero.
        time.sleep(1.1)

    statuses = [
        _wait_for_final_status(
            lambda t=track_id: boleta.check_status(
                t,
                certificate=sii_certificate,
                company_rut=_COMPANY,
                environment=_CERTIFICATION,
            ),
        )
        for track_id in track_ids
    ]

    rejected = [s for s in statuses if s.resume.rejected == 1]
    assert rejected
    [detail] = rejected[0].details
    assert detail.status == 'RCH'
    assert detail.folio == folio
    assert _DUPLICATED_FOLIO_CODES & {e.code for e in detail.errors}


def test_an_exempt_invoice_is_accepted_by_the_sii_and_queried(
    real_sdk,
    sii_certificate,
    sii_caf,
):
    caf = sii_caf(34)
    _, desde, hasta = caf
    sii = real_sdk.billing.integration.sii_dte

    def send(folio):
        _, envelope = _sii_envelope(
            real_sdk,
            sii_certificate,
            caf,
            34,
            folio,
            receptor=_RECEPTOR_SII,
            detalle=[
                {
                    'NmbItem': 'Servicio exento',
                    'QtyItem': 1,
                    'PrcItem': 1000,
                    'IndExe': 1,
                },
            ],
        )
        assert envelope.tag == 'EnvioDTE'
        assert envelope.caratula['RutReceptor'] == SII_RUT
        return sii.send(
            envelope.xml_base64,
            certificate=sii_certificate,
            company_rut=_COMPANY,
            environment=_CERTIFICATION,
        ).track_id

    def check(track_id):
        return sii.check_status(
            track_id,
            certificate=sii_certificate,
            company_rut=_COMPANY,
            environment=_CERTIFICATION,
        )

    status, _ = _send_until_accepted(
        send,
        check,
        list(range(desde, hasta + 1)),
    )

    assert status.error is False
    assert status.status == 'EPR'
    assert status.raw['resume']['accepted'] == 1
    assert status.raw['documents']['34']['accepted'] == 1


def test_the_envelope_for_the_client_keeps_the_receptor_of_the_document(
    real_sdk,
    sii_certificate,
    sii_caf,
):
    """Sin `receptor_rut` el sobre va al receptor real del documento."""
    caf = sii_caf(34)
    _, desde, _ = caf
    bag, to_sii = _sii_envelope(
        real_sdk,
        sii_certificate,
        caf,
        34,
        desde,
        receptor={**_RECEPTOR_SII, 'RUTRecep': '12345678-5'},
        detalle=[
            {
                'NmbItem': 'Servicio',
                'QtyItem': 1,
                'PrcItem': 1000,
                'IndExe': 1,
            },
        ],
    )

    to_client = real_sdk.billing.document.dispatcher.create(bag)

    assert to_sii.caratula['RutReceptor'] == SII_RUT
    assert to_client.caratula['RutReceptor'] == '12345678-5'


def test_the_sii_queries_for_a_document_the_sii_has_not_received(
    real_sdk,
    sii_certificate,
):
    sii = real_sdk.billing.integration
    kwargs = {
        'company_rut': _COMPANY,
        'document_type': 33,
        'number': 999999,
        'certificate': sii_certificate,
        'environment': _CERTIFICATION,
    }

    validation = sii.sii_dte.validate_document(
        date=_today(),
        total=1000,
        recipient_rut='12345678-5',
        **kwargs,
    )
    assert validation.received is False
    # `FAU` (no recibido) o `FNA` (no autorizado): el SII no lo tiene.
    assert validation.status in {'FAU', 'FNA'}

    assert sii.sii_rcv.list_document_events(**kwargs).events == []

    assignability = sii.sii_rcv.check_document_assignability(**kwargs)
    assert isinstance(assignability.codigo, int)
    assert assignability.glosa

    assignment = sii.sii_rtc.get_assignment_status(**kwargs)
    assert assignment.assigned is False
    assert assignment.holder is None

    aec = sii.sii_rtc.check_status(
        1,
        certificate=sii_certificate,
        environment=_CERTIFICATION,
    )
    assert aec.track_id == 1
    assert aec.error is True
    assert aec.final is False


def test_the_envelope_contains_the_signed_document(
    real_sdk,
    sii_certificate,
    sii_caf,
):
    caf = sii_caf(34)
    _, desde, _ = caf
    bag, envelope = _sii_envelope(
        real_sdk,
        sii_certificate,
        caf,
        34,
        desde,
        receptor=_RECEPTOR_SII,
        detalle=[
            {
                'NmbItem': 'Servicio',
                'QtyItem': 1,
                'PrcItem': 1000,
                'IndExe': 1,
            },
        ],
    )

    assert [d.document_id for d in envelope.documents] == [bag.document_id]


def test_a_related_assignment_query_that_the_sii_never_answers_fails_in_time(
    real_sdk,
    sii_certificate,
):
    """
    El servicio del SII que consulta la cesión no responde en certificación.

    Con un solo intento de 10 s la llamada termina en poco más de eso, con el
    error de la API, y la API sigue atendiendo.
    """
    rtc = real_sdk.billing.integration.sii_rtc
    start = time.monotonic()

    try:
        result = rtc.get_related_assignment_status(
            company_rut=_COMPANY,
            document_type=34,
            number=1,
            related_company_rut=_COMPANY,
            certificate=sii_certificate,
            environment=_CERTIFICATION,
            options=SiiRequestOptions(retries=1, timeout=10, max_duration=10),
        )
    except LibreDteApiError:
        pass
    else:
        # Si el SII respondiera, la consulta se resuelve con su estado.
        assert result.assigned is not None

    assert time.monotonic() - start < 25
    assert real_sdk.billing.document.examples.list()
