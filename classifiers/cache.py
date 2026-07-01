"""
Caché SQLite de clasificaciones IA previas: misma empresa + NIT + descripción
normalizada -> mismo resultado, sin volver a llamar la API.
"""

import sqlite3
import os
import threading

_RUTA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache.sqlite3')
_lock = threading.Lock()


class CacheClasificacion:
    def __init__(self, ruta_db=_RUTA_DB):
        self.ruta_db = ruta_db
        self._crear_tabla()

    def _conectar(self):
        return sqlite3.connect(self.ruta_db)

    def _crear_tabla(self):
        with _lock, self._conectar() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    empresa_nit TEXT NOT NULL,
                    nit TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    cuenta TEXT,
                    tipo TEXT,
                    naturaleza TEXT,
                    confianza REAL,
                    justificacion TEXT,
                    PRIMARY KEY (empresa_nit, nit, descripcion)
                )
            """)

    def get(self, empresa_nit, nit, descripcion):
        with _lock, self._conectar() as con:
            cur = con.execute(
                "SELECT cuenta, tipo, naturaleza, confianza, justificacion "
                "FROM cache WHERE empresa_nit=? AND nit=? AND descripcion=?",
                (empresa_nit, str(nit).strip(), descripcion)
            )
            row = cur.fetchone()
        if not row:
            return None
        cuenta, tipo, naturaleza, confianza, justificacion = row
        return {
            'cuenta': cuenta, 'tipo': tipo, 'naturaleza': naturaleza,
            'confianza': confianza, 'justificacion': justificacion
        }

    def set(self, empresa_nit, nit, descripcion, resultado):
        with _lock, self._conectar() as con:
            con.execute(
                "INSERT OR REPLACE INTO cache "
                "(empresa_nit, nit, descripcion, cuenta, tipo, naturaleza, confianza, justificacion) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (empresa_nit, str(nit).strip(), descripcion,
                 resultado.get('cuenta'), resultado.get('tipo'),
                 resultado.get('naturaleza'), resultado.get('confianza'),
                 resultado.get('justificacion'))
            )
