"""
Clasificador híbrido de cuentas contables para documentos DIAN.

Tres niveles, en orden de prioridad:
  1. Reglas determinísticas por empresa (reglas.py) — NIT exacto o keyword.
  2. Caché de clasificaciones previas (cache.py) — evita repetir llamadas IA.
  3. IA (ia_clasificador.py) — fallback vía Anthropic para lo no cubierto.

Documentos con confianza de IA por debajo del umbral quedan 'pendiente'
para revisión humana (revision.py); al reimportar el Excel corregido,
las correcciones se agregan como reglas nuevas (nivel 1) para la próxima vez.
"""

from .reglas import cargar_reglas, guardar_reglas, buscar_regla, agregar_regla_nit
from .cache import CacheClasificacion
from .ia_clasificador import clasificar_lote_ia, IA_DISPONIBLE

UMBRAL_CONFIANZA = 0.85


def _normalizar_descripcion(texto):
    return ' '.join((texto or '').strip().lower().split())


def clasificar_lote_documentos(empresa_nit, docs, tipo_default='gasto'):
    """
    Clasifica un lote de documentos recibidos (compras/gastos) para una
    empresa. Cada doc debe tener: 'nit', 'nombre', 'detalle' (descripción u
    observación), 'total', 'folio', 'tipo_documento' (texto DIAN original).

    Retorna una lista paralela de dicts con:
      cuenta, tipo ('compra'|'gasto'), naturaleza, confianza, fuente
      ('regla'|'cache'|'ia'|'default'), justificacion, pendiente (bool)
    """
    reglas = cargar_reglas(empresa_nit)
    cache = CacheClasificacion()
    resultados = [None] * len(docs)
    pendientes_ia = []  # (idx, doc) sin regla ni caché

    for i, doc in enumerate(docs):
        nit = str(doc.get('nit', '')).strip()
        desc = _normalizar_descripcion(doc.get('detalle') or doc.get('nombre'))

        regla = buscar_regla(reglas, nit, desc, doc.get('nombre'))
        if regla:
            resultados[i] = {
                'cuenta': regla['cuenta'], 'tipo': regla.get('tipo', tipo_default),
                'naturaleza': 'debito', 'confianza': 1.0, 'fuente': 'regla',
                'justificacion': regla.get('notas', 'Regla configurada'),
                'pendiente': False
            }
            continue

        cacheado = cache.get(empresa_nit, nit, desc)
        if cacheado:
            resultados[i] = {**cacheado, 'fuente': 'cache', 'pendiente': False}
            continue

        pendientes_ia.append((i, doc))

    # Nivel 2: IA en lote para lo que no resolvió reglas ni caché
    if pendientes_ia and IA_DISPONIBLE:
        items = [{
            'id_temporal': f"{d.get('folio')}-{d.get('nit')}",
            'descripcion': d.get('detalle') or d.get('nombre') or '',
            'nombre_tercero': d.get('nombre') or '',
            'valor': d.get('total', 0),
            'tipo_documento': d.get('tipo_documento', '')
        } for _, d in pendientes_ia]

        clasificaciones_ia = clasificar_lote_ia(items)

        for (idx, doc), clas in zip(pendientes_ia, clasificaciones_ia):
            confianza = clas.get('confianza', 0.0)
            pendiente = confianza < UMBRAL_CONFIANZA
            resultado = {
                'cuenta': clas.get('cuenta_puc', reglas.get('cuenta_default_gasto')),
                'tipo': 'compra' if clas.get('tipo_cuenta') == 'compra_mercancia' else 'gasto',
                'naturaleza': clas.get('naturaleza', 'debito'),
                'confianza': confianza,
                'fuente': 'ia',
                'justificacion': clas.get('justificacion', ''),
                'pendiente': pendiente
            }
            resultados[idx] = resultado
            # Cachear siempre (incluso pendientes: evita re-preguntar a la
            # IA lo mismo; si el usuario corrige, la regla nueva
            # tiene prioridad sobre el caché de todas formas).
            nit = str(doc.get('nit', '')).strip()
            desc = _normalizar_descripcion(doc.get('detalle') or doc.get('nombre'))
            cache.set(empresa_nit, nit, desc, resultado)

    # Lo que no tuvo regla/caché y no hay IA disponible → default, pendiente
    for i, doc in enumerate(docs):
        if resultados[i] is None:
            resultados[i] = {
                'cuenta': reglas.get('cuenta_default_gasto'),
                'tipo': tipo_default, 'naturaleza': 'debito', 'confianza': 0.0,
                'fuente': 'default', 'justificacion': 'Sin regla, sin caché, IA no disponible',
                'pendiente': True
            }

    return resultados
