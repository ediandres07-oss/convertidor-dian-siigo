#!/usr/bin/env python3
"""
Analizador Completo de Exógena - Norma DIAN Colombia
Mapea y verifica rentas según clasificación oficial
"""

import pandas as pd
from datetime import datetime

class AnalizadorExogenaDIAN:
    """Analiza y mapea Exógena según norma DIAN"""

    # Clasificación de rentas según DIAN
    RENTAS_TRABAJO = {
        'Salarios': ['salario', 'sueldo', 'compensación', 'bonificación'],
        'Honorarios': ['honorario', 'profesional', 'consultor', 'asesor'],
        'Comisiones': ['comisión', 'commission'],
        'Prestaciones': ['vacaciones', 'prima', 'cesantías'],
    }

    RENTAS_CAPITAL = {
        'Intereses': ['interés', 'interest', 'rendimiento', 'cdt'],
        'Dividendos': ['dividendo', 'dividend', 'utilidad'],
        'Ganancias': ['ganancia', 'capital gain', 'plusvalía'],
        'Arrendamiento': ['arrendamiento', 'rent', 'alquiler'],
    }

    RENTAS_NO_LABORALES = {
        'Pensiones': ['pensión', 'pensioner', 'jubilación'],
        'Transferencias': ['transferencia', 'ayuda', 'subsidio'],
        'Otros': ['otro', 'miscelaneous'],
    }

    def __init__(self, ruta_exogena):
        self.ruta_exogena = ruta_exogena
        self.df = None
        self.analisis = {}

    def leer_exogena(self):
        """Lee y procesa el archivo de Exógena"""
        try:
            self.df = pd.read_excel(self.ruta_exogena, sheet_name='Reporte', header=None)
            return True
        except Exception as e:
            print(f"Error leyendo Exógena: {e}")
            return False

    def clasificar_renta(self, concepto):
        """Clasifica una renta según su tipo"""
        concepto_lower = str(concepto).lower()

        # Verificar Rentas de Trabajo
        for tipo, palabras_clave in self.RENTAS_TRABAJO.items():
            if any(palabra in concepto_lower for palabra in palabras_clave):
                return 'Rentas de Trabajo', tipo

        # Verificar Rentas de Capital
        for tipo, palabras_clave in self.RENTAS_CAPITAL.items():
            if any(palabra in concepto_lower for palabra in palabras_clave):
                return 'Rentas de Capital', tipo

        # Verificar Rentas No Laborales
        for tipo, palabras_clave in self.RENTAS_NO_LABORALES.items():
            if any(palabra in concepto_lower for palabra in palabras_clave):
                return 'Rentas No Laborales', tipo

        return 'Otros', 'Sin clasificar'

    def extraer_datos_completos(self):
        """Extrae y clasifica todos los datos del archivo"""
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║        ANÁLISIS COMPLETO DE EXÓGENA - NORMA DIAN           ║")
        print("╚════════════════════════════════════════════════════════════╝\n")

        datos = {
            'contribuyente': {},
            'rentas_trabajo': {},
            'rentas_capital': {},
            'rentas_no_laborales': {},
            'otros': {},
            'retenciones': {},
            'patrimonio': {},
            'cuentas_por_pagar': {},
        }

        # Extraer datos del contribuyente (primeras filas)
        for i in range(len(self.df)):
            row = self.df.iloc[i]
            if pd.notna(row.iloc[0]):
                txt = str(row.iloc[0]).lower()
                if 'identificación:' in txt and pd.notna(row.iloc[2]):
                    datos['contribuyente']['cedula'] = str(row.iloc[2])
                elif 'nombres' in txt and pd.notna(row.iloc[2]):
                    datos['contribuyente']['nombre'] = str(row.iloc[2])
                elif 'año' in txt and 'refiere' in txt and pd.notna(row.iloc[2]):
                    datos['contribuyente']['ano'] = int(row.iloc[2])
                elif 'patrimonio' in txt and pd.notna(row.iloc[2]):
                    try:
                        datos['patrimonio']['total'] = float(row.iloc[2])
                    except:
                        pass

        # Extraer ingresos y clasificarlos (desde fila 14)
        for i in range(14, len(self.df)):
            row = self.df.iloc[i]
            if pd.notna(row.iloc[4]) and pd.notna(row.iloc[5]):
                concepto = str(row.iloc[4]).strip()
                try:
                    valor = float(row.iloc[5])
                    if valor > 0:
                        uso = str(row.iloc[6]).lower() if pd.notna(row.iloc[6]) else ""

                        # Clasificar retenciones
                        if 'retención' in uso or 'r132' in uso or 'cdt retención' in concepto.lower():
                            if concepto not in datos['retenciones']:
                                datos['retenciones'][concepto] = 0
                            datos['retenciones'][concepto] += valor
                        else:
                            # Clasificar por tipo de renta
                            tipo_renta, subtipo = self.clasificar_renta(concepto)

                            if tipo_renta == 'Rentas de Trabajo':
                                if subtipo not in datos['rentas_trabajo']:
                                    datos['rentas_trabajo'][subtipo] = {}
                                if concepto not in datos['rentas_trabajo'][subtipo]:
                                    datos['rentas_trabajo'][subtipo][concepto] = 0
                                datos['rentas_trabajo'][subtipo][concepto] += valor

                            elif tipo_renta == 'Rentas de Capital':
                                if subtipo not in datos['rentas_capital']:
                                    datos['rentas_capital'][subtipo] = {}
                                if concepto not in datos['rentas_capital'][subtipo]:
                                    datos['rentas_capital'][subtipo][concepto] = 0
                                datos['rentas_capital'][subtipo][concepto] += valor

                            elif tipo_renta == 'Rentas No Laborales':
                                if subtipo not in datos['rentas_no_laborales']:
                                    datos['rentas_no_laborales'][subtipo] = {}
                                if concepto not in datos['rentas_no_laborales'][subtipo]:
                                    datos['rentas_no_laborales'][subtipo][concepto] = 0
                                datos['rentas_no_laborales'][subtipo][concepto] += valor

                            else:
                                if concepto not in datos['otros']:
                                    datos['otros'][concepto] = 0
                                datos['otros'][concepto] += valor

                except (ValueError, TypeError):
                    pass

        self.analisis = datos
        return datos

    def mostrar_resumen(self):
        """Muestra resumen detallado del análisis"""
        datos = self.analisis

        print("\n📋 DATOS DEL CONTRIBUYENTE")
        print("─" * 70)
        print(f"  Cédula: {datos['contribuyente'].get('cedula', 'N/A')}")
        print(f"  Nombre: {datos['contribuyente'].get('nombre', 'N/A')}")
        print(f"  Año: {datos['contribuyente'].get('ano', 'N/A')}")

        # Rentas de Trabajo
        print("\n💼 RENTAS DE TRABAJO")
        print("─" * 70)
        total_trabajo = 0
        for subtipo, conceptos in datos['rentas_trabajo'].items():
            print(f"  {subtipo}:")
            for concepto, valor in conceptos.items():
                print(f"    • {concepto}: ${valor:,.0f}")
                total_trabajo += valor
        if total_trabajo > 0:
            print(f"  SUBTOTAL: ${total_trabajo:,.0f}")
        else:
            print("  ℹ️  Sin rentas de trabajo reportadas")

        # Rentas de Capital
        print("\n💰 RENTAS DE CAPITAL")
        print("─" * 70)
        total_capital = 0
        for subtipo, conceptos in datos['rentas_capital'].items():
            print(f"  {subtipo}:")
            for concepto, valor in conceptos.items():
                print(f"    • {concepto}: ${valor:,.0f}")
                total_capital += valor
        if total_capital > 0:
            print(f"  SUBTOTAL: ${total_capital:,.0f}")
        else:
            print("  ℹ️  Sin rentas de capital reportadas")

        # Rentas No Laborales
        print("\n🏥 RENTAS NO LABORALES")
        print("─" * 70)
        total_no_labor = 0
        for subtipo, conceptos in datos['rentas_no_laborales'].items():
            print(f"  {subtipo}:")
            for concepto, valor in conceptos.items():
                print(f"    • {concepto}: ${valor:,.0f}")
                total_no_labor += valor
        if total_no_labor > 0:
            print(f"  SUBTOTAL: ${total_no_labor:,.0f}")
        else:
            print("  ℹ️  Sin rentas no laborales reportadas")

        # Retenciones
        print("\n🔐 RETENCIONES EN LA FUENTE")
        print("─" * 70)
        total_retenciones = 0
        for concepto, valor in datos['retenciones'].items():
            print(f"  • {concepto}: ${valor:,.0f}")
            total_retenciones += valor
        print(f"  TOTAL RETENCIONES: ${total_retenciones:,.0f}")

        # Patrimonio
        if datos['patrimonio'].get('total', 0) > 0:
            print("\n🏠 PATRIMONIO")
            print("─" * 70)
            print(f"  Total Patrimonio Bruto: ${datos['patrimonio'].get('total', 0):,.0f}")

        # Totales generales
        print("\n" + "=" * 70)
        print("📊 TOTALES GENERALES")
        print("=" * 70)
        total_ingresos = total_trabajo + total_capital + total_no_labor
        print(f"  Total Ingresos: ${total_ingresos:,.0f}")
        print(f"  Total Retenciones: ${total_retenciones:,.0f}")
        print(f"  Base para Liquidación: ${total_ingresos:,.0f}")

        return {
            'total_trabajo': total_trabajo,
            'total_capital': total_capital,
            'total_no_labor': total_no_labor,
            'total_retenciones': total_retenciones,
            'total_ingresos': total_ingresos,
        }

    def generar_reporte(self):
        """Genera reporte completo"""
        if not self.leer_exogena():
            return None

        self.extraer_datos_completos()
        totales = self.mostrar_resumen()

        print("\n✅ ANÁLISIS COMPLETADO")
        print("=" * 70)

        return {
            'datos': self.analisis,
            'totales': totales,
            'timestamp': datetime.now().isoformat(),
        }


if __name__ == "__main__":
    analizador = AnalizadorExogenaDIAN(
        "/Users/edison/Downloads/reporteExogena2024Elizabeth.xlsx"
    )
    resultado = analizador.generar_reporte()
