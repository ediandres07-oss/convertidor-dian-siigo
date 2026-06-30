#!/usr/bin/env python3
"""
APP WEB - Liquidador de Formulario 210
Interfaz Streamlit para mapear Exógena y generar liquidaciones tributarias
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from liquidador_renta import Formulario210Liquidador, procesar_liquidacion
from llenar_formulario_210_completo_dian import LlenadorFormulario210CompletoDIAN
import json
from datetime import datetime
import os
import shutil

st.set_page_config(
    page_title="Liquidador Formulario 210",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Liquidador de Formulario 210 - DIAN")
st.markdown("**Mapeo de Exógena y Cálculo de Liquidaciones Tributarias Colombianas**")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📁 Cargar Archivos",
    "🔗 Mapear Datos",
    "💰 Liquidación",
    "📈 Resultados"
])

# Estado de sesión
if 'liquidador' not in st.session_state:
    st.session_state.liquidador = None
if 'datos_mapeados' not in st.session_state:
    st.session_state.datos_mapeados = False
if 'liquidacion_completa' not in st.session_state:
    st.session_state.liquidacion_completa = None

# ============================================================
# TAB 1: CARGAR ARCHIVOS
# ============================================================
with tab1:
    st.header("📁 Cargar Archivos")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Reporte Exógena")
        st.info("Archivo con información reportada por terceros (bancos, empleadores, etc.)")
        archivo_exogena = st.file_uploader(
            "Selecciona archivo Exógena",
            type=["xlsx", "xls"],
            key="exogena"
        )

    with col2:
        st.subheader("📝 Formulario 210 Base")
        st.info("Plantilla del formulario 210 a llenar")
        archivo_210 = st.file_uploader(
            "Selecciona Formulario 210 base (opcional)",
            type=["xlsx", "xls"],
            key="formulario"
        )

    if archivo_exogena:
        with st.spinner("Leyendo archivo de Exógena..."):
            # Guardar archivo temporal
            temp_exogena = f"/tmp/exogena_{datetime.now().timestamp()}.xlsx"
            with open(temp_exogena, "wb") as f:
                f.write(archivo_exogena.getbuffer())

            # Crear liquidador
            ano_gravable = st.number_input("Año Gravable", value=2024, min_value=2020, max_value=2025)
            st.session_state.liquidador = Formulario210Liquidador(ano_gravable)

            if st.session_state.liquidador.leer_exogena(temp_exogena):
                st.success("✅ Archivo de Exógena cargado correctamente")

                # Mostrar datos del contribuyente
                st.subheader("Datos del Contribuyente")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Cédula", st.session_state.liquidador.datos['contribuyente'].get('cedula', 'N/A'))
                with col2:
                    st.metric("Nombre", st.session_state.liquidador.datos['contribuyente'].get('nombre', 'N/A'))
                with col3:
                    st.metric("Año", st.session_state.liquidador.datos['contribuyente'].get('ano', 'N/A'))

                # ============================================================
                # LIQUIDACIÓN AUTOMÁTICA
                # ============================================================

                # Usar datos del archivo para calcular automáticamente
                if True:  # Calcular siempre
                if mapeador.leer_exogena():
                    resultado_mapeo = mapeador.generar_reporte_detallado()

                    datos_mapeo = resultado_mapeo['datos']
                    mapeo_categorias = resultado_mapeo['mapeo']
                    conceptos = resultado_mapeo['conceptos']
                    totales_mapeo = resultado_mapeo['totales']
                    total_ingresos_real = resultado_mapeo['total_ingresos']

                    # Tabs detallados por categoría
                    if mapeo_categorias:
                        tabs_list = list(mapeo_categorias.keys())
                        tabs = st.tabs(tabs_list)

                        for tab, categoria in zip(tabs, tabs_list):
                            with tab:
                                st.subheader(f"{categoria}")
                                subcategorias = mapeo_categorias[categoria]

                                for subcategoria, conceptos_dict in subcategorias.items():
                                    st.markdown(f"**{subcategoria}**")
                                    df = pd.DataFrame([
                                        {'Concepto': k, 'Valor': f"${v:,.0f}"}
                                        for k, v in conceptos_dict.items()
                                    ])
                                    st.dataframe(df, use_container_width=True, hide_index=True)

                                    subtotal = sum(conceptos_dict.values())
                                    st.metric(f"Subtotal {subcategoria}", f"${subtotal:,.0f}")

                    # Resumen total detallado
                    st.divider()
                    st.subheader("📈 Resumen Total por Categoría")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if 'Rentas de Trabajo' in totales_mapeo:
                            st.metric("💼 Rentas de Trabajo", f"${totales_mapeo['Rentas de Trabajo']:,.0f}")
                    with col2:
                        if 'Rentas de Capital' in totales_mapeo:
                            st.metric("💰 Rentas de Capital", f"${totales_mapeo['Rentas de Capital']:,.0f}")
                    with col3:
                        if 'Rentas No Laborales' in totales_mapeo:
                            st.metric("🏥 Rentas No Laborales", f"${totales_mapeo['Rentas No Laborales']:,.0f}")

                    st.metric("📊 TOTAL INGRESOS MAPEADOS", f"${total_ingresos_real:,.0f}", delta=f"{len(conceptos)} conceptos identificados")

                # ============================================================
                # CÁLCULO AUTOMÁTICO INMEDIATO
                # ============================================================
                st.divider()
                st.subheader("🧮 Liquidación Automática")

                # Datos del archivo
                total_ingresos = sum(st.session_state.liquidador.datos['ingresos'].values())
                total_retenciones_detectadas = sum(st.session_state.liquidador.datos['retenciones'].values())

                # Mostrar valores detectados
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 **Ingresos Detectados:** ${total_ingresos:,.0f}")
                with col2:
                    st.info(f"🔐 **Retenciones Detectadas:** ${total_retenciones_detectadas:,.0f}")

                # Cálculo automático CON parámetros por defecto
                deduccion_pct = 10  # Por defecto
                deducciones = total_ingresos * (deduccion_pct / 100)
                base_liquida = total_ingresos - deducciones

                # IRPF progresivo
                rangos = [
                    (0, 66950000, 0),
                    (66950000, 134900000, 0.05),
                    (134900000, 404700000, 0.12),
                    (404700000, 673500000, 0.25),
                    (673500000, 1347000000, 0.32),
                    (1347000000, float('inf'), 0.37),
                ]
                irpf = 0
                for inicio, fin, tasa in rangos:
                    if base_liquida > inicio:
                        tramo = min(base_liquida, fin) - inicio
                        irpf += tramo * tasa

                # Aporte solidario
                uvt_2025 = 49799
                limite = 16000 * uvt_2025
                aporte_solidario = 0
                if base_liquida > limite:
                    aporte_solidario = (base_liquida - limite) * 0.01

                total_impuesto = irpf + aporte_solidario
                saldo = max(0, total_impuesto - total_retenciones_detectadas)
                acreencia = max(0, total_retenciones_detectadas - total_impuesto)

                # Guardar en sesión
                st.session_state.liquidacion_completa = {
                    'liquidador_renta': base_liquida,
                    'base_liquida': base_liquida,
                    'irpf': irpf,
                    'aporte_solidario': aporte_solidario,
                    'total_impuesto': total_impuesto,
                    'retenciones': total_retenciones_detectadas,
                    'saldo_pagar': saldo,
                    'acreencia': acreencia,
                }

                st.success("✅ Liquidación calculada automáticamente")

                # Mostrar resultado prominente
                st.divider()
                st.subheader("📊 Resultado de la Liquidación")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Impuesto", f"${st.session_state.liquidacion_completa['total_impuesto']:,.0f}")

                with col2:
                    st.metric("Retenciones", f"${st.session_state.liquidacion_completa['retenciones']:,.0f}")

                with col3:
                    if st.session_state.liquidacion_completa['saldo_pagar'] > 0:
                        st.metric("💰 SALDO A PAGAR", f"${st.session_state.liquidacion_completa['saldo_pagar']:,.0f}", delta="A Pagar")
                    else:
                        st.metric("💵 ACREENCIA", f"${st.session_state.liquidacion_completa['acreencia']:,.0f}", delta="Saldo a Favor")

                # Detalles
                st.divider()
                st.subheader("📋 Detalles del Cálculo")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Base Líquida (10% deducción)", f"${base_liquida:,.0f}")
                    st.metric("IRPF", f"${irpf:,.0f}")
                with col2:
                    st.metric("Aporte Solidario", f"${aporte_solidario:,.0f}")
                    st.metric("Total Impuesto", f"${total_impuesto:,.0f}")

                # Limpiar archivo temporal
                os.remove(temp_exogena)

            else:
                st.error("❌ Error al leer el archivo de Exógena")

# ============================================================
# TAB 2: MAPEAR DATOS
# ============================================================
with tab2:
    st.header("🔗 Mapear Datos")

    if st.session_state.liquidador is None:
        st.warning("⚠️ Primero carga un archivo de Exógena en la pestaña anterior")
    else:
        st.subheader("Mapeo de Conceptos")
        st.info("Personaliza cómo se mapean los conceptos de Exógena al Formulario 210")

        datos_mapeados = {}
        for concepto, valor in st.session_state.liquidador.datos['ingresos'].items():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(concepto)
            with col2:
                categoria = st.selectbox(
                    f"Categoría para {concepto}",
                    ["Honorarios", "Rendimientos Fin.", "Arrendamiento", "Ganancia Bienes", "Otros"],
                    key=f"cat_{concepto}"
                )
                datos_mapeados[concepto] = categoria
            with col3:
                st.metric("Valor", f"${valor:,.0f}")

        if st.button("✅ Confirmar Mapeo", use_container_width=True):
            st.session_state.datos_mapeados = True
            st.success("✅ Mapeo configurado correctamente")

        # Retenciones
        st.subheader("Retenciones en la Fuente")
        retencion = st.number_input(
            "Retención en la Fuente (valor en $)",
            min_value=0,
            step=10000,
            key="retencion"
        )
        if retencion > 0:
            st.session_state.liquidador.datos['retenciones'] = {
                'Retención en la Fuente': retencion
            }

# ============================================================
# TAB 3: LIQUIDACIÓN
# ============================================================
with tab3:
    st.header("💰 Liquidación del Impuesto")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Parámetros de Cálculo")
        st.metric("UVT 2025", "$49,799")
        st.metric("Tasa IRPF Básica", "5% - 37%")

    with col2:
        st.subheader("⚙️ Entrada Manual de Datos")

        # Liquidador Renta
        ingresos_manual = st.number_input(
            "Liquidador Renta ($)",
            min_value=0,
            value=int(sum(st.session_state.liquidador.datos['ingresos'].values())) if st.session_state.liquidador else 0,
            step=100000,
            key="ingresos_manual"
        )

        # Retenciones
        retenciones_manual = st.number_input(
            "Retenciones en la Fuente ($)",
            min_value=0,
            value=int(sum(st.session_state.liquidador.datos['retenciones'].values())) if st.session_state.liquidador else 0,
            step=100000,
            key="retenciones_manual"
        )

    st.divider()

    if st.button("🧮 Calcular Liquidación Completa", use_container_width=True, type="primary"):
        with st.spinner("Calculando liquidación..."):
            # Validar que al menos haya ingresos
            if ingresos_manual > 0:
                # Liquidador Renta es la base líquida directa
                base_liquida = ingresos_manual
                retenciones = retenciones_manual

                # IRPF progresivo
                rangos = [
                    (0, 66950000, 0),
                    (66950000, 134900000, 0.05),
                    (134900000, 404700000, 0.12),
                    (404700000, 673500000, 0.25),
                    (673500000, 1347000000, 0.32),
                    (1347000000, float('inf'), 0.37),
                ]
                irpf = 0
                for inicio, fin, tasa in rangos:
                    if base_liquida > inicio:
                        tramo = min(base_liquida, fin) - inicio
                        irpf += tramo * tasa

                # Aporte solidario
                uvt_2025 = 49799
                limite = 16000 * uvt_2025
                aporte_solidario = 0
                if base_liquida > limite:
                    aporte_solidario = (base_liquida - limite) * 0.01

                total_impuesto = irpf + aporte_solidario
                saldo = max(0, total_impuesto - retenciones)
                acreencia = max(0, retenciones - total_impuesto)

                st.session_state.liquidacion_completa = {
                    'liquidador_renta': base_liquida,
                    'base_liquida': base_liquida,
                    'irpf': irpf,
                    'aporte_solidario': aporte_solidario,
                    'total_impuesto': total_impuesto,
                    'retenciones': retenciones,
                    'saldo_pagar': saldo,
                    'acreencia': acreencia,
                }

                st.success("✅ Liquidación calculada correctamente")

                # Mostrar resultado prominente
                st.divider()
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Impuesto", f"${st.session_state.liquidacion_completa['total_impuesto']:,.0f}")

                with col2:
                    st.metric("Retenciones", f"${st.session_state.liquidacion_completa['retenciones']:,.0f}")

                with col3:
                    if st.session_state.liquidacion_completa['saldo_pagar'] > 0:
                        st.metric("💰 SALDO A PAGAR", f"${st.session_state.liquidacion_completa['saldo_pagar']:,.0f}", delta="A Pagar")
                    else:
                        st.metric("💵 ACREENCIA", f"${st.session_state.liquidacion_completa['acreencia']:,.0f}", delta="Saldo a Favor")
            else:
                st.info("💡 Ingresa un valor en 'Liquidador Renta' para calcular")

# ============================================================
# TAB 4: RESULTADOS
# ============================================================
with tab4:
    st.header("📈 Resultados de la Liquidación")

    if st.session_state.liquidacion_completa is None:
        st.warning("⚠️ Primero realiza una liquidación en la pestaña anterior")
    else:
        calculos = st.session_state.liquidacion_completa

        # Resumen
        st.subheader("Resumen Ejecutivo")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Liquidador Renta",
                f"${calculos['base_liquida']:,.0f}"
            )
        with col2:
            st.metric(
                "IRPF",
                f"${calculos['irpf']:,.0f}"
            )
        with col3:
            st.metric(
                "Total Impuesto",
                f"${calculos['total_impuesto']:,.0f}"
            )

        # Detalles
        st.subheader("Detalle de Cálculo")

        df_detalle = pd.DataFrame([
            {"Concepto": "Liquidador Renta", "Valor": f"${calculos['base_liquida']:,.0f}"},
            {"Concepto": "IRPF Calculado", "Valor": f"${calculos['irpf']:,.0f}"},
            {"Concepto": "Aporte Solidario", "Valor": f"${calculos['aporte_solidario']:,.0f}"},
            {"Concepto": "Total Impuesto", "Valor": f"${calculos['total_impuesto']:,.0f}"},
            {"Concepto": "Retenciones", "Valor": f"${calculos['retenciones']:,.0f}"},
            {"Concepto": "Saldo a Pagar", "Valor": f"${calculos['saldo_pagar']:,.0f}"},
            {"Concepto": "Acreencia", "Valor": f"${calculos['acreencia']:,.0f}"},
        ])

        st.dataframe(df_detalle, use_container_width=True)

        # Gráfica
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Composición del Impuesto")
            impuesto_data = {
                'IRPF': calculos['irpf'],
                'Aporte Solidario': calculos['aporte_solidario'],
            }
            if any(impuesto_data.values()):
                st.bar_chart(impuesto_data)

        with col2:
            st.subheader("Liquidador Renta vs Retenciones")
            balance_data = {
                'Liquidador Renta': calculos['base_liquida'],
                'Retenciones': calculos['retenciones'],
                'Impuesto': calculos['total_impuesto'],
            }
            st.bar_chart(balance_data)

        # Generar Excel
        st.subheader("📥 Descargar Resultados")

        if st.session_state.liquidador is not None:
            if st.button("📄 Generar Excel", use_container_width=True, type="primary"):
                with st.spinner("Generando Excel..."):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ruta_salida = f"formulario_210_liquidado_{timestamp}.xlsx"
                    st.session_state.liquidador.generar_excel(ruta_salida)

                    # Descargar
                    with open(ruta_salida, "rb") as f:
                        st.download_button(
                            label="⬇️ Descargar Formulario 210",
                            data=f.read(),
                            file_name=ruta_salida,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

        # Formulario Oficial DIAN 210
        st.subheader("📋 Formulario Oficial DIAN 210")

        col1, col2 = st.columns(2)

        with col1:
            st.info("Carga el formulario oficial de DIAN para llenar con los datos de la liquidación")
            formulario_oficial = st.file_uploader(
                "Carga Formulario 210 Oficial de DIAN",
                type=["xlsx"],
                key="formulario_oficial"
            )

        with col2:
            if formulario_oficial and st.session_state.liquidacion_completa:
                if st.button("📄 Descargar en Formulario Oficial DIAN", use_container_width=True, type="primary"):
                    with st.spinner("Llenando formulario oficial..."):
                        # Guardar archivo temporal
                        temp_formulario = f"/tmp/formulario_oficial_{datetime.now().timestamp()}.xlsx"
                        with open(temp_formulario, "wb") as f:
                            f.write(formulario_oficial.getbuffer())

                        try:
                            # Crear llenador COMPLETO según DIAN
                            llenador = LlenadorFormulario210CompletoDIAN(temp_formulario)

                            # Datos para llenar (COMPLETO)
                            datos_llenado = {
                                'ano': 2024,
                                'cedula': 'MANUAL',
                                'nombre': 'CONTRIBUYENTE',
                                'liquidador_renta': int(st.session_state.liquidacion_completa['base_liquida']),
                                'irpf': int(st.session_state.liquidacion_completa['irpf']),
                                'aporte_solidario': int(st.session_state.liquidacion_completa['aporte_solidario']),
                                'total_impuesto': int(st.session_state.liquidacion_completa['total_impuesto']),
                                'retenciones': int(st.session_state.liquidacion_completa['retenciones']),
                                'saldo_pagar': int(st.session_state.liquidacion_completa['saldo_pagar']),
                            }

                            # Procesar y guardar (COMPLETO)
                            ruta_archivo = llenador.procesar_completo(datos_llenado)

                            if ruta_archivo and os.path.exists(ruta_archivo):
                                # Leer y descargar
                                with open(ruta_archivo, "rb") as f:
                                    st.download_button(
                                        label="⬇️ Descargar Formulario 210 Llenado",
                                        data=f.read(),
                                        file_name=ruta_archivo.split('/')[-1],
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )

                                st.success(f"✅ Formulario llenado: {ruta_archivo.split('/')[-1]}")
                            else:
                                st.error("❌ Error llenando el formulario")

                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

                        finally:
                            # Limpiar temporal
                            if os.path.exists(temp_formulario):
                                os.remove(temp_formulario)
            elif not formulario_oficial:
                st.warning("⚠️ Carga el Formulario 210 oficial de DIAN")
            elif not st.session_state.liquidacion_completa:
                st.warning("⚠️ Primero calcula la liquidación")

        # JSON exportable
        st.subheader("📋 Datos JSON")
        contribuyente_info = {}
        if st.session_state.liquidador:
            contribuyente_info = st.session_state.liquidador.datos['contribuyente']

        json_data = {
            'contribuyente': contribuyente_info,
            'calculos': calculos,
        }
        st.json(json_data)

# ============================================================
# Pie de página
# ============================================================
st.divider()
st.markdown("""
**Sistema de Liquidación de Formulario 210**
- 📍 Colombia | DIAN 2024-2025
- ⚠️ Esta herramienta es informativa. Valida con un contador antes de presentar a DIAN
- 🔒 Tus datos se procesan localmente
""")
