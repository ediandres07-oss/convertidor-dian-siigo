#!/usr/bin/env python3
"""
Liquidador de Renta v2 - Con UVT 2025 y modificación de valores
"""

import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
import json

class LiquidadorRentaV2:
    """Liquidador interactivo con UVT 2025"""

    # UVT actualizado 2025
    UVT_2025 = 49799

    RANGOS_IRPF_2025 = [
        (0, 66950000, 0),
        (66950000, 134900000, 0.05),
        (134900000, 404700000, 0.12),
        (404700000, 673500000, 0.25),
        (673500000, 1347000000, 0.32),
        (1347000000, float('inf'), 0.37),
    ]

    def __init__(self, ruta_exogena, ruta_formulario):
        self.ruta_exogena = ruta_exogena
        self.ruta_formulario = ruta_formulario
        self.datos = {}
        self.parametros = {
            'deduccion_pct': 10,
            'ano_gravable': 2024
        }

    def extraer_exogena(self):
        """Extrae datos de la exógena"""
        df = pd.read_excel(self.ruta_exogena, sheet_name='Reporte', header=None)

        # Datos del contribuyente
        for i in range(len(df)):
            row = df.iloc[i]
            if pd.notna(row.iloc[0]):
                txt = str(row.iloc[0]).lower()
                if 'identificación:' in txt and pd.notna(row.iloc[2]):
                    self.datos['cedula'] = str(row.iloc[2])
                elif 'nombres' in txt and pd.notna(row.iloc[2]):
                    self.datos['nombre'] = str(row.iloc[2])
                elif 'año' in txt and 'refiere' in txt and pd.notna(row.iloc[2]):
                    self.datos['ano'] = int(row.iloc[2])

        # Ingresos y retenciones
        self.datos['ingresos'] = {}
        self.datos['retenciones'] = {}

        for i in range(14, len(df)):
            row = df.iloc[i]
            if pd.notna(row.iloc[4]) and pd.notna(row.iloc[5]):
                concepto = str(row.iloc[4]).strip()
                try:
                    valor = float(row.iloc[5])
                    if valor > 0:
                        uso = str(row.iloc[6]).lower() if pd.notna(row.iloc[6]) else ""

                        if 'retención' in uso or 'r132' in uso or 'cdt retención' in concepto.lower():
                            if concepto not in self.datos['retenciones']:
                                self.datos['retenciones'][concepto] = 0
                            self.datos['retenciones'][concepto] += valor
                        else:
                            if concepto not in self.datos['ingresos']:
                                self.datos['ingresos'][concepto] = 0
                            self.datos['ingresos'][concepto] += valor
                except:
                    pass

        self.datos['total_ingresos'] = sum(self.datos['ingresos'].values())
        self.datos['total_retenciones'] = sum(self.datos['retenciones'].values())

        return self.datos

    def mostrar_resumen_exogena(self):
        """Muestra resumen de exógena"""
        print("\n╔════════════════════════════════════════════════════════════╗")
        print("║         LIQUIDADOR DE RENTA - UVT 2025 ($49.799)          ║")
        print("╚════════════════════════════════════════════════════════════╝\n")

        print("📋 DATOS DEL CONTRIBUYENTE")
        print("─" * 70)
        print(f"  Cédula:        {self.datos.get('cedula')}")
        print(f"  Nombre:        {self.datos.get('nombre')}")
        print(f"  Año Gravable:  {self.datos.get('ano')}")

        print("\n💰 INGRESOS DETECTADOS")
        print("─" * 70)
        total = 0
        for concepto, valor in sorted(self.datos['ingresos'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {concepto[:50]:50s} ${valor:>15,.0f}")
            total += valor

        if len(self.datos['ingresos']) > 10:
            print(f"  ... +{len(self.datos['ingresos']) - 10} conceptos más")
            total = self.datos.get('total_ingresos', 0)

        print(f"  {'─' * 70}")
        print(f"  TOTAL INGRESOS:                          ${self.datos.get('total_ingresos', 0):>15,.0f}")

        print("\n📌 RETENCIONES")
        print("─" * 70)
        for concepto, valor in self.datos['retenciones'].items():
            print(f"  • {concepto[:50]:50s} ${valor:>15,.0f}")
        print(f"  {'─' * 70}")
        print(f"  TOTAL RETENCIONES:                       ${self.datos.get('total_retenciones', 0):>15,.0f}")

    def permitir_modificaciones(self):
        """Permite al usuario modificar valores"""
        print("\n\n⚙️  PARÁMETROS DE LIQUIDACIÓN")
        print("─" * 70)
        print(f"\n1. Porcentaje de Deducción (actual: {self.parametros['deduccion_pct']}%)")
        print("   • Empleados: 10%")
        print("   • Independientes: 10-20% (con gastos comprobados)")

        while True:
            try:
                deduccion = input(f"\n   Ingresa % de deducción (Enter para {self.parametros['deduccion_pct']}%): ").strip()
                if deduccion == "":
                    break
                deduccion = float(deduccion)
                if 0 <= deduccion <= 100:
                    self.parametros['deduccion_pct'] = deduccion
                    break
                else:
                    print("   ❌ Ingresa un valor entre 0 y 100")
            except ValueError:
                print("   ❌ Valor inválido")

        print(f"\n2. Retenciones (actual: ${self.datos.get('total_retenciones', 0):,.0f})")
        print("   • Comprueba con FORMUL-2649")

        while True:
            try:
                retenciones = input(f"\n   Ingresa valor de retenciones (Enter para ${self.datos.get('total_retenciones', 0):,.0f}): ").strip()
                if retenciones == "":
                    break
                retenciones = float(retenciones)
                if retenciones >= 0:
                    self.datos['total_retenciones'] = retenciones
                    break
                else:
                    print("   ❌ Ingresa un valor positivo")
            except ValueError:
                print("   ❌ Valor inválido")

        print(f"\n3. Ingresos Brutos (actual: ${self.datos.get('total_ingresos', 0):,.0f})")

        while True:
            try:
                ingresos = input(f"\n   Ingresa total ingresos (Enter para ${self.datos.get('total_ingresos', 0):,.0f}): ").strip()
                if ingresos == "":
                    break
                ingresos = float(ingresos)
                if ingresos >= 0:
                    self.datos['total_ingresos'] = ingresos
                    break
                else:
                    print("   ❌ Ingresa un valor positivo")
            except ValueError:
                print("   ❌ Valor inválido")

    def calcular_irpf(self, base):
        """Calcula IRPF progresivo"""
        irpf = 0
        detalles = []

        for inicio, fin, tasa in self.RANGOS_IRPF_2025:
            if base > inicio:
                tramo = min(base, fin) - inicio
                impuesto_tramo = tramo * tasa
                irpf += impuesto_tramo
                if impuesto_tramo > 0:
                    detalles.append({
                        'rango': f'${inicio:,.0f} - ${fin:,.0f}',
                        'tasa': f'{tasa*100:.0f}%',
                        'base': tramo,
                        'impuesto': impuesto_tramo
                    })

        return irpf, detalles

    def calcular_aporte_solidario(self, base):
        """Calcula aporte solidario (1% > 16.000 UVT)"""
        limite = 16000 * self.UVT_2025
        if base > limite:
            return (base - limite) * 0.01
        return 0

    def liquidar(self):
        """Realiza liquidación completa"""
        print("\n\n🧮 LIQUIDACIÓN TRIBUTARIA")
        print("═" * 70)

        total_ingresos = self.datos.get('total_ingresos', 0)
        deduccion = total_ingresos * (self.parametros['deduccion_pct'] / 100)
        base_liquida = total_ingresos - deduccion

        # IRPF
        irpf, detalles_irpf = self.calcular_irpf(base_liquida)

        # Aporte solidario
        aporte_solidario = self.calcular_aporte_solidario(base_liquida)

        # Total impuesto
        total_impuesto = irpf + aporte_solidario

        # Retenciones
        retenciones = self.datos.get('total_retenciones', 0)

        # Saldo
        saldo = max(0, total_impuesto - retenciones)
        acreencia = max(0, retenciones - total_impuesto)

        # Mostrar cálculos paso a paso
        print("\n1️⃣  INGRESOS Y DEDUCCIONES")
        print("─" * 70)
        print(f"   Ingresos Brutos:              ${total_ingresos:>20,.0f}")
        print(f"   Deducción ({self.parametros['deduccion_pct']}%):                  ${deduccion:>20,.0f}")
        print(f"   {'─' * 70}")
        print(f"   BASE LÍQUIDA:                 ${base_liquida:>20,.0f}")

        print("\n2️⃣  CÁLCULO IRPF (Tarifa Progresiva 2025)")
        print("─" * 70)
        for detalle in detalles_irpf:
            print(f"   {detalle['rango']:30s} @ {detalle['tasa']:>4s} = ${detalle['impuesto']:>15,.0f}")
        print(f"   {'─' * 70}")
        print(f"   IRPF TOTAL:                   ${irpf:>20,.0f}")

        print("\n3️⃣  APORTE SOLIDARIO")
        print("─" * 70)
        limite_uvt = 16000 * self.UVT_2025
        print(f"   Límite (16.000 UVT × $49.799): ${limite_uvt:>15,.0f}")
        if aporte_solidario > 0:
            print(f"   Excedente:                    ${base_liquida - limite_uvt:>20,.0f}")
            print(f"   Aporte (1%):                  ${aporte_solidario:>20,.0f}")
        else:
            print(f"   ℹ️  No aplica (base < 16.000 UVT)")
        print(f"   {'─' * 70}")

        print("\n4️⃣  RESUMEN DE LIQUIDACIÓN")
        print("═" * 70)
        print(f"   IRPF:                         ${irpf:>20,.0f}")
        print(f"   Aporte Solidario:             ${aporte_solidario:>20,.0f}")
        print(f"   ────────────────────────────────────────")
        print(f"   TOTAL IMPUESTO:               ${total_impuesto:>20,.0f}")
        print(f"   Menos Retenciones:            ${retenciones:>20,.0f}")
        print(f"   ════════════════════════════════════════")

        if saldo > 0:
            print(f"   ✅ SALDO A PAGAR:             ${saldo:>20,.0f}")
        else:
            print(f"   💰 ACREENCIA (Saldo a favor):  ${acreencia:>20,.0f}")

        print("\n5️⃣  INDICADORES")
        print("─" * 70)
        tasa_irpf = (irpf / base_liquida * 100) if base_liquida > 0 else 0
        tasa_total = (total_impuesto / total_ingresos * 100) if total_ingresos > 0 else 0
        print(f"   Tasa IRPF:                    {tasa_irpf:>20.2f}%")
        print(f"   Carga Total Tributaria:       {tasa_total:>20.2f}%")
        print(f"   Número de UVT (Base/UVT):     {base_liquida/self.UVT_2025:>20,.0f}")

        self.datos['calculos'] = {
            'total_ingresos': total_ingresos,
            'deduccion': deduccion,
            'deduccion_pct': self.parametros['deduccion_pct'],
            'base_liquida': base_liquida,
            'irpf': irpf,
            'aporte_solidario': aporte_solidario,
            'total_impuesto': total_impuesto,
            'retenciones': retenciones,
            'saldo_pagar': saldo,
            'acreencia': acreencia,
            'uvt_2025': self.UVT_2025,
        }

        return self.datos['calculos']

    def guardar_resultados(self, ruta_salida=None):
        """Guarda resultados en JSON"""
        if not ruta_salida:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cedula = self.datos.get('cedula', 'XXX')
            ruta_salida = f"liquidacion_{cedula}_{timestamp}.json"

        resultado = {
            'contribuyente': {
                'cedula': self.datos.get('cedula'),
                'nombre': self.datos.get('nombre'),
                'ano_gravable': self.datos.get('ano'),
            },
            'parametros': self.parametros,
            'calculos': self.datos.get('calculos', {}),
            'fecha_generacion': datetime.now().isoformat(),
            'uvt_2025': self.UVT_2025,
        }

        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False, default=str)

        return ruta_salida

    def procesar_completo(self):
        """Proceso completo interactivo"""
        # Extraer
        self.extraer_exogena()
        self.mostrar_resumen_exogena()

        # Permitir modificaciones
        self.permitir_modificaciones()

        # Liquidar
        self.liquidar()

        # Guardar
        print("\n\n📄 Guardando resultados...")
        ruta = self.guardar_resultados()
        print(f"✅ Guardado en: {ruta}")

        print("\n" + "=" * 70)
        print("✅ LIQUIDACIÓN COMPLETADA")
        print("=" * 70)
        print("\n⚠️  PRÓXIMOS PASOS:")
        print("  1. Valida con tu contador")
        print("  2. Comprueba retenciones (FORMUL-2649)")
        print("  3. Revisa clasificación de ingresos")
        print("  4. Presenta a DIAN antes del 10 de abril 2025")

if __name__ == "__main__":
    liquidador = LiquidadorRentaV2(
        ruta_exogena="/Users/edison/Downloads/reporteExogena2024Elizabeth.xlsx",
        ruta_formulario="/Users/edison/Downloads/formulario 210.xlsx"
    )

    liquidador.procesar_completo()
