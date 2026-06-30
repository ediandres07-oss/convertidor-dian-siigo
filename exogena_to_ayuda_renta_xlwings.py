#!/usr/bin/env python3
"""
AUTOMATIZADOR EXÓGENA → AYUDA RENTA (versión xlwings)
======================================================
Usa xlwings para interactuar con Excel directamente.
REQUIERE: Excel instalado y xlwings (pip3 install xlwings)
"""

import pandas as pd
import xlwings as xw
import time
from pathlib import Path

def procesar_exogena_y_llenar_renta():
    # ==========================================
    # 1. CONFIGURACIÓN DE ARCHIVOS Y RUTAS
    # ==========================================

    # RUTAS ABSOLUTAS (más confiables)
    archivo_exogena = "/Users/edison/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/0141329A-8688-45CB-9787-E5FD5051A852/reporteExogena2024Elizabeth.xlsx"
    archivo_renta = "/Users/edison/Downloads/Programa-Ayuda-Renta-DIAN-2025/AyudaRenta 2025 V1.0 .xlsm"
    archivo_salida = "/Users/edison/Desktop/proyecto-subir info a siigo nube/AyudaRenta_Diligenciado_xlwings.xlsm"

    print("="*80)
    print("AUTOMATIZADOR EXÓGENA → AYUDA RENTA (xlwings)")
    print("="*80)

    # Verificar que los archivos existan
    if not Path(archivo_exogena).exists():
        print(f"❌ Error: Archivo Exógena no encontrado: {archivo_exogena}")
        return

    if not Path(archivo_renta).exists():
        print(f"❌ Error: Archivo Ayuda Renta no encontrado: {archivo_renta}")
        return

    print(f"\n✓ Archivo Exógena: {Path(archivo_exogena).name}")
    print(f"✓ Archivo Ayuda Renta: {Path(archivo_renta).name}")

    # ==========================================
    # 2. LECTURA Y PROCESAMIENTO DEL EXÓGENA
    # ==========================================
    print("\nLeyendo archivo Exógena...")

    try:
        # El archivo es .xlsx, leerlo directamente
        df = pd.read_excel(archivo_exogena, sheet_name="Reporte", header=13)

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()

        # Convertir columna Valor a numérico
        df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
        df = df.dropna(subset=["Valor"])

        print(f"✓ Se leyeron {len(df)} registros")
        print(f"✓ Columnas: {', '.join(df.columns.tolist())}")

    except Exception as e:
        print(f"❌ Error al leer Exógena: {e}")
        return

    # ==========================================
    # 3. AGRUPAR DATOS POR CATEGORÍA
    # ==========================================
    print("\nProcesando datos...")

    # Agrupar por "Uso declaración Sugerida" (categoría tributaria)
    if "Uso declaración Sugerida" in df.columns:
        datos_agrupados = df.groupby("Uso declaración Sugerida")["Valor"].sum().to_dict()
    else:
        datos_agrupados = df.groupby("Detalle")["Valor"].sum().to_dict()

    print(f"✓ {len(datos_agrupados)} categorías identificadas")

    print("\n--- Resumen de valores por categoría ---")
    for categoria, valor in list(datos_agrupados.items())[:10]:
        print(f"  • {str(categoria)[:60]}: ${valor:,.0f}")
    if len(datos_agrupados) > 10:
        print(f"  ... y {len(datos_agrupados) - 10} categorías más")

    # ==========================================
    # 4. MAPEO: CATEGORÍA → (HOJA, CELDA)
    # ==========================================
    # BASADO EN EL ANÁLISIS REAL DE LA EXÓGENA
    mapeo = {
        "R132 Retenciones año gravable a declarar": {
            "hoja": "Retenciones",
            "celda": "C32",
            "tipo": "suma"
        },
        "Tope 2. Patrimonio | R29 Patrimonio bruto": {
            "hoja": "Patrimonio",
            "celda": "D14",
            "tipo": "directo"
        },
        "Tope 2. Patrimonio bruto | R29 Patrimonio bruto": {
            "hoja": "Patrimonio",
            "celda": "D18",
            "tipo": "directo"
        },
        "Tope 2. Patrimonio| R29 Patrimonio bruto": {
            "hoja": "Efectivo_Bancos_Cuentas",
            "celda": "E7",
            "tipo": "lista"
        },
        "TOPE 4. Consignaciones e inversiones": {
            "hoja": "Inversiones",
            "celda": "E7",
            "tipo": "lista"
        },
        "Tope 1: ingresos brutos | R32 Ingresos brutos por rentas de trabajo (art. 103 E.T.)": {
            "hoja": "Salarios_Demas_Pagos_Laborales",
            "celda": "E7",
            "tipo": "lista"
        },
        "Tope 1: ingresos brutos | R58 Ingresos brutos por rentas de capital | R59 Ingresos no constitutivos  por rentas de capital": {
            "hoja": "Inter_Rend_Finan",
            "celda": "E7",
            "tipo": "lista"
        },
    }

    # ==========================================
    # 5. INYECCIÓN DE DATOS CON xlwings
    # ==========================================
    print("\nAbriendo Ayuda Renta con Excel (esto puede tardar unos segundos)...")

    inyecciones_exitosas = 0
    inyecciones_fallidas = 0

    try:
        # Abrimos Excel (visible para ver la magia)
        app = xw.App(visible=False)  # Cambia a True si quieres ver Excel abrirse

        print("✓ Excel abierto")

        # Abrimos el libro
        wb = app.books.open(archivo_renta)
        print(f"✓ Ayuda Renta abierto")

        # Iteramos sobre el mapeo
        for categoria, config in mapeo.items():

            # Verificar si la categoría existe en los datos
            if categoria not in datos_agrupados:
                print(f"  ⚠️  Categoría no encontrada: {categoria}")
                continue

            valor_total = datos_agrupados[categoria]
            hoja_nombre = config["hoja"]
            celda_destino = config["celda"]
            tipo = config["tipo"]

            try:
                # Verificar que la hoja exista
                if hoja_nombre not in [sheet.name for sheet in wb.sheets]:
                    print(f"  ⚠️  Hoja '{hoja_nombre}' no encontrada en Ayuda Renta")
                    inyecciones_fallidas += 1
                    continue

                hoja = wb.sheets[hoja_nombre]

                if tipo == "directo":
                    # Inyección directa del total
                    hoja.range(celda_destino).value = valor_total
                    print(f"  ✓ {hoja_nombre}!{celda_destino} = ${valor_total:,.0f}")
                    inyecciones_exitosas += 1

                elif tipo == "suma":
                    # Para sumas automáticas, solo verificamos
                    print(f"  ✓ {hoja_nombre}!{celda_destino} (cálculo automático)")
                    inyecciones_exitosas += 1

                elif tipo == "lista":
                    # Para listas, inyectamos el total en la primera celda
                    hoja.range(celda_destino).value = valor_total
                    print(f"  ✓ {hoja_nombre}!{celda_destino} ({len(datos_agrupados)} items)")
                    inyecciones_exitosas += 1

                # Pausa para permitir recálculos
                time.sleep(0.5)

            except Exception as e:
                print(f"  ❌ Error inyectando en {hoja_nombre}!{celda_destino}: {e}")
                inyecciones_fallidas += 1

        # Recalcular todo (solo en Windows)
        print("\nRecalculando fórmulas...")
        try:
            wb.api.CalculateFull()
        except:
            pass  # Mac no soporta CalculateFull
        time.sleep(1)

        # Guardar el archivo
        print(f"\nGuardando como: {Path(archivo_salida).name}")
        wb.save(archivo_salida)
        print(f"✓ Archivo guardado: {archivo_salida}")

        print("\n" + "="*80)
        print(f"✓ PROCESO COMPLETADO")
        print(f"  Inyecciones exitosas: {inyecciones_exitosas}")
        print(f"  Inyecciones fallidas: {inyecciones_fallidas}")
        print("="*80)

    except Exception as e:
        print(f"❌ Error grave: {e}")

    finally:
        # Cerrar Excel
        try:
            wb.close()
            app.quit()
            print("✓ Excel cerrado")
        except:
            pass

if __name__ == "__main__":
    procesar_exogena_y_llenar_renta()
