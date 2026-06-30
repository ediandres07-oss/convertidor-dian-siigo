#!/usr/bin/env python3
"""
Generador Formulario 210 v3
Copia el archivo base y solo modifica valores
Genera Excel idéntico al original
"""

import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
import shutil
import tempfile
import os
from pathlib import Path
from datetime import datetime

def procesar_exogena(exogena_path):
    """Lee y agrupa datos de Exógena"""
    print("Leyendo Exógena...")
    df = pd.read_excel(exogena_path, sheet_name="Reporte", header=13)
    df.columns = df.columns.str.strip()
    df["Valor"] = pd.to_numeric(df["Valor"], errors="coerce")
    df = df.dropna(subset=["Valor"])

    print(f"✓ {len(df)} registros leídos")
    print(f"✓ {len(df['Uso declaración Sugerida'].unique())} categorías")

    return df

def generar_formulario_210(archivo_base, archivo_salida, df_exogena):
    """Copia archivo base y modifica solo los valores"""

    print("\nProcesando archivo base...")

    # Copiar archivo
    shutil.copy(archivo_base, archivo_salida)

    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()

    try:
        # Extraer copia
        with zipfile.ZipFile(archivo_salida, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Modificar Formulario 210 (sheet4.xml) - donde están los valores principales
        print("Llenando Formulario 210...")
        sheet4_path = os.path.join(temp_dir, 'xl', 'worksheets', 'sheet4.xml')
        llenar_formulario_210(sheet4_path, df_exogena)

        # Reempacar
        print("Reempacando archivo...")
        with zipfile.ZipFile(archivo_salida, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        print(f"✓ Archivo Excel generado: {archivo_salida}")
        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def llenar_formulario_210(sheet_path, df_exogena):
    """Llena Formulario 210 con los valores"""
    tree = ET.parse(sheet_path)
    root = tree.getroot()

    ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    # Mapeos
    mapeos = {
        "R132 Retenciones año gravable a declarar": "AZ30",
        "Tope 2. Patrimonio | R29 Patrimonio bruto": "AZ40",
        "Tope 2. Patrimonio bruto | R29 Patrimonio bruto": "P25",
        "Tope 2. Patrimonio| R29 Patrimonio bruto": "AD25",
        "TOPE 4. Consignaciones e inversiones": "K44",
        "Tope 1: ingresos brutos | R32 Ingresos brutos por rentas de trabajo (art. 103 E.T.)": "K25",
        "Tope 1: ingresos brutos | R58 Ingresos brutos por rentas de capital | R59 Ingresos no constitutivos  por rentas de capital": "AX47",
    }

    # Agrupar datos
    datos = df_exogena.groupby("Uso declaración Sugerida")["Valor"].sum().to_dict()

    # Buscar y modificar celdas existentes
    for categoria, celda_ref in mapeos.items():
        if categoria not in datos:
            continue

        valor = int(datos[categoria])

        # Buscar la celda en el XML
        encontrado = False
        for row in root.findall('.//ss:row', ns):
            for cell in row.findall('ss:c', ns):
                if cell.get('r') == celda_ref:
                    # Encontrar o crear elemento 'v'
                    v_elem = cell.find('ss:v', ns)
                    if v_elem is None:
                        v_elem = ET.Element('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
                        cell.append(v_elem)

                    v_elem.text = str(valor)
                    encontrado = True
                    print(f"  ✓ {celda_ref} = ${valor:,}")
                    break

            if encontrado:
                break

    tree.write(sheet_path, encoding='UTF-8', xml_declaration=True)

if __name__ == "__main__":
    print("="*80)
    print("GENERADOR: Formulario 210 v3 (Excel solamente)")
    print("="*80 + "\n")

    # Configuración
    EXOGENA = "/Users/edison/Downloads/reporteExogena2024Elizabeth.xlsx"
    FORMULARIO_BASE = "/Users/edison/Downloads/VA23-Formulario-210-AG2022-PN-SIMONVELASQUEZ.xlsx"
    TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
    SALIDA_EXCEL = f"/Users/edison/Desktop/Formulario210_{TIMESTAMP}.xlsx"

    # Verificar archivos
    if not Path(EXOGENA).exists():
        print(f"❌ Exógena no encontrada")
        exit(1)

    if not Path(FORMULARIO_BASE).exists():
        print(f"❌ Formulario 210 base no encontrado")
        exit(1)

    # Procesar
    df = procesar_exogena(EXOGENA)
    generar_formulario_210(FORMULARIO_BASE, SALIDA_EXCEL, df)

    print("\n" + "="*80)
    print("✅ GENERACIÓN COMPLETADA")
    print("="*80)
    print(f"\n📄 Excel:  {SALIDA_EXCEL}")
    print(f"\n💡 Abre el archivo:")
    print(f"   {SALIDA_EXCEL}\n")
