LibreDTE: SDK Python para la API de LibreDTE Lib
================================================

SDK Python (``libredte_lib_sdk``) que orquesta la API de LibreDTE Lib
(``https://core.libredte.cl/api`` por defecto) para cubrir el ciclo de
emisión de un DTE: borrador, documento timbrado y firmado,
envío al SII, consulta de estado por Track ID, y generación de HTML/PDF
— más carga y validación de CAF real, y generación de CAF y certificado
ficticios para poder probar todo lo anterior sin credenciales reales.

Pensado como base de una app de facturación (ej. Django): este SDK
concentra la lógica de negocio/orquestación de DTE, para que la app web
sea solo vista, autenticación y persistencia.

El paquete Python espeja la organización de la propia API
(``package.component.worker::operation``): ``sdk.billing.<component>
.<worker>`` para negocio DTE, ``sdk.system.<component>.<worker>`` para
infraestructura de la biblioteca (catálogos reales, carga de certificados
— ver "Recursos de `system`" más abajo).

Instalación
-----------

.. code-block:: bash

    pip install libredte-lib-sdk

Uso
---

.. code-block:: python

    import dataclasses

    from libredte_lib_sdk import LibreDTE
    from libredte_lib_sdk.billing.common import SII_RUT
    from libredte_lib_sdk.billing.integration import SiiRequestOptions
    from libredte_lib_sdk.billing.trading_parties import Mandatario

    sdk = LibreDTE()  # base_url y api_token también vía env vars, ver abajo
    b = sdk.billing

    input_data = {
        'Encabezado': {
            'IdDoc': {
                'TipoDTE': 33,
                'Folio': 1
            },
            'Emisor': {
                'RUTEmisor': '76192083-9',
                'RznSoc': 'SASCO SpA',
                'GiroEmis': 'Servicios',
                'Acteco': 620200,
                'DirOrigen': 'Santiago',
                'CmnaOrigen': 'Santiago',
            },
            'Receptor': {
                'RUTRecep': '12345678-5',
                'RznSocRecep': 'Cliente de prueba',
                'GiroRecep': 'Giro',
                'DirRecep': 'Santiago',
                'CmnaRecep': 'Santiago',
            },
        },
        'Detalle': [
            {
                'NmbItem': 'Producto A',
                'QtyItem': 1,
                'PrcItem': 1000
            }
        ],
    }

    # CAF y certificado ficticios, para pruebas/desarrollo:
    caf = b.identifier.caf_faker.create(
        {'rut': '76192083-9', 'razon_social': 'SASCO SpA'},
        codigo_documento=33, folio_desde=1, folio_hasta=100,
    )
    certificate = b.trading_parties.mandatario_manager.create_fake_certificate(
        Mandatario(run='76192083-9', nombre='SASCO SpA', email='sasco@example.com'),
    )

    # En producción: cargar y validar el CAF real que el SII le entregó
    # al emisor, en vez del CAF ficticio de arriba.
    # caf = b.identifier.caf_loader.load(xml_base64_del_caf_subido)
    # b.identifier.caf_validator.validate(caf.xml_base64)

    # 1. Borrador.
    borrador = b.document.builder.build_draft(input_data)

    # 2. Documento real, timbrado y firmado.
    documento = b.document.builder.build_signed(
        input_data, caf_xml=caf.xml_base64, certificate=certificate,
    )

    # 3. Sobres. El envío normal usa dos: uno para el SII y otro para el
    # receptor del documento (el cliente). `documento` ya trae
    # certificate/emisor incluidos — no hace falta pasarlos aparte, salvo
    # `autorizacion_dte` del emisor (`fecha_resolucion` y
    # `numero_resolucion`), que va en la carátula.
    documento = dataclasses.replace(
        documento,
        emisor={
            **documento.emisor,
            'autorizacion_dte': {
                'fecha_resolucion': '2019-12-23',
                'numero_resolucion': 0,
            },
        },
    )

    # El sobre para el SII siempre tiene al SII como receptor.
    sobre_sii = b.document.dispatcher.create(documento, receptor_rut=SII_RUT)

    # El sobre para el cliente toma el receptor del documento.
    sobre_cliente = b.document.dispatcher.create(documento)

    # 4. Envío al SII y estado del envío, por Track ID.
    envio = b.integration.sii_dte.send(
        sobre_sii.xml_base64, certificate=certificate,
        company_rut='76192083-9',
    )
    estado = b.integration.sii_dte.check_status(
        envio.track_id, certificate=certificate, company_rut='76192083-9',
    )

    # Las boletas (tipos 39 y 41) se envían por otra API del SII, solo
    # disponible en Lib Pro: `b.integration.sii_boleta` tiene `send()`,
    # `check_status()` y `validate_document()` con la misma forma.

    # Reintentos y tiempos de una llamada al SII (todos opcionales; la API
    # usa los suyos si no se indican y los ajusta a su rango).
    estado = b.integration.sii_dte.check_status(
        envio.track_id, certificate=certificate, company_rut='76192083-9',
        options=SiiRequestOptions(retries=3, timeout=20, max_duration=60),
    )

    # 5. HTML o PDF — misma forma de respuesta para ambos.
    html = b.document.renderer.render(documento.xml_base64, format='html')
    pdf = b.document.renderer.render(documento.xml_base64, format='pdf')
    pdf_bytes = pdf.first.content_bytes

    # Varias copias/presentaciones en una sola llamada (ej. cedible +
    # tributaria):
    copias = b.document.renderer.render(
        documento.xml_base64,
        format='pdf',
        renderings={'tributaria': 1, 'cedible': 1},
    )
    cedible_bytes = copias.by_label('cedible')[0].content_bytes

Cada componente (``document``, ``identifier``, ``trading_parties``,
``integration``) agrupa servicios independientes, uno por *worker* de la
API: cada método hace exactamente una llamada HTTP, sin encadenar red por
detrás. Encadenar los pasos (ej. armar el documento, el sobre, y
enviarlo) es responsabilidad de quien use el SDK.

Configuración
-------------

Base URL
~~~~~~~~

Por defecto el SDK apunta a ``https://core.libredte.cl/api``. Para usar
otra API (ej. ``https://pro.libredte.cl/api``, o un ambiente propio),
pasar ``base_url`` al construir ``LibreDTE`` o setear la variable de
entorno ``LIBREDTE_LIB_SDK_BASE_URL``:

.. code-block:: python

    sdk = LibreDTE(base_url='https://pro.libredte.cl/api')

.. code-block:: bash

    export LIBREDTE_LIB_SDK_BASE_URL=https://pro.libredte.cl/api

``core.libredte.cl`` y ``pro.libredte.cl`` exponen el mismo contrato con
límites de solicitudes distintos; ambos aceptan la variante ``LibreDTE
(base_url=..., ...)`` con el resto de los parámetros de configuración
(``api_token``, ``auth_scheme``, ``timeout``, ``http_client``).

Autenticación
~~~~~~~~~~~~~

``LibreDTE(api_token=...)`` o la variable de entorno
``LIBREDTE_LIB_SDK_TOKEN`` — si está presente, se manda como header
``Authorization: <esquema> <token>``. El esquema es ``Bearer`` por
defecto (lo que espera ``core.libredte.cl``/``pro.libredte.cl``);
configurable con ``LibreDTE(auth_scheme=...)`` o la variable de entorno
``LIBREDTE_LIB_SDK_AUTH_SCHEME`` para hablar con otra API que use un
esquema distinto (ej. ``'Token'``):

.. code-block:: python

    sdk = LibreDTE(
        base_url='https://app.apigateway.cl/api/v2/libredte',
        api_token='...',
        auth_scheme='Token',
    )

Recursos de ``system``
-----------------------

Además de ``billing`` (negocio DTE), el SDK expone ``system``:
infraestructura de la biblioteca que una app consumidora
necesita para poblar sus propios datos, no operaciones de facturación.

.. code-block:: python

    s = sdk.system

    # Ejemplos de documentos reales (los mismos casos de prueba,
    # validados, de libredte-lib-core) — útiles para poblar datos de
    # demostración con variedad real en vez de inventada a mano.
    ejemplos = b.document.examples.list()  # [ExampleSummary(id=..., category=..., case=...), ...]
    ejemplo = b.document.examples.get(ejemplos[0].id)
    documento = b.document.builder.build_signed(
        ejemplo.example, caf_xml=caf.xml_base64, certificate=certificate,
    )

    # Catálogos/repositorios reales (comunas, tipos de documento, etc.)
    # — el esquema de cada elemento depende del repositorio pedido, no
    # hay un DTO fijo: se devuelve el dict/list tal cual la API.
    repositorios = s.repository.catalog.list()  # FQCN de cada repositorio disponible
    tipos_dte = s.repository.catalog.find_by(
        'libredte\\lib\\Core\\Package\\Billing\\Component\\Document'
        '\\Contract\\TipoDocumentoInterface',
        criteria={'codigo': [33, 39]},  # coincidencia con cualquiera de estos códigos
    )

    # Cargar un certificado real (.p12/.pfx) sin desempaquetarlo
    # localmente: la API entrega certificado (PEM) + RUT/nombre/correo
    # ya extraídos en una sola llamada — mismo `Certificate` que usan
    # build_signed()/dispatcher.create(), ya con todos los datos.
    certificate = s.certificate.loader.load(datos_del_archivo_pfx, 'contraseña')
    print(certificate.id, certificate.name, certificate.email)

Errores
-------

Cualquier error de la API (validación, regla de negocio, error interno)
levanta ``libredte_lib_sdk.LibreDteApiError``, con ``.status_code``,
``.detail`` y ``.php_class`` (la clase real de la excepción PHP detrás,
si la API la informó — ej. ``DocumentException``, o una excepción de
autenticación del SII). Un ``429`` de la API levanta
``LibreDteRateLimitError`` (subclase de lo anterior), con
``.retry_after`` y ``.reset_at`` (cuándo se libera), ``.policy`` (cuál límite
se agotó), el cupo del usuario (``.limit``/``.remaining``, solo con
autenticación) y el límite por IP (``.ip_limit``/``.ip_remaining``). Cada
dato es ``None`` si la API no lo informa. Un problema de red levanta
``libredte_lib_sdk.LibreDteConnectionError``.

Desarrollo
----------

.. code-block:: bash

    make install-dev
    make check       # ruff + tests unitarios (offline, sin red)
    make test-live   # tests de integración reales contra la API

Los tests unitarios no hacen red real: mockean la API con ``respx``. Los
de ``tests/integration/`` sí (marker ``live``), y están excluidos por
defecto de ``pytest``/``make test``/``make check``.

Los tests ``live`` usan ``LIBREDTE_LIB_SDK_BASE_URL`` y
``LIBREDTE_LIB_SDK_TOKEN``. Los de ``tests/integration/test_sii_certification.py``
envían documentos reales al ambiente de certificación del SII y se omiten si
faltan estas variables de entorno:

- ``LIBREDTE_CERTIFICATE_CERT`` y ``LIBREDTE_CERTIFICATE_PKEY``: certificado
  digital y su clave privada, en PEM (un ``\n`` literal vale como salto de
  línea).
- ``LIBREDTE_CAF_DIR``: directorio con los CAF de certificación, uno por tipo
  de documento (``033.xml``, ``034.xml``, ``039.xml``, ...).

Términos y condiciones de uso
------------------------------

Este proyecto está licenciado bajo la Licencia MIT. Ver
`LICENSE <LICENSE>`_.
