#!/usr/bin/env python3
"""
APP WEB - Liquidador Formulario 210 COMPLETO
Clasificación según Norma DIAN + Cálculo + Descarga
"""

import streamlit as st
import pandas as pd
from liquidador_renta import Formulario210Liquidador
from llenar_formulario_210_completo_dian import LlenadorFormulario210CompletoDIAN
from datetime import datetime
import os

st.set_page_config(
    page_title="Liquidador Formulario 210",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Liquidador de Formulario 210 - DIAN")
st.markdown("**Clasificación | Cálculo | Liquidación | Descarga**")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📁 Cargar", "📊 Análisis", "💰 Liquidación", "📄 Descarga"])

# Mapeo de conceptos a categorías
CLASIFICACION = {
    'Rentas de Trabajo': [
        'salario', 'sueldo', 'honorario', 'comisión', 'bono', 'prima',
        'vacaciones', 'cesantías', 'prestación', 'pago laboral', 'compensación'
    ],
    'Rentas de Capital': [
        'interés', 'dividendo', 'rendimiento', 'cdt', 'arrendamiento',
        'ganancia', 'utilidad', 'renta fija', 'capital', 'inversión'
    ],
    'Rentas No Laborales': [
        'pensión', 'transferencia', 'subsidio', 'ayuda', 'donación',
        'herencia', 'jubilación', 'retiro'
    ]
}

def clasificar_renta(concepto):
    """Clasifica concepto en categoría según norma DIAN"""
    concepto_lower = str(concepto).lower()
    for categoria, palabras_clave in CLASIFICACION.items():
        if any(palabra in concepto_lower for palabra in palabras_clave):
            return categoria
    return 'Otros'

# ============================================================
# TAB 1: CARGAR ARCHIVO
# ============================================================
with tab1:
    st.header("📁 Cargar Archivo de Exógena")

    archivo_exogena = st.file_uploader(
        "Selecciona archivo Exógena",
        type=["xlsx", "xls"]
    )

    if archivo_exogena:
        with st.spinner("Leyendo archivo..."):
            temp_exogena = f"/tmp/exogena_{datetime.now().timestamp()}.xlsx"
            with open(temp_exogena, "wb") as f:
                f.write(archivo_exogena.getbuffer())

            # Crear liquidador
            liquidador = Formulario210Liquidador(2024)

            if liquidador.leer_exogena(temp_exogena):
                st.success("✅ Archivo cargado correctamente")

                # Datos del contribuyente
                st.subheader("📋 Datos del Contribuyente")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Cédula", liquidador.datos['contribuyente'].get('cedula', 'N/A'))
                with col2:
                    st.metric("Nombre", liquidador.datos['contribuyente'].get('nombre', 'N/A'))
                with col3:
                    st.metric("Año", liquidador.datos['contribuyente'].get('ano', 'N/A'))

                # Guardar en sesión
                st.session_state.liquidador = liquidador
                st.session_state.temp_exogena = temp_exogena

            else:
                st.error("❌ Error al leer el archivo")

# ============================================================
# TAB 2: ANÁLISIS POR CATEGORÍA
# ============================================================
with tab2:
    st.header("📊 Análisis Clasificado - Norma DIAN")

    if 'liquidador' in st.session_state:
        liquidador = st.session_state.liquidador

        # Clasificar ingresos
        ingresos_clasificados = {
            'Rentas de Trabajo': {},
            'Rentas de Capital': {},
            'Rentas No Laborales': {},
            'Otros': {},
            'Retenciones': {}
        }

        for concepto, valor in liquidador.datos['ingresos'].items():
            categoria = clasificar_renta(concepto)
            ingresos_clasificados[categoria][concepto] = valor

        for concepto, valor in liquidador.datos['retenciones'].items():
            ingresos_clasificados['Retenciones'][concepto] = valor

        # Mostrar por categoría
        col1, col2, col3 = st.columns(3)

        # Rentas de Trabajo
        with col1:
            st.markdown("### 💼 Rentas de Trabajo")
            if ingresos_clasificados['Rentas de Trabajo']:
                df_trab = pd.DataFrame([
                    {'Concepto': k, 'Valor': f"${v:,.0f}"}
                    for k, v in ingresos_clasificados['Rentas de Trabajo'].items()
                ])
                st.dataframe(df_trab, use_container_width=True, hide_index=True)
                total_trab = sum(ingresos_clasificados['Rentas de Trabajo'].values())
                st.metric("Total", f"${total_trab:,.0f}")
            else:
                st.info("Sin rentas de trabajo")

        # Rentas de Capital
        with col2:
            st.markdown("### 💰 Rentas de Capital")
            if ingresos_clasificados['Rentas de Capital']:
                df_cap = pd.DataFrame([
                    {'Concepto': k, 'Valor': f"${v:,.0f}"}
                    for k, v in ingresos_clasificados['Rentas de Capital'].items()
                ])
                st.dataframe(df_cap, use_container_width=True, hide_index=True)
                total_cap = sum(ingresos_clasificados['Rentas de Capital'].values())
                st.metric("Total", f"${total_cap:,.0f}")
            else:
                st.info("Sin rentas de capital")

        # Rentas No Laborales
        with col3:
            st.markdown("### 🏥 Rentas No Laborales")
            if ingresos_clasificados['Rentas No Laborales']:
                df_nol = pd.DataFrame([
                    {'Concepto': k, 'Valor': f"${v:,.0f}"}
                    for k, v in ingresos_clasificados['Rentas No Laborales'].items()
                ])
                st.dataframe(df_nol, use_container_width=True, hide_index=True)
                total_nol = sum(ingresos_clasificados['Rentas No Laborales'].values())
                st.metric("Total", f"${total_nol:,.0f}")
            else:
                st.info("Sin rentas no laborales")

        # Resumen
        st.divider()
        st.subheader("📈 Resumen Total")

        total_trab = sum(ingresos_clasificados['Rentas de Trabajo'].values()) if ingresos_clasificados['Rentas de Trabajo'] else 0
        total_cap = sum(ingresos_clasificados['Rentas de Capital'].values()) if ingresos_clasificados['Rentas de Capital'] else 0
        total_nol = sum(ingresos_clasificados['Rentas No Laborales'].values()) if ingresos_clasificados['Rentas No Laborales'] else 0
        total_ret = sum(ingresos_clasificados['Retenciones'].values()) if ingresos_clasificados['Retenciones'] else 0
        total_ingresos = total_trab + total_cap + total_nol

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("💼 Trabajo", f"${total_trab:,.0f}")
        with col2:
            st.metric("💰 Capital", f"${total_cap:,.0f}")
        with col3:
            st.metric("🏥 No Laborales", f"${total_nol:,.0f}")
        with col4:
            st.metric("📊 TOTAL", f"${total_ingresos:,.0f}")
        with col5:
            st.metric("🔐 Retenciones", f"${total_ret:,.0f}")

    else:
        st.warning("⚠️ Primero carga un archivo en la pestaña anterior")

# ============================================================
# TAB 3: LIQUIDACIÓN
# ============================================================
with tab3:
    st.header("💰 Liquidación del Impuesto")

    if 'liquidador' in st.session_state:
        liquidador = st.session_state.liquidador

        st.subheader("⚙️ Parámetros de Cálculo")

        col1, col2 = st.columns(2)
        with col1:
            deduccion_pct = st.slider("% Deducción", 0, 100, 10)
        with col2:
            st.metric("UVT 2025", "$49,799")

        # Calcular
        total_ingresos = sum(liquidador.datos['ingresos'].values())
        total_retenciones = sum(liquidador.datos['retenciones'].values())

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
        saldo = max(0, total_impuesto - total_retenciones)

        # Guardar en sesión
        st.session_state.liquidacion_completa = {
            'base_liquida': base_liquida,
            'irpf': irpf,
            'aporte_solidario': aporte_solidario,
            'total_impuesto': total_impuesto,
            'retenciones': total_retenciones,
            'saldo_pagar': saldo,
        }

        st.divider()
        st.subheader("📊 Resultado de la Liquidación")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Ingresos", f"${total_ingresos:,.0f}")
            st.metric("Deducciones", f"${deducciones:,.0f}")
            st.metric("Base Líquida", f"${base_liquida:,.0f}")
            st.metric("IRPF", f"${irpf:,.0f}")

        with col2:
            st.metric("Aporte Solidario", f"${aporte_solidario:,.0f}")
            st.metric("Total Impuesto", f"${total_impuesto:,.0f}")
            st.metric("Retenciones", f"${total_retenciones:,.0f}")
            st.metric("💰 SALDO A PAGAR", f"${saldo:,.0f}")

    else:
        st.warning("⚠️ Primero carga un archivo en la pestaña anterior")

# ============================================================
# TAB 4: DESCARGA
# ============================================================
with tab4:
    st.header("📄 Descargar Formulario 210")

    st.info("Carga el Formulario 210 Oficial de DIAN para descargarlo llenado")

    if 'liquidacion_completa' in st.session_state:
        formulario_oficial = st.file_uploader(
            "Carga Formulario 210 Oficial",
            type=["xlsx"],
            key="formulario_descarga"
        )

        if formulario_oficial:
            if st.button("📥 Descargar Formulario Llenado", use_container_width=True, type="primary"):
                with st.spinner("Llenando formulario..."):
                    temp_form = f"/tmp/form_{datetime.now().timestamp()}.xlsx"
                    with open(temp_form, "wb") as f:
                        f.write(formulario_oficial.getbuffer())

                    try:
                        llenador = LlenadorFormulario210CompletoDIAN(temp_form)

                        # Clasificar ingresos por categoría
                        ingresos_clasificados = {
                            'Rentas de Trabajo': {},
                            'Rentas de Capital': {},
                            'Rentas No Laborales': {},
                        }

                        for concepto, valor in st.session_state.liquidador.datos['ingresos'].items():
                            categoria = clasificar_renta(concepto)
                            if categoria in ingresos_clasificados:
                                ingresos_clasificados[categoria][concepto] = valor

                        total_trabajo = sum(ingresos_clasificados['Rentas de Trabajo'].values())
                        total_capital = sum(ingresos_clasificados['Rentas de Capital'].values())
                        total_no_labor = sum(ingresos_clasificados['Rentas No Laborales'].values())

                        datos = {
                            'ano': 2024,
                            'cedula': st.session_state.liquidador.datos['contribuyente'].get('cedula', 'MANUAL'),
                            'nombre': st.session_state.liquidador.datos['contribuyente'].get('nombre', 'CONTRIBUYENTE'),
                            'rentas_trabajo': int(total_trabajo),
                            'rentas_capital': int(total_capital),
                            'rentas_no_laborales': int(total_no_labor),
                            'liquidador_renta': int(st.session_state.liquidacion_completa['base_liquida']),
                            'irpf': int(st.session_state.liquidacion_completa['irpf']),
                            'aporte_solidario': int(st.session_state.liquidacion_completa['aporte_solidario']),
                            'total_impuesto': int(st.session_state.liquidacion_completa['total_impuesto']),
                            'retenciones': int(st.session_state.liquidacion_completa['retenciones']),
                            'saldo_pagar': int(st.session_state.liquidacion_completa['saldo_pagar']),
                        }

                        ruta = llenador.procesar_completo(datos)

                        if ruta and os.path.exists(ruta):
                            with open(ruta, "rb") as f:
                                st.download_button(
                                    label="⬇️ Descargar Formulario 210",
                                    data=f.read(),
                                    file_name=ruta.split('/')[-1],
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            st.success(f"✅ Listo para descargar")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

                    finally:
                        if os.path.exists(temp_form):
                            os.remove(temp_form)

    else:
        st.warning("⚠️ Primero completa el cálculo en la pestaña anterior")
