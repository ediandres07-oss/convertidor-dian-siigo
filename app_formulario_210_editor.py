#!/usr/bin/env python3
"""
Editor Interactivo Formulario 210 DIAN
Interfaz Streamlit para lectura, edición y guardado de casillas
"""

import streamlit as st
from formulario_210_mapper import Formulario210Mapper
import os

st.set_page_config(
    page_title="Editor Formulario 210",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Editor Formulario 210 - DIAN")
st.markdown("**Declaración de Renta Personas Naturales Residentes**")

# Ruta predeterminada
RUTA_ARCHIVO_DEFECTO = "/Users/edison/Downloads/210-Declaracion-de-renta-y-complementarios-Personas-Naturales-y-asimiladas-1.xlsx"

# Inicializar sesión
if 'mapper' not in st.session_state:
    st.session_state.mapper = None

if 'archivo_cargado' not in st.session_state:
    st.session_state.archivo_cargado = False

# ============================================================
# CARGAR ARCHIVO
# ============================================================
st.sidebar.header("📂 Formulario 210")

# Opción: Usar archivo predeterminado o cargar otro
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📥 Cargar Archivo Predeterminado", use_container_width=True):
        if os.path.exists(RUTA_ARCHIVO_DEFECTO):
            st.session_state.mapper = Formulario210Mapper(RUTA_ARCHIVO_DEFECTO)
            if st.session_state.mapper.abrir():
                st.session_state.mapper.leer_valores()
                st.session_state.archivo_cargado = True
                st.sidebar.success("✓ Archivo cargado")
            else:
                st.sidebar.error("✗ Error al cargar")
        else:
            st.sidebar.error("✗ Archivo no encontrado")

with col2:
    archivo = st.file_uploader(
        "O carga otro archivo",
        type=["xlsx"],
        key="uploader"
    )

    if archivo:
        temp_path = f"/tmp/formulario_210_{os.urandom(8).hex()}.xlsx"
        with open(temp_path, "wb") as f:
            f.write(archivo.getbuffer())

        st.session_state.mapper = Formulario210Mapper(temp_path)
        if st.session_state.mapper.abrir():
            st.session_state.mapper.leer_valores()
            st.session_state.archivo_cargado = True
            st.session_state.temp_path = temp_path
            st.sidebar.success("✓ Archivo cargado")
        else:
            st.sidebar.error("✗ Error")

# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================
if st.session_state.archivo_cargado:
    mapper = st.session_state.mapper

    # Mostrar UVT
    st.info(f"📊 **UVT 2024:** ${mapper.uvt_2024:,}")

    # Crear tabs por secciones
    tab_patrimonio, tab_cedula, tab_pensiones, tab_dividendos, tab_ganancias, tab_liquidacion, tab_resultado = st.tabs(
        ["Patrimonio", "Cédula General", "Pensiones", "Dividendos", "Ganancias", "Liquidación", "Resultado"]
    )

    cambios = {}

    # ============================================================
    # TAB: PATRIMONIO
    # ============================================================
    with tab_patrimonio:
        st.subheader("🏠 Patrimonio")

        col1, col2, col3 = st.columns(3)

        with col1:
            c29 = st.number_input(
                "Casilla 29: Total patrimonio bruto",
                value=int(mapper.obtener_casilla(29).valor or 0) if mapper.obtener_casilla(29) else 0,
                step=1000,
                key="c29"
            )
            if mapper.obtener_casilla(29) and c29 != mapper.obtener_casilla(29).valor:
                cambios[29] = c29

        with col2:
            c30 = st.number_input(
                "Casilla 30: Deudas",
                value=int(mapper.obtener_casilla(30).valor or 0) if mapper.obtener_casilla(30) else 0,
                step=1000,
                key="c30"
            )
            if mapper.obtener_casilla(30) and c30 != mapper.obtener_casilla(30).valor:
                cambios[30] = c30

        with col3:
            c31_val = mapper.obtener_casilla(31).valor or 0 if mapper.obtener_casilla(31) else 0
            st.metric(
                "Casilla 31: Total patrimonio líquido",
                f"${int(c31_val):,}",
                help="C29 - C30 (Calculado automáticamente)"
            )

    # ============================================================
    # TAB: CÉDULA GENERAL
    # ============================================================
    with tab_cedula:
        st.subheader("📊 Cédula General de Rentas")

        # RENTAS DE TRABAJO
        st.markdown("#### 💼 Rentas de Trabajo")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c32 = st.number_input("C32: Ingresos brutos", value=int(mapper.casillas[32].valor or 0), step=1000, key="c32")
            if c32 != mapper.casillas[32].valor:
                cambios[32] = c32

        with col2:
            c33 = st.number_input("C33: No constitutivos", value=int(mapper.casillas[33].valor or 0), step=1000, key="c33")
            if c33 != mapper.casillas[33].valor:
                cambios[33] = c33

        with col3:
            st.metric("C34: Renta líquida", f"${int(mapper.casillas[34].valor or 0):,}")

        with col4:
            c35 = st.number_input("C35: Exentas", value=int(mapper.casillas[35].valor or 0), step=1000, key="c35")
            if c35 != mapper.casillas[35].valor:
                cambios[35] = c35

        # RENTAS DE TRABAJO SIN RELACIÓN LABORAL
        st.markdown("#### 💼 Rentas de Trabajo Sin Relación Laboral")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c43 = st.number_input("C43: Ingresos brutos", value=int(mapper.casillas[43].valor or 0), step=1000, key="c43")
            if c43 != mapper.casillas[43].valor:
                cambios[43] = c43

        with col2:
            c44 = st.number_input("C44: No constitutivos", value=int(mapper.casillas[44].valor or 0), step=1000, key="c44")
            if c44 != mapper.casillas[44].valor:
                cambios[44] = c44

        with col3:
            c45 = st.number_input("C45: Costos/deducciones", value=int(mapper.casillas[45].valor or 0), step=1000, key="c45")
            if c45 != mapper.casillas[45].valor:
                cambios[45] = c45

        with col4:
            st.metric("C46: Renta líquida", f"${int(mapper.casillas[46].valor or 0):,}")

        # RENTAS DE CAPITAL
        st.markdown("#### 💰 Rentas de Capital")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c58 = st.number_input("C58: Ingresos brutos", value=int(mapper.casillas[58].valor or 0), step=1000, key="c58")
            if c58 != mapper.casillas[58].valor:
                cambios[58] = c58

        with col2:
            c59 = st.number_input("C59: No constitutivos", value=int(mapper.casillas[59].valor or 0), step=1000, key="c59")
            if c59 != mapper.casillas[59].valor:
                cambios[59] = c59

        with col3:
            c60 = st.number_input("C60: Costos/deducciones", value=int(mapper.casillas[60].valor or 0), step=1000, key="c60")
            if c60 != mapper.casillas[60].valor:
                cambios[60] = c60

        with col4:
            st.metric("C61: Renta líquida", f"${int(mapper.casillas[61].valor or 0):,}")

        # RENTAS NO LABORALES
        st.markdown("#### 🏥 Rentas No Laborales")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c74 = st.number_input("C74: Ingresos brutos", value=int(mapper.casillas[74].valor or 0), step=1000, key="c74")
            if c74 != mapper.casillas[74].valor:
                cambios[74] = c74

        with col2:
            c75 = st.number_input("C75: Devol./Rebajas", value=int(mapper.casillas[75].valor or 0), step=1000, key="c75")
            if c75 != mapper.casillas[75].valor:
                cambios[75] = c75

        with col3:
            c76 = st.number_input("C76: No constitutivos", value=int(mapper.casillas[76].valor or 0), step=1000, key="c76")
            if c76 != mapper.casillas[76].valor:
                cambios[76] = c76

        with col4:
            c77 = st.number_input("C77: Costos/deducciones", value=int(mapper.casillas[77].valor or 0), step=1000, key="c77")
            if c77 != mapper.casillas[77].valor:
                cambios[77] = c77

    # ============================================================
    # TAB: PENSIONES
    # ============================================================
    with tab_pensiones:
        st.subheader("🏥 Cédula de Pensiones")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c99 = st.number_input("C99: Ingresos brutos", value=int(mapper.casillas[99].valor or 0), step=1000, key="c99")
            if c99 != mapper.casillas[99].valor:
                cambios[99] = c99

        with col2:
            c100 = st.number_input("C100: No constitutivos", value=int(mapper.casillas[100].valor or 0), step=1000, key="c100")
            if c100 != mapper.casillas[100].valor:
                cambios[100] = c100

        with col3:
            st.metric("C101: Renta líquida", f"${int(mapper.casillas[101].valor or 0):,}")

        with col4:
            c102 = st.number_input("C102: Rentas exentas", value=int(mapper.casillas[102].valor or 0), step=1000, key="c102")
            if c102 != mapper.casillas[102].valor:
                cambios[102] = c102

    # ============================================================
    # TAB: DIVIDENDOS
    # ============================================================
    with tab_dividendos:
        st.subheader("💵 Cédula de Dividendos")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c104 = st.number_input("C104: Dividendos 2016+", value=int(mapper.casillas[104].valor or 0), step=1000, key="c104")
            if c104 != mapper.casillas[104].valor:
                cambios[104] = c104

        with col2:
            c105 = st.number_input("C105: No constitutivos", value=int(mapper.casillas[105].valor or 0), step=1000, key="c105")
            if c105 != mapper.casillas[105].valor:
                cambios[105] = c105

        with col3:
            c107 = st.number_input("C107: 1a subcédula 2017+", value=int(mapper.casillas[107].valor or 0), step=1000, key="c107")
            if c107 != mapper.casillas[107].valor:
                cambios[107] = c107

        with col4:
            c108 = st.number_input("C108: 2a subcédula 2017+", value=int(mapper.casillas[108].valor or 0), step=1000, key="c108")
            if c108 != mapper.casillas[108].valor:
                cambios[108] = c108

    # ============================================================
    # TAB: GANANCIAS OCASIONALES
    # ============================================================
    with tab_ganancias:
        st.subheader("🎲 Cédula de Ganancias Ocasionales")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c112 = st.number_input("C112: Ingresos", value=int(mapper.casillas[112].valor or 0), step=1000, key="c112")
            if c112 != mapper.casillas[112].valor:
                cambios[112] = c112

        with col2:
            c113 = st.number_input("C113: Costos", value=int(mapper.casillas[113].valor or 0), step=1000, key="c113")
            if c113 != mapper.casillas[113].valor:
                cambios[113] = c113

        with col3:
            c114 = st.number_input("C114: Exentas", value=int(mapper.casillas[114].valor or 0), step=1000, key="c114")
            if c114 != mapper.casillas[114].valor:
                cambios[114] = c114

        with col4:
            st.metric("C115: Gravables", f"${int(mapper.casillas[115].valor or 0):,}")

    # ============================================================
    # TAB: LIQUIDACIÓN
    # ============================================================
    with tab_liquidacion:
        st.subheader("🧮 Liquidación Privada")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("C116: Imp. cédula general", f"${int(mapper.casillas[116].valor or 0):,}")
            st.metric("C117: Imp. presuntiva", f"${int(mapper.casillas[117].valor or 0):,}")
            c122 = st.number_input("C122: Imp. exterior", value=int(mapper.casillas[122].valor or 0), step=1000, key="c122")
            if c122 != mapper.casillas[122].valor:
                cambios[122] = c122

        with col2:
            c118 = st.number_input("C118: Imp. div. 2017+", value=int(mapper.casillas[118].valor or 0), step=1000, key="c118")
            if c118 != mapper.casillas[118].valor:
                cambios[118] = c118

            c119 = st.number_input("C119: Imp. div. 2016", value=int(mapper.casillas[119].valor or 0), step=1000, key="c119")
            if c119 != mapper.casillas[119].valor:
                cambios[119] = c119

            c123 = st.number_input("C123: Donaciones", value=int(mapper.casillas[123].valor or 0), step=1000, key="c123")
            if c123 != mapper.casillas[123].valor:
                cambios[123] = c123

        with col3:
            st.metric("C121: Total impuesto rentas", f"${int(mapper.casillas[121].valor or 0):,}")
            st.metric("C125: Total descuentos", f"${int(mapper.casillas[125].valor or 0):,}")
            st.metric("C126: Impuesto neto", f"${int(mapper.casillas[126].valor or 0):,}")

        st.divider()
        st.subheader("📥 Retenciones y Anticipos")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            c130 = st.number_input("C130: Anticipo año anterior", value=int(mapper.casillas[130].valor or 0), step=1000, key="c130")
            if c130 != mapper.casillas[130].valor:
                cambios[130] = c130

        with col2:
            c131 = st.number_input("C131: Saldo favor anterior", value=int(mapper.casillas[131].valor or 0), step=1000, key="c131")
            if c131 != mapper.casillas[131].valor:
                cambios[131] = c131

        with col3:
            c132 = st.number_input("C132: Retenciones", value=int(mapper.casillas[132].valor or 0), step=1000, key="c132")
            if c132 != mapper.casillas[132].valor:
                cambios[132] = c132

        with col4:
            c133 = st.number_input("C133: Anticipo siguiente", value=int(mapper.casillas[133].valor or 0), step=1000, key="c133")
            if c133 != mapper.casillas[133].valor:
                cambios[133] = c133

    # ============================================================
    # TAB: RESULTADO FINAL
    # ============================================================
    with tab_resultado:
        st.subheader("✅ Saldo / Resultado Final")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("C129: Total impuesto a cargo", f"${int(mapper.casillas[129].valor or 0):,}")
            st.metric("C134: Saldo a pagar", f"${int(mapper.casillas[134].valor or 0):,}")

        with col2:
            c135 = st.number_input("C135: Sanciones", value=int(mapper.casillas[135].valor or 0), step=1000, key="c135")
            if c135 != mapper.casillas[135].valor:
                cambios[135] = c135

            st.metric("C136: Total saldo pagar", f"${int(mapper.casillas[136].valor or 0):,}")

        with col3:
            st.metric("C137: Total saldo favor", f"${int(mapper.casillas[137].valor or 0):,}")

        with col4:
            st.divider()
            st.subheader("📋 Datos Adicionales")

            c138 = st.number_input("C138: Dependientes", value=int(mapper.casillas[138].valor or 0), step=1, key="c138")
            if c138 != mapper.casillas[138].valor:
                cambios[138] = c138

            c139 = st.number_input("C139: Adición dependientes", value=int(mapper.casillas[139].valor or 0), step=1000, key="c139")
            if c139 != mapper.casillas[139].valor:
                cambios[139] = c139

            c141 = st.number_input("C141: Aporte voluntario", value=int(mapper.casillas[141].valor or 0), step=1000, key="c141")
            if c141 != mapper.casillas[141].valor:
                cambios[141] = c141

    # ============================================================
    # GUARDAR CAMBIOS
    # ============================================================
    st.divider()

    if cambios:
        st.warning(f"📝 **Cambios pendientes:** {len(cambios)} casilla(s)")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
                guardados = 0
                for num_casilla, valor in cambios.items():
                    if mapper.guardar_valor(num_casilla, valor):
                        guardados += 1

                if mapper.guardar_archivo():
                    st.success(f"✅ Se guardaron {guardados} cambios en el archivo")
                    st.session_state.archivo_cargado = False
                else:
                    st.error("✗ Error guardando archivo")

        with col2:
            if st.button("🔄 Descartar Cambios", use_container_width=True):
                st.rerun()

    else:
        st.info("ℹ️  Sin cambios pendientes")

else:
    st.info("👈 Haz clic en 'Cargar Archivo Predeterminado' en la barra lateral para comenzar")
