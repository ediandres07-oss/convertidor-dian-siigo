#!/usr/bin/env python3
"""
Mapeo Detallado de Conceptos - Norma DIAN
Analiza cada concepto específicamente y genera mapeo completo
"""

import pandas as pd
from datetime import datetime

class MapeadorConceptosDIAN:
    """Mapea conceptos específicos según DIAN"""

    # Mapeo detallado de conceptos a categorías
    MAPEO_CONCEPTOS = {
        # RENTAS DE TRABAJO
        'Rentas de Trabajo': {
            'Salarios y Asimilados': [
                'salario', 'sueldo', 'compensación', 'jornal', 'emolumento',
                'pagos laborales', 'pagos por servicios personales'
            ],
            'Honorarios Profesionales': [
                'honorarios', 'profesional', 'consultor', 'asesor', 'expertise',
                'servicios profesionales', 'valor ingreso laboral prom'
            ],
            'Comisiones y Bonificaciones': [
                'comisión', 'comisiones', 'bonificación', 'bono', 'incentivo',
                'commission'
            ],
            'Prestaciones': [
                'vacaciones', 'prima', 'cesantías', 'aguinaldo', 'prestación',
                'aportes afe', 'ahorros obligatorios', 'fondo de ahorros',
                'aporte obligatorio fondos', 'aportes voluntarios'
            ],
        },

        # RENTAS DE CAPITAL
        'Rentas de Capital': {
            'Intereses y Rendimientos': [
                'interés', 'interest', 'rendimiento', 'cdt', 'certificado',
                'renta fija', 'valor total de los movimientos', 'cdt rendimientos',
                'saldo cdt', 'intereses de cesantías'
            ],
            'Dividendos': [
                'dividendo', 'dividend', 'utilidad', 'ganancias', 'distribución',
                'reparto de utilidades'
            ],
            'Arrendamiento': [
                'arrendamiento', 'rent', 'alquiler', 'lease', 'renta',
                'valor auxiliar catastral', 'saldo cuenta bancaria'
            ],
            'Ganancias de Capital': [
                'ganancia', 'capital gain', 'plusvalía', 'valorización',
                'venta de bienes'
            ],
        },

        # RENTAS NO LABORALES
        'Rentas No Laborales': {
            'Pensiones': [
                'pensión', 'pensioner', 'jubilación', 'retiro', 'pensionado',
                'asignación pensional'
            ],
            'Transferencias': [
                'transferencia', 'ayuda', 'subsidio', 'donación', 'herencia'
            ],
        }
    }

    def __init__(self, ruta_exogena):
        self.ruta_exogena = ruta_exogena
        self.df = None
        self.mapeo = {}

    def leer_exogena(self):
        """Lee el archivo completo"""
        try:
            self.df = pd.read_excel(self.ruta_exogena, sheet_name='Reporte', header=None)
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def clasificar_concepto(self, concepto):
        """Clasifica un concepto específico"""
        concepto_lower = str(concepto).lower().strip()

        for categoria_principal, subcategorias in self.MAPEO_CONCEPTOS.items():
            for subcategoria, palabras_clave in subcategorias.items():
                if any(palabra in concepto_lower for palabra in palabras_clave):
                    return categoria_principal, subcategoria

        return 'No Clasificado', 'Otros'

    def mapear_todos_conceptos(self):
        """Mapea TODOS los conceptos encontrados"""
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║         MAPEO DETALLADO DE CONCEPTOS - NORMA DIAN          ║")
        print("╚════════════════════════════════════════════════════════════╝\n")

        mapeo = {}
        conceptos_encontrados = []

        # Extraer datos del contribuyente
        datos_contrib = {
            'cedula': 'N/A',
            'nombre': 'N/A',
            'ano': 'N/A'
        }

        for i in range(len(self.df)):
            row = self.df.iloc[i]
            if pd.notna(row.iloc[0]):
                txt = str(row.iloc[0]).lower()
                if 'identificación' in txt or 'cédula' in txt:
                    if pd.notna(row.iloc[1]):
                        datos_contrib['cedula'] = str(row.iloc[1])
                elif 'nombre' in txt:
                    if pd.notna(row.iloc[1]):
                        datos_contrib['nombre'] = str(row.iloc[1])
                elif 'año' in txt:
                    if pd.notna(row.iloc[1]):
                        try:
                            datos_contrib['ano'] = int(row.iloc[1])
                        except:
                            pass

        # Buscar sección de INGRESOS (después de "INGRESOS BRUTOS")
        ingresos_iniciados = False
        for i in range(len(self.df)):
            row = self.df.iloc[i]

            # Detectar inicio de ingresos
            if pd.notna(row.iloc[0]) and 'ingreso' in str(row.iloc[0]).lower():
                ingresos_iniciados = True
                continue

            # Detectar fin de ingresos (cuando llega a "LIQUIDACIÓN")
            if pd.notna(row.iloc[0]) and 'liquidación' in str(row.iloc[0]).lower():
                ingresos_iniciados = False
                break

            # Procesar conceptos de ingresos
            if ingresos_iniciados and pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                concepto = str(row.iloc[0]).strip()
                try:
                    valor = float(row.iloc[1])
                    if valor > 0 and len(concepto) > 3:  # Evitar encabezados
                        categoria, subcategoria = self.clasificar_concepto(concepto)

                        if categoria not in mapeo:
                            mapeo[categoria] = {}
                        if subcategoria not in mapeo[categoria]:
                            mapeo[categoria][subcategoria] = {}

                        mapeo[categoria][subcategoria][concepto] = valor
                        conceptos_encontrados.append({
                            'concepto': concepto,
                            'valor': valor,
                            'categoria': categoria,
                            'subcategoria': subcategoria
                        })
                except (ValueError, TypeError):
                    pass

        self.mapeo = mapeo
        return {
            'contribuyente': datos_contrib,
            'mapeo': mapeo,
            'conceptos': conceptos_encontrados
        }

    def generar_reporte_detallado(self):
        """Genera reporte completo y detallado"""
        resultado = self.mapear_todos_conceptos()
        datos = resultado['contribuyente']
        mapeo = resultado['mapeo']
        conceptos = resultado['conceptos']

        print("\n📋 DATOS DEL CONTRIBUYENTE")
        print("─" * 70)
        print(f"  Cédula: {datos['cedula']}")
        print(f"  Nombre: {datos['nombre']}")
        print(f"  Año: {datos['ano']}")

        print("\n" + "=" * 70)
        print("📊 MAPEO DETALLADO POR CATEGORÍA")
        print("=" * 70)

        totales = {}

        for categoria, subcategorias in mapeo.items():
            print(f"\n{categoria.upper()}")
            print("─" * 70)

            total_categoria = 0
            for subcategoria, conceptos_dict in subcategorias.items():
                print(f"  {subcategoria}:")
                total_subcategoria = 0
                for concepto, valor in conceptos_dict.items():
                    print(f"    • {concepto}: ${valor:,.0f}")
                    total_subcategoria += valor
                    total_categoria += valor

                print(f"    Subtotal: ${total_subcategoria:,.0f}\n")

            totales[categoria] = total_categoria
            print(f"  TOTAL {categoria}: ${total_categoria:,.0f}\n")

        # Resumen final
        print("\n" + "=" * 70)
        print("📈 RESUMEN TOTAL")
        print("=" * 70)

        total_ingresos = sum(totales.values())
        for categoria, valor in totales.items():
            porcentaje = (valor / total_ingresos * 100) if total_ingresos > 0 else 0
            print(f"  {categoria}: ${valor:,.0f} ({porcentaje:.1f}%)")

        print(f"\n  TOTAL GENERAL: ${total_ingresos:,.0f}")

        print("\n✅ ANÁLISIS COMPLETADO")
        print(f"  • Conceptos procesados: {len(conceptos)}")
        print(f"  • Categorías identificadas: {len(mapeo)}")

        return {
            'datos': datos,
            'mapeo': mapeo,
            'conceptos': conceptos,
            'totales': totales,
            'total_ingresos': total_ingresos,
        }


if __name__ == "__main__":
    mapeador = MapeadorConceptosDIAN(
        "/Users/edison/Downloads/reporteExogena2024Elizabeth.xlsx"
    )
    if mapeador.leer_exogena():
        resultado = mapeador.generar_reporte_detallado()
