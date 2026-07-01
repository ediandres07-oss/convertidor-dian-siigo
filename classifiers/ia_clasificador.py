"""
Nivel 2: clasificación por IA (Anthropic) para documentos sin regla ni caché.

Se procesa en lotes para minimizar llamadas. Si no hay ANTHROPIC_API_KEY
configurada, IA_DISPONIBLE queda False y el sistema simplemente marca esos
documentos como pendientes de revisión (no falla ni bloquea el plano).
"""

import json
import logging
import os
import time

logger = logging.getLogger(__name__)

MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-sonnet-5')
TAMANO_LOTE = 20
MAX_REINTENTOS = 3

try:
    import anthropic
    _API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    IA_DISPONIBLE = bool(_API_KEY)
    _client = anthropic.Anthropic(api_key=_API_KEY) if IA_DISPONIBLE else None
except ImportError:
    IA_DISPONIBLE = False
    _client = None
    logger.warning("Paquete 'anthropic' no instalado; clasificación IA deshabilitada.")

_TOOL_SCHEMA = {
    "name": "clasificar_documentos_puc",
    "description": "Clasifica cada documento contable a una cuenta del Plan Único de Cuentas colombiano (PUC, Decreto 2650).",
    "input_schema": {
        "type": "object",
        "properties": {
            "clasificaciones": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id_temporal": {"type": "string"},
                        "cuenta_puc": {"type": "string", "description": "Cuenta PUC, 4 a 6 dígitos"},
                        "tipo_cuenta": {"type": "string", "enum": ["gasto", "costo", "compra_mercancia", "ingreso"]},
                        "naturaleza": {"type": "string", "enum": ["debito", "credito"]},
                        "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                        "justificacion": {"type": "string"}
                    },
                    "required": ["id_temporal", "cuenta_puc", "tipo_cuenta", "naturaleza", "confianza", "justificacion"]
                }
            }
        },
        "required": ["clasificaciones"]
    }
}


def _construir_prompt(items):
    lineas = []
    for it in items:
        lineas.append(
            f"- id={it['id_temporal']} | tercero={it['nombre_tercero']} | "
            f"descripción={it['descripcion']} | valor=${it['valor']:,.2f} | "
            f"tipo_documento={it['tipo_documento']}"
        )
    return (
        "Clasifica cada uno de estos documentos contables colombianos a su "
        "cuenta del Plan Único de Cuentas (PUC, Decreto 2650), a nivel de "
        "subcuenta (6 dígitos) cuando sea posible, mínimo 4 dígitos.\n\n"
        "Documentos:\n" + "\n".join(lineas) +
        "\n\nUsa la herramienta clasificar_documentos_puc para responder, "
        "un item por cada documento listado (mismo id_temporal)."
    )


def clasificar_lote_ia(items):
    """
    items: lista de dicts {id_temporal, descripcion, nombre_tercero, valor, tipo_documento}
    Retorna una lista PARALELA (mismo orden/longitud que items) de dicts:
      {cuenta_puc, tipo_cuenta, naturaleza, confianza, justificacion}
    Si la IA no está disponible o falla tras reintentos, retorna confianza=0
    para que el llamador marque esos items como pendientes.
    """
    if not IA_DISPONIBLE:
        return [_resultado_vacio() for _ in items]

    resultados_por_id = {}
    for inicio in range(0, len(items), TAMANO_LOTE):
        lote = items[inicio:inicio + TAMANO_LOTE]
        resultados_por_id.update(_clasificar_un_lote(lote))

    return [resultados_por_id.get(it['id_temporal'], _resultado_vacio()) for it in items]


def _resultado_vacio():
    return {'cuenta_puc': None, 'tipo_cuenta': 'gasto', 'naturaleza': 'debito',
            'confianza': 0.0, 'justificacion': 'IA no disponible o sin respuesta'}


def _clasificar_un_lote(lote):
    prompt = _construir_prompt(lote)
    ultimo_error = None

    for intento in range(MAX_REINTENTOS):
        try:
            resp = _client.messages.create(
                model=MODEL,
                max_tokens=4096,
                tools=[_TOOL_SCHEMA],
                tool_choice={"type": "tool", "name": "clasificar_documentos_puc"},
                messages=[{"role": "user", "content": prompt}]
            )
            for block in resp.content:
                if block.type == 'tool_use':
                    data = block.input
                    return {c['id_temporal']: c for c in data.get('clasificaciones', [])}
            logger.warning("Respuesta IA sin tool_use, reintentando...")
        except Exception as e:
            ultimo_error = e
            espera = 2 ** intento
            logger.warning(f"Error llamando API Anthropic (intento {intento+1}/{MAX_REINTENTOS}): {e}. Reintentando en {espera}s...")
            time.sleep(espera)

    logger.error(f"Clasificación IA falló tras {MAX_REINTENTOS} intentos: {ultimo_error}")
    return {}
