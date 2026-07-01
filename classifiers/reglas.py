"""
Nivel 1: reglas determinísticas por empresa (NIT exacto o keyword).

Cada empresa tiene su propio archivo reglas_empresas/<nit_empresa>.json.
Ver [[project-multi-empresa]] en memoria: las cuentas contables NO se
comparten entre empresas, cada una necesita su propio archivo.
"""

import json
import os

DIR_REGLAS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reglas_empresas')

_PLANTILLA_VACIA = {
    'empresa': None,
    'nit_empresa': None,
    'reglas_nit': {},
    'reglas_keyword': [],
    'cuenta_default_gasto': None,
    'cuenta_compras_mercancia': None,
    'cuenta_proveedores': None,
    'cuenta_iva_descontable': None,
    'cuenta_dev_compras': None,
}


def _ruta(empresa_nit):
    return os.path.join(DIR_REGLAS, f"{empresa_nit}.json")


def cargar_reglas(empresa_nit):
    """Carga las reglas de una empresa. Si no existe el archivo, devuelve
    una plantilla vacía (sin reglas, cuentas en None) — no se inventan
    cuentas de otra empresa como fallback."""
    ruta = _ruta(empresa_nit)
    if not os.path.exists(ruta):
        return {**_PLANTILLA_VACIA, 'nit_empresa': empresa_nit}
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)


def guardar_reglas(empresa_nit, reglas):
    os.makedirs(DIR_REGLAS, exist_ok=True)
    with open(_ruta(empresa_nit), 'w', encoding='utf-8') as f:
        json.dump(reglas, f, indent=2, ensure_ascii=False)


def buscar_regla(reglas, nit, descripcion_normalizada, nombre_emisor=None):
    """
    Busca una regla aplicable: primero por NIT exacto, luego por keyword
    en la descripción o nombre del emisor. Retorna dict {'cuenta','tipo',...}
    o None si no hay match.
    """
    nit = str(nit).strip()
    regla_nit = reglas.get('reglas_nit', {}).get(nit)
    if regla_nit:
        return regla_nit

    texto = f"{descripcion_normalizada or ''} {(nombre_emisor or '').lower()}"
    for regla_kw in reglas.get('reglas_keyword', []):
        palabra = regla_kw.get('contiene', '').lower()
        if palabra and palabra in texto:
            return regla_kw

    return None


def agregar_regla_nit(empresa_nit, nit, cuenta, tipo='gasto', notas=''):
    """Agrega/actualiza una regla NIT->cuenta y persiste el archivo.
    Usado por el Nivel 3 (revisión humana) para aprendizaje incremental."""
    reglas = cargar_reglas(empresa_nit)
    reglas.setdefault('reglas_nit', {})[str(nit).strip()] = {
        'cuenta': cuenta, 'tipo': tipo, 'notas': notas
    }
    guardar_reglas(empresa_nit, reglas)
    return reglas
