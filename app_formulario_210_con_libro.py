#!/usr/bin/env python3
"""
Editor Formulario 210 DIAN - CON REFERENCIAS DEL LIBRO DE RENTA 2025
Integración completa de norma + interfaz + educación
"""

import streamlit as st
import sys
import os

# Agregar ruta de módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from formulario_210_mapper import Formulario210Mapper
from libro_referencias import (
    obtener_ayuda_casilla, obtener_ayuda_seccion,
    VALORES_2025, RANGOS_IRPF
)

st.set_page_config(
    page_title="Formulario 210 + Libro Renta 2025",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Formulario 210 + 📚 Guía Renta 2025")
st.markdown("**Editor interactivo con referencias normativas completas**")

RUTA_ARCHIVO = "/Users/edison/Downloads/210-Declaracion-de-renta-y-complementarios-Personas-Naturales-y-asimiladas-1.xlsx"

if 'mapper' not in st.session_state:
    st.session_state.mapper = None
if 'archivo_cargado' not in st.session_state:
    st.session_state.archivo_cargado = False

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("📂 Formulario 210")

    if st.button("📥 Cargar Archivo", use_container_width=True, type="primary"):
        if os.path.exists(RUTA_ARCHIVO):
            mapper = Formulario210Mapper(RUTA_ARCHIVO)
            if mapper.abrir():
                mapper.leer_valores()
                st.session_state.mapper = mapper
                st.session_state.archivo_cargado = True
                st.sidebar.success("✅ Archivo cargado")
            else:
                st.sidebar.error("❌ Error al abrir")
        else:
            st.sidebar.error("❌ Archivo no encontrado")

    st.divider()
    st.subheader("📚 Referencias Rápidas")

    st.markdown("#### 💰 Valores 2025")
    st.metric("UVT", f"${VALORES_2025['uvt']['valor']:,}")
    st.markdown("**Aporte Solidario:** 1% sobre > 16.000 UVT")

# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================
if st.session_state.archivo_cargado:
    mapper = st.session_state.mapper

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📊 **UVT 2024:** ${mapper.uvt_2024:,}")
    with col2:
        st.info(f"📊 **UVT 2025:** ${VALORES_2025['uvt']['valor']:,}")
    with col3:
        st.info("📚 Año Gravable: 2025")

    def get_valor(num):
        try:
            c = mapper.casillas.get(num)
            return int(c.valor) if c and c.valor else 0
        except:
            return 0

    def get_es_calculada(num):
        try:
            c = mapper.casillas.get(num)
            return c.es_calculada if c else False
        except:
            return False

    # Tabs
    tabs = st.tabs(
        ["Patrimonio", "Cédula General", "Pensiones", "Dividendos", "Ganancias", "Liquidación", "Resultado", "ℹ️ Guía"]
    )
    cambios = {}

    # TAB 0: PATRIMONIO
    with tabs[0]:
        st.subheader("🏠 Patrimonio")

        ayuda_sec = obtener_ayuda_seccion("patrimonio")
        with st.expander("📚 Guía de esta sección"):
            st.markdown(f"**{ayuda_sec['titulo']}** (págs. {ayuda_sec['paginas']})")
            for punto in ayuda_sec['puntos_clave']:
                st.markdown(punto)

        col1, col2, col3 = st.columns(3)

        with col1:
            val_29 = get_valor(29)
            c29 = st.number_input("C29: Total patrimonio bruto", value=val_29, step=1000, key="c29")
            if c29 != val_29:
                cambios[29] = c29
            ayuda = obtener_ayuda_casilla(29)
            if ayuda:
                st.caption(f"📄 Página {ayuda['pagina']} - {ayuda['descripcion'][:50]}")

        with col2:
            val_30 = get_valor(30)
            c30 = st.number_input("C30: Deudas", value=val_30, step=1000, key="c30")
            if c30 != val_30:
                cambios[30] = c30
            ayuda = obtener_ayuda_casilla(30)
            if ayuda:
                st.caption(f"📄 Página {ayuda['pagina']} - {ayuda['descripcion'][:50]}")

        with col3:
            val_31 = get_valor(31)
            st.metric("C31: Total patrimonio líquido", f"${val_31:,}")
            st.caption("📐 C29 - C30 (Calculado)")

    # TAB 1: CÉDULA GENERAL
    with tabs[1]:
        st.subheader("📊 Cédula General")

        ayuda_sec = obtener_ayuda_seccion("rentas_trabajo")
        with st.expander("📚 Guía de esta sección"):
            st.markdown(f"**{ayuda_sec['titulo']}** (págs. {ayuda_sec['paginas']})")
            for punto in ayuda_sec['puntos_clave']:
                st.markdown(punto)

        st.markdown("#### 💼 Rentas de Trabajo")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            val = get_valor(32)
            c = st.number_input("C32: Ingresos brutos", value=val, step=1000, key="c32")
            if c != val:
                cambios[32] = c
            st.caption("📄 Página 88")

        with col2:
            val = get_valor(33)
            c = st.number_input("C33: No constitutivos", value=val, step=1000, key="c33")
            if c != val:
                cambios[33] = c
            st.caption("📄 Página 123")

        with col3:
            val = get_valor(34)
            st.metric("C34: Renta líquida", f"${val:,}")
            st.caption("📐 C32 - C33")

        with col4:
            val = get_valor(35)
            c = st.number_input("C35: Exentas", value=val, step=1000, key="c35")
            if c != val:
                cambios[35] = c
            st.caption("📄 Página 146")

    # TAB 2: PENSIONES
    with tabs[2]:
        st.subheader("🏥 Pensiones")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            val = get_valor(99)
            c = st.number_input("C99: Ingresos brutos", value=val, step=1000, key="c99")
            if c != val:
                cambios[99] = c

        with col2:
            val = get_valor(100)
            c = st.number_input("C100: No constitutivos", value=val, step=1000, key="c100")
            if c != val:
                cambios[100] = c

        with col3:
            val = get_valor(101)
            st.metric("C101: Renta líquida", f"${val:,}")

        with col4:
            val = get_valor(102)
            c = st.number_input("C102: Exentas", value=val, step=1000, key="c102")
            if c != val:
                cambios[102] = c

    # TAB 3: DIVIDENDOS
    with tabs[3]:
        st.subheader("💵 Dividendos")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            val = get_valor(104)
            c = st.number_input("C104: Dividendos 2016+", value=val, step=1000, key="c104")
            if c != val:
                cambios[104] = c

        with col2:
            val = get_valor(105)
            c = st.number_input("C105: No constitutivos", value=val, step=1000, key="c105")
            if c != val:
                cambios[105] = c

        with col3:
            val = get_valor(107)
            c = st.number_input("C107: 1a subcédula", value=val, step=1000, key="c107")
            if c != val:
                cambios[107] = c

        with col4:
            val = get_valor(108)
            c = st.number_input("C108: 2a subcédula", value=val, step=1000, key="c108")
            if c != val:
                cambios[108] = c

    # TAB 4: GANANCIAS OCASIONALES
    with tabs[4]:
        st.subheader("🎲 Ganancias Ocasionales")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            val = get_valor(112)
            c = st.number_input("C112: Ingresos", value=val, step=1000, key="c112")
            if c != val:
                cambios[112] = c

        with col2:
            val = get_valor(113)
            c = st.number_input("C113: Costos", value=val, step=1000, key="c113")
            if c != val:
                cambios[113] = c

        with col3:
            val = get_valor(114)
            c = st.number_input("C114: Exentas", value=val, step=1000, key="c114")
            if c != val:
                cambios[114] = c

        with col4:
            val = get_valor(115)
            st.metric("C115: Gravables", f"${val:,}")

    # TAB 5: LIQUIDACIÓN
    with tabs[5]:
        st.subheader("🧮 Liquidación del Impuesto")

        ayuda_sec = obtener_ayuda_seccion("liquidacion")
        with st.expander("📚 Guía de Liquidación"):
            st.markdown(f"**{ayuda_sec['titulo']}**")
            for punto in ayuda_sec['puntos_clave']:
                st.markdown(punto)

        st.markdown("#### Cálculo de IRPF 2025")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Rangos progresivos:**")
            for rango in RANGOS_IRPF[:3]:
                st.markdown(f"  • ${rango['minimo']:,} a ${rango['maximo']:,}: {rango['tasa_txt']}")

        with col2:
            for rango in RANGOS_IRPF[3:]:
                st.markdown(f"  • ${rango['minimo']:,} a ${rango['maximo']:,}: {rango['tasa_txt']}")

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("C116: Imp. cédula", f"${get_valor(116):,}")
            st.metric("C117: Imp. presuntiva", f"${get_valor(117):,}")
            val = get_valor(122)
            c = st.number_input("C122: Imp. exterior", value=val, step=1000, key="c122")
            if c != val:
                cambios[122] = c

        with col2:
            val = get_valor(118)
            c = st.number_input("C118: Imp. div. 2017", value=val, step=1000, key="c118")
            if c != val:
                cambios[118] = c

            val = get_valor(119)
            c = st.number_input("C119: Imp. div. 2016", value=val, step=1000, key="c119")
            if c != val:
                cambios[119] = c

            val = get_valor(123)
            c = st.number_input("C123: Donaciones", value=val, step=1000, key="c123")
            if c != val:
                cambios[123] = c

        with col3:
            st.metric("C121: Total rentas", f"${get_valor(121):,}")
            st.metric("C125: Descuentos", f"${get_valor(125):,}")
            st.metric("C126: Neto", f"${get_valor(126):,}")

        st.divider()
        st.subheader("📥 Retenciones")

        col1, col2, col3, col4 = st.columns(4)

        for col, num, label in [
            (col1, 130, "C130: Anticipo anterior"),
            (col2, 131, "C131: Saldo anterior"),
            (col3, 132, "C132: Retenciones"),
            (col4, 133, "C133: Anticipo siguiente"),
        ]:
            with col:
                val = get_valor(num)
                c = st.number_input(label, value=val, step=1000, key=f"c{num}")
                if c != val:
                    cambios[num] = c

    # TAB 6: RESULTADO FINAL
    with tabs[6]:
        st.subheader("✅ Resultado Final")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("C129: Total a cargo", f"${get_valor(129):,}")
            st.metric("C134: Saldo pagar", f"${get_valor(134):,}")
            val = get_valor(135)
            c = st.number_input("C135: Sanciones", value=val, step=1000, key="c135")
            if c != val:
                cambios[135] = c

        with col2:
            st.metric("C136: Total saldo pagar", f"${get_valor(136):,}")
            st.metric("C137: Total saldo favor", f"${get_valor(137):,}")

            st.divider()
            st.subheader("📋 Datos Adicionales")
            val = get_valor(138)
            c = st.number_input("C138: Dependientes", value=val, step=1, key="c138")
            if c != val:
                cambios[138] = c

            val = get_valor(139)
            c = st.number_input("C139: Adición dependientes", value=val, step=1000, key="c139")
            if c != val:
                cambios[139] = c

            val = get_valor(141)
            c = st.number_input("C141: Aporte voluntario", value=val, step=1000, key="c141")
            if c != val:
                cambios[141] = c

    # TAB 7: GUÍA
    with tabs[7]:
        st.subheader("📚 Guía Rápida")
        st.markdown("""
        ### ¿Cómo usar?
        1. ✅ Carga tu Formulario 210
        2. ✅ Navega por secciones
        3. ✅ Consulta referencias del libro en cada casilla
        4. ✅ Edita campos permitidos
        5. ✅ Guarda cambios

        ### 📖 Estructura del Libro (665 págs)
        - **Cap. 2**: Patrimonio (págs. 43-83)
        - **Cap. 3**: Sistema Cedular (págs. 84-350+)
          - Rentas Trabajo (págs. 86-187)
          - Rentas Capital (págs. 254-317)
        - **Part. 2**: Casos Prácticos Detallados

        ### 💡 Conceptos
        - **UVT 2025:** $49.799
        - **IRPF:** 6 rangos progresivos (0% a 37%)
        - **Aporte Solidario:** 1% sobre > 16.000 UVT
        """)

else:
    st.info("👈 Haz clic en '**Cargar Archivo**' en la barra lateral para comenzar")

    st.divider()
    st.markdown("""
    ### 📚 Aplicación con Guía de Renta 2025

    ✨ **Características integradas:**
    - 📋 Editor interactivo del Formulario 210
    - 📖 Referencias normativas en cada casilla
    - 💡 Información del libro (página, capítulo, descripción)
    - 📊 Rangos IRPF 2025 y valores importantes
    - 🔒 Protección de fórmulas
    - 💾 Guardado automático en Excel

    **Puerto:** http://localhost:8502
    """)
