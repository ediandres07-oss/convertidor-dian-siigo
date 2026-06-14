import streamlit as st
import requests
import pandas as pd
import io
import time

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Sistema de Liquidaciones",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-title {
        color: #1f4788;
        font-size: 2.5em;
        margin-bottom: 20px;
    }
    .employee-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f4788;
        margin: 10px 0;
    }
    .download-button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<div class="header-title">💼 Sistema de Liquidaciones de Nómina</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🔧 Configuración")
    st.write("Carga tu archivo Excel con las siguientes hojas:")
    st.info("""
    **Hojas requeridas:**
    - **Empleados**: nombre, documento, salario_mensual, dias_laborados, auxilio_transporte

    **Hojas opcionales:**
    - **Parametros**: salud, pension, fondo_solidaridad
    - **Novedades**: documento, tipo_novedad, valor
    """)

# Crear 7 pestañas
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📤 Cargar",
    "📊 Completa",
    "💼 Prima",
    "🏖️ Vacaciones",
    "👤 Individual",
    "📈 Comparativa",
    "⚙️ Config"
])

# ========== TAB 1: CARGAR ARCHIVO ==========
with tab1:
    st.subheader("Carga tu archivo Excel")

    uploaded_file = st.file_uploader(
        "Selecciona un archivo Excel (.xlsx)",
        type=["xlsx", "xls"],
        help="El archivo debe contener al menos la hoja 'Empleados'"
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.session_state.archivo_name = uploaded_file.name

        st.success(f"✅ Archivo cargado: {uploaded_file.name}")

        # Procesar
        if st.button("🔍 Procesar Archivo", use_container_width=True, key="process_main"):
            with st.spinner("Procesando archivo..."):
                try:
                    files = {'file': uploaded_file.getvalue()}
                    response = requests.post(f"{API}/api/procesar-completo", files=files, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(f"❌ Error: {data['error']}")
                        else:
                            st.session_state.resultados = data
                            st.success(f"✅ Procesado: {data['total_empleados']} empleados")
                            st.info(f"💰 Total neto: ${data['total_neto']:,.2f}")
                            time.sleep(1)
                            st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        # Preview
        if st.button("👁️ Ver Vista Previa", use_container_width=True):
            try:
                df = pd.read_excel(uploaded_file, sheet_name='Empleados')
                st.write("**Primeras filas del archivo:**")
                st.dataframe(df.head(10), use_container_width=True)
            except Exception as e:
                st.error(f"Error: {e}")

# ========== TAB 2: LIQUIDACIÓN COMPLETA ==========
with tab2:
    st.subheader("📊 Liquidación Completa")

    if "resultados" in st.session_state:
        datos = st.session_state.resultados

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Empleados", datos['total_empleados'])
        with col2:
            total_dev = sum(e['total_devengos'] for e in datos['empleados'])
            st.metric("💰 Devengos", f"${total_dev:,.0f}")
        with col3:
            total_ded = sum(e['total_deducciones'] for e in datos['empleados'])
            st.metric("📉 Deducciones", f"${total_ded:,.0f}")
        with col4:
            st.metric("💵 Neto", f"${datos['total_neto']:,.0f}")

        st.divider()
        st.write("**Detalle por Empleado**")
        df_display = pd.DataFrame(datos['empleados'])
        cols = ['nombre', 'documento', 'salario_mensual', 'total_devengos', 'total_deducciones', 'neto_pagar']
        st.dataframe(df_display[cols].rename(columns={
            'nombre': 'Nombre',
            'documento': 'Documento',
            'salario_mensual': 'Salario',
            'total_devengos': 'Devengos',
            'total_deducciones': 'Deducciones',
            'neto_pagar': 'Neto'
        }), use_container_width=True, hide_index=True)

    else:
        st.info("📤 Carga un archivo para ver los resultados")

# ========== TAB 3: PRIMA DE SERVICIOS ==========
with tab3:
    st.subheader("💼 Prima de Servicios")
    st.write("*Prima = (Salario + Auxilio) × Días / 360*")

    if "uploaded_file" in st.session_state:
        if st.button("📊 Calcular Prima", use_container_width=True, key="calc_prima"):
            with st.spinner("Calculando prima..."):
                try:
                    files = {'file': st.session_state.uploaded_file.getvalue()}
                    response = requests.post(f"{API}/api/calcular-prima", files=files, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(f"❌ {data['error']}")
                        else:
                            st.session_state.prima_data = data
                            st.success(f"✅ Prima calculada para {data['total_empleados']} empleados")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        # Mostrar resultados
        if "prima_data" in st.session_state:
            datos = st.session_state.prima_data

            col1, col2 = st.columns(2)
            with col1:
                st.metric("👥 Empleados", datos['total_empleados'])
            with col2:
                st.metric("💰 Total Prima", f"${datos['total_prima']:,.0f}")

            st.divider()

            df_prima = pd.DataFrame(datos['empleados'])
            st.dataframe(df_prima[[
                'nombre', 'salario_mensual', 'auxilio_transporte', 'dias_laborados', 'valor_prima'
            ]].rename(columns={
                'nombre': 'Nombre',
                'salario_mensual': 'Salario',
                'auxilio_transporte': 'Auxilio',
                'dias_laborados': 'Días',
                'valor_prima': 'Prima'
            }), use_container_width=True, hide_index=True)

            # Botón descargar
            if st.button("📥 Descargar Excel Prima", use_container_width=True):
                with st.spinner("Generando Excel..."):
                    try:
                        files = {'file': st.session_state.uploaded_file.getvalue()}
                        response = requests.post(f"{API}/api/exportar-excel-prima", files=files, timeout=30)

                        if response.status_code == 200:
                            st.download_button(
                                label="⬇️ Descargar",
                                data=response.content,
                                file_name="prima_servicios.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    else:
        st.info("📤 Carga un archivo para calcular prima")

# ========== TAB 4: VACACIONES ==========
with tab4:
    st.subheader("🏖️ Vacaciones Proporcionales")
    st.write("*Vacaciones = Salario × Días / 720*")

    if "uploaded_file" in st.session_state:
        if st.button("📊 Calcular Vacaciones", use_container_width=True, key="calc_vaca"):
            with st.spinner("Calculando vacaciones..."):
                try:
                    files = {'file': st.session_state.uploaded_file.getvalue()}
                    response = requests.post(f"{API}/api/calcular-vacaciones", files=files, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(f"❌ {data['error']}")
                        else:
                            st.session_state.vacaciones_data = data
                            st.success(f"✅ Vacaciones calculadas para {data['total_empleados']} empleados")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        # Mostrar resultados
        if "vacaciones_data" in st.session_state:
            datos = st.session_state.vacaciones_data

            col1, col2 = st.columns(2)
            with col1:
                st.metric("👥 Empleados", datos['total_empleados'])
            with col2:
                st.metric("🏖️ Total Vacaciones", f"${datos['total_vacaciones']:,.0f}")

            st.divider()

            df_vaca = pd.DataFrame(datos['empleados'])
            st.dataframe(df_vaca[[
                'nombre', 'salario_mensual', 'dias_laborados', 'valor_vacaciones'
            ]].rename(columns={
                'nombre': 'Nombre',
                'salario_mensual': 'Salario',
                'dias_laborados': 'Días',
                'valor_vacaciones': 'Vacaciones'
            }), use_container_width=True, hide_index=True)

            # Botón descargar
            if st.button("📥 Descargar Excel Vacaciones", use_container_width=True):
                with st.spinner("Generando Excel..."):
                    try:
                        files = {'file': st.session_state.uploaded_file.getvalue()}
                        response = requests.post(f"{API}/api/exportar-excel-vacaciones", files=files, timeout=30)

                        if response.status_code == 200:
                            st.download_button(
                                label="⬇️ Descargar",
                                data=response.content,
                                file_name="vacaciones_proporcionales.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    else:
        st.info("📤 Carga un archivo para calcular vacaciones")

# ========== TAB 5: INDIVIDUAL ==========
with tab5:
    st.subheader("👤 Descargar PDF Individual")

    if "resultados" in st.session_state:
        datos = st.session_state.resultados
        empleados = datos['empleados']

        opciones = {f"{e['nombre']} ({e['documento']})": e['documento'] for e in empleados}

        empleado_seleccionado = st.selectbox(
            "Selecciona un empleado:",
            options=list(opciones.keys())
        )

        if empleado_seleccionado:
            documento = opciones[empleado_seleccionado]
            emp = next((e for e in empleados if e['documento'] == documento), None)

            if emp:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Salario", f"${emp['salario_mensual']:,.0f}")
                with col2:
                    st.metric("Devengos", f"${emp['total_devengos']:,.0f}")
                with col3:
                    st.metric("Deducciones", f"${emp['total_deducciones']:,.0f}")
                with col4:
                    st.metric("NETO", f"${emp['neto_pagar']:,.0f}")

                st.divider()

                if "uploaded_file" in st.session_state:
                    if st.button("📄 Descargar PDF", use_container_width=True):
                        with st.spinner("Generando PDF..."):
                            try:
                                files = {'file': st.session_state.uploaded_file.getvalue()}
                                params = {'documento': documento}
                                response = requests.post(
                                    f"{API}/api/exportar-pdf-individual-desde-excel",
                                    files=files,
                                    params=params,
                                    timeout=30
                                )

                                if response.status_code == 200:
                                    st.download_button(
                                        label="⬇️ Descargar PDF",
                                        data=response.content,
                                        file_name=f"{emp['nombre']}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

    else:
        st.info("📤 Carga un archivo para descargar PDFs")

# ========== TAB 6: COMPARATIVA ==========
with tab6:
    st.subheader("📈 Comparativa: Prima vs Vacaciones")

    if "prima_data" in st.session_state and "vacaciones_data" in st.session_state:
        df_prima = pd.DataFrame(st.session_state.prima_data['empleados'])
        df_vaca = pd.DataFrame(st.session_state.vacaciones_data['empleados'])

        # Combinar
        df_comp = pd.DataFrame({
            'Nombre': df_prima['nombre'],
            'Salario': df_prima['salario_mensual'],
            'Prima': df_prima['valor_prima'],
            'Vacaciones': df_vaca['valor_vacaciones'],
            'Total': df_prima['valor_prima'] + df_vaca['valor_vacaciones']
        })

        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Prima", f"${df_prima['valor_prima'].sum():,.0f}")
        with col2:
            st.metric("Total Vacaciones", f"${df_vaca['valor_vacaciones'].sum():,.0f}")
        with col3:
            st.metric("TOTAL", f"${(df_prima['valor_prima'].sum() + df_vaca['valor_vacaciones'].sum()):,.0f}")

    else:
        st.info("⚠️ Calcula Prima y Vacaciones primero para ver la comparativa")

# ========== TAB 7: CONFIGURACIÓN ==========
with tab7:
    st.subheader("⚙️ Configuración")

    # Estado del servidor
    st.write("### Estado del Servidor")
    try:
        response = requests.get(f"{API}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend conectado")
        else:
            st.error("❌ Backend no responde")
    except:
        st.error("❌ No se puede conectar con el backend")

    st.divider()

    st.write("### Estructura del Archivo Excel")
    st.info("""
    **Hoja Empleados (Requerida)**
    - nombre: Nombre del empleado
    - documento: Número de documento
    - salario_mensual: Salario mensual
    - dias_laborados: Días trabajados
    - auxilio_transporte: Auxilio (opcional)

    **Hoja Parámetros (Opcional)**
    - parametro: salud, pension, fondo_solidaridad
    - valor: Porcentaje

    **Hoja Novedades (Opcional)**
    - documento: Documento del empleado
    - tipo_novedad: Tipo (ej: retención)
    - valor: Valor de la novedad
    """)

    st.divider()

    st.write("### Fórmulas Utilizadas")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Prima de Servicios**")
        st.code("(Salario + Auxilio) × Días ÷ 360")

    with col2:
        st.write("**Vacaciones Proporcionales**")
        st.code("Salario × Días ÷ 720")
