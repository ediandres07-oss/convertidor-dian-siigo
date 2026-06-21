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

# Crear 10 pestañas
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📤 Cargar",
    "📊 Completa",
    "💼 Prima",
    "🏖️ Vacaciones",
    "👤 Individual",
    "📈 Comparativa",
    "🧮 SIIGO",
    "🔄 Convertir TXT",
    "🎓 Prestaciones",
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
                        if "error" in data and data["error"] is not None:
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
                        if "error" in data and data["error"] is not None:
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

            # Botones descargar
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📥 Descargar Excel Prima", use_container_width=True):
                    with st.spinner("Generando Excel..."):
                        try:
                            files = {'file': st.session_state.uploaded_file.getvalue()}
                            response = requests.post(f"{API}/api/exportar-excel-prima", files=files, timeout=30)

                            if response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Descargar Excel",
                                    data=response.content,
                                    file_name="prima_servicios.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            with col2:
                if st.button("📄 Descargar ZIP PDFs Prima", use_container_width=True):
                    with st.spinner("Generando ZIP..."):
                        try:
                            files = {'file': st.session_state.uploaded_file.getvalue()}
                            response = requests.post(f"{API}/api/exportar-pdf-prima-zip", files=files, timeout=30)

                            if response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Descargar ZIP",
                                    data=response.content,
                                    file_name="prima_servicios.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            st.divider()
            st.subheader("📄 Descargar Certificado Individual")

            # Selector de empleado para prima
            empleados_prima = datos['empleados']
            opciones_prima = {f"{e['nombre']} ({e['documento']})": e['documento'] for e in empleados_prima}

            empleado_prima = st.selectbox(
                "Selecciona un empleado:",
                options=list(opciones_prima.keys()),
                key="select_prima_individual"
            )

            if empleado_prima:
                documento_prima = opciones_prima[empleado_prima]
                emp_prima = next((e for e in empleados_prima if e['documento'] == documento_prima), None)

                if emp_prima:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Salario", f"${emp_prima['salario_mensual']:,.0f}")
                    with col2:
                        dias_modificados = st.number_input(
                            "Días Laborados",
                            min_value=1,
                            max_value=360,
                            value=int(emp_prima['dias_laborados']),
                            key=f"dias_prima_{documento_prima}"
                        )
                    with col3:
                        prima_ajustada = ((emp_prima['salario_mensual'] + emp_prima.get('auxilio_transporte', 0)) * dias_modificados) / 360
                        st.metric("Valor Prima", f"${prima_ajustada:,.2f}")

                    # Botón descargar PDF individual
                    if st.button("📋 Descargar Certificado de Prima (Media Carta)",
                                use_container_width=True, type="primary", key="download_prima_cert"):
                        with st.spinner("Generando certificado..."):
                            try:
                                files = {'file': st.session_state.uploaded_file.getvalue()}
                                params = {'documento': documento_prima}
                                response = requests.post(
                                    f"{API}/api/exportar-pdf-prima-individual",
                                    files=files,
                                    params=params,
                                    timeout=30
                                )

                                if response.status_code == 200:
                                    st.download_button(
                                        label="⬇️ Descargar PDF",
                                        data=response.content,
                                        file_name=f"prima_{emp_prima['nombre'].replace(' ', '_')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True,
                                        key="btn_download_prima_cert"
                                    )
                                    st.success("✅ Certificado generado en formato media carta")
                                else:
                                    st.error("Error al generar certificado")
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
                        if "error" in data and data["error"] is not None:
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

            # Botones descargar
            col1, col2 = st.columns(2)

            with col1:
                if st.button("📥 Descargar Excel Vacaciones", use_container_width=True):
                    with st.spinner("Generando Excel..."):
                        try:
                            files = {'file': st.session_state.uploaded_file.getvalue()}
                            response = requests.post(f"{API}/api/exportar-excel-vacaciones", files=files, timeout=30)

                            if response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Descargar Excel",
                                    data=response.content,
                                    file_name="vacaciones_proporcionales.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            with col2:
                if st.button("📄 Descargar ZIP PDFs Vacaciones", use_container_width=True):
                    with st.spinner("Generando ZIP..."):
                        try:
                            files = {'file': st.session_state.uploaded_file.getvalue()}
                            response = requests.post(f"{API}/api/exportar-pdf-vacaciones-zip", files=files, timeout=30)

                            if response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Descargar ZIP",
                                    data=response.content,
                                    file_name="vacaciones_proporcionales.zip",
                                    mime="application/zip",
                                    use_container_width=True
                                )
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            st.divider()
            st.subheader("📄 Descargar Certificado Individual")

            # Selector de empleado para vacaciones
            empleados_vaca = datos['empleados']
            opciones_vaca = {f"{e['nombre']} ({e['documento']})": e['documento'] for e in empleados_vaca}

            empleado_vaca = st.selectbox(
                "Selecciona un empleado:",
                options=list(opciones_vaca.keys()),
                key="select_vacaciones_individual"
            )

            if empleado_vaca:
                documento_vaca = opciones_vaca[empleado_vaca]
                emp_vaca = next((e for e in empleados_vaca if e['documento'] == documento_vaca), None)

                if emp_vaca:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Salario", f"${emp_vaca['salario_mensual']:,.0f}")
                    with col2:
                        dias_modificados_vaca = st.number_input(
                            "Días Laborados",
                            min_value=1,
                            max_value=360,
                            value=int(emp_vaca['dias_laborados']),
                            key=f"dias_vaca_{documento_vaca}"
                        )
                    with col3:
                        vaca_ajustada = (emp_vaca['salario_mensual'] * dias_modificados_vaca) / 720
                        st.metric("Valor Vacaciones", f"${vaca_ajustada:,.2f}")

                    # Botón descargar PDF individual
                    if st.button("📋 Descargar Certificado de Vacaciones (Media Carta)",
                                use_container_width=True, type="primary", key="download_vaca_cert"):
                        with st.spinner("Generando certificado..."):
                            try:
                                files = {'file': st.session_state.uploaded_file.getvalue()}
                                params = {'documento': documento_vaca}
                                response = requests.post(
                                    f"{API}/api/exportar-pdf-vacaciones-individual",
                                    files=files,
                                    params=params,
                                    timeout=30
                                )

                                if response.status_code == 200:
                                    st.download_button(
                                        label="⬇️ Descargar PDF",
                                        data=response.content,
                                        file_name=f"vacaciones_{emp_vaca['nombre'].replace(' ', '_')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True,
                                        key="btn_download_vaca_cert"
                                    )
                                    st.success("✅ Certificado generado en formato media carta")
                                else:
                                    st.error("Error al generar certificado")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")

    else:
        st.info("📤 Carga un archivo para calcular vacaciones")

# ========== TAB 5: INDIVIDUAL - NÓMINA ==========
with tab5:
    st.subheader("👤 Generar Nómina Individual")

    if "resultados" in st.session_state and "uploaded_file" in st.session_state:
        datos = st.session_state.resultados
        empleados = datos['empleados']

        opciones = {f"{e['nombre']} ({e['documento']})": e['documento'] for e in empleados}

        empleado_seleccionado = st.selectbox(
            "Selecciona un empleado para generar nómina:",
            options=list(opciones.keys()),
            key="select_nomina"
        )

        if empleado_seleccionado:
            documento = opciones[empleado_seleccionado]
            emp = next((e for e in empleados if e['documento'] == documento), None)

            if emp:
                st.divider()
                st.subheader(f"📋 Nómina - {emp['nombre']}")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Salario", f"${emp['salario_mensual']:,.0f}")
                with col2:
                    st.metric("Auxilio", f"${emp['auxilio_transporte']:,.0f}")
                with col3:
                    dias_nomina = st.number_input(
                        "Días Laborados",
                        min_value=1,
                        max_value=360,
                        value=int(emp['dias_laborados']),
                        key=f"dias_nomina_{documento}"
                    )
                with col4:
                    salario_dev = (emp['salario_mensual'] / 30) * dias_nomina
                    auxilio_dev = (emp['auxilio_transporte'] / 30) * dias_nomina
                    base = salario_dev + auxilio_dev
                    cesantias = (base * dias_nomina) / 360
                    intereses = (cesantias * 0.12 * dias_nomina) / 360
                    prima = (base * dias_nomina) / 360
                    vacaciones = (salario_dev * dias_nomina) / 720
                    total_dev = salario_dev + auxilio_dev + cesantias + intereses + prima + vacaciones
                    st.metric("Total Devengado", f"${total_dev:,.0f}")

                st.divider()

                # Botón para descargar nómina
                if st.button("📄 Descargar Nómina PDF", use_container_width=True, type="primary", key="download_nomina_pdf"):
                    with st.spinner("Generando nómina..."):
                        try:
                            files = {'file': st.session_state.uploaded_file.getvalue()}
                            params = {'documento': documento}
                            response = requests.post(
                                f"{API}/api/exportar-nomina-individual",
                                files=files,
                                params=params,
                                timeout=30
                            )

                            if response.status_code == 200:
                                st.download_button(
                                    label="⬇️ Descargar PDF",
                                    data=response.content,
                                    file_name=f"nomina_{emp['nombre'].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key="btn_download_nomina"
                                )
                                st.success("✅ Nómina generada correctamente")
                            else:
                                st.error("Error al generar nómina")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    else:
        st.info("📤 Carga un archivo para generar nóminas")

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

# ========== TAB 7: SIIGO ==========
with tab7:
    st.subheader("🧮 Generador de Archivo Plano SIIGO")
    st.write("*Crea archivo plano compatible con SIIGO para cargar asientos contables*")

    if "uploaded_file" in st.session_state:
        st.write("Genera archivos plano con todos los asientos contables de nómina")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📄 Generar TXT", use_container_width=True, key="gen_siigo_txt"):
                with st.spinner("Generando archivo plano TXT..."):
                    try:
                        files = {'file': st.session_state.uploaded_file.getvalue()}
                        response = requests.post(f"{API}/api/generar-plano-siigo", files=files, timeout=30)

                        if response.status_code == 200:
                            st.success("✅ Archivo TXT generado")
                            st.download_button(
                                label="⬇️ Descargar plano_siigo.txt",
                                data=response.content,
                                file_name="plano_siigo.txt",
                                mime="text/plain",
                                use_container_width=True,
                                key="down_txt"
                            )
                        else:
                            st.error("Error al generar archivo")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            if st.button("📊 Generar Excel", use_container_width=True, key="gen_siigo_xlsx"):
                with st.spinner("Generando archivo plano Excel..."):
                    try:
                        files = {'file': st.session_state.uploaded_file.getvalue()}
                        response = requests.post(f"{API}/api/exportar-plano-siigo-excel", files=files, timeout=30)

                        if response.status_code == 200:
                            st.success("✅ Archivo Excel generado")
                            st.download_button(
                                label="⬇️ Descargar plano_siigo.xlsx",
                                data=response.content,
                                file_name="plano_siigo.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True,
                                key="down_xlsx"
                            )
                        else:
                            st.error("Error al generar archivo")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        st.divider()

        st.write("### 📋 Formatos Disponibles")

        tab_txt, tab_xlsx = st.tabs(["📄 Formato TXT", "📊 Formato Excel"])

        with tab_txt:
            st.write("**Archivo separado por punto y coma (;)**")
            st.code(
                "NOMINA;5105;1020304050;Maria Gomez;2200000.00;D;01\n"
                "NOMINA;510530;1020304050;Maria Gomez;183333.33;D;01\n"
                "NOMINA;237005;1020304050;Maria Gomez;88000.00;C;01\n"
                "NOMINA;111005;1020304050;Maria Gomez;2432333.33;C;01",
                language="csv"
            )
            st.write("**Uso:** Carga directa en SIIGO → Importar")

        with tab_xlsx:
            st.write("**Archivo Excel con 4 hojas:**")
            st.markdown("""
            1. **Plano SIIGO** - Asientos en formato tabular
            2. **Resumen** - Balance contable (Débitos = Créditos)
            3. **Por Cuenta** - Agrupado por cuenta contable
            4. **Instrucciones** - Pasos para cargar en SIIGO
            """)
            st.write("**Uso:** Revisar antes de cargar en SIIGO")

        st.write("### 📋 Estructura de Campos")
        st.markdown("""
        1. **TIPO** - Tipo de movimiento (NOMINA)
        2. **CUENTA** - Cuenta contable
           - 5105: Salarios
           - 510530: Cesantías
           - 510533: Intereses Cesantías
           - 510536: Prima
           - 510539: Vacaciones
           - 237005: Salud
           - 238030: Pensión
           - 238095: Fondo Solidaridad
           - 236540: Retención en la Fuente
           - 111005: Bancos (Neto)
        3. **DOCUMENTO** - Cédula del empleado
        4. **NOMBRE** - Nombre del empleado
        5. **VALOR** - Valor del movimiento
        6. **DEBITO_CREDITO** - D (Débito) o C (Crédito)
        7. **CENTRO_COSTOS** - Centro de costos (01)
        8. **CONCEPTO** - Descripción del movimiento
        """)

        st.divider()

        st.write("### 🚀 Cómo Usar en SIIGO")
        st.markdown("""
        1. Descarga el archivo plano desde esta pestaña
        2. Abre SIIGO
        3. Ve a: **Contabilidad → Comprobantes → Importar**
        4. Selecciona el archivo `plano_siigo.txt`
        5. Valida los asientos
        6. Graba el comprobante
        """)

    else:
        st.info("📤 Carga un archivo para generar el plano SIIGO")


# ========== TAB 8: CONVERTIR TXT A EXCEL ==========
with tab8:
    st.subheader("🔄 Convertir Plano TXT a Excel")
    st.write("*Convierte archivo plano SIIGO (TXT) a Excel con validaciones*")

    uploaded_txt = st.file_uploader(
        "Selecciona archivo TXT",
        type=["txt"],
        help="Archivo plano separado por punto y coma (;)"
    )

    if uploaded_txt is not None:
        st.success(f"✅ Archivo cargado: {uploaded_txt.name}")

        if st.button("🔄 Convertir a Excel", use_container_width=True, key="convert_txt"):
            with st.spinner("Convirtiendo archivo..."):
                try:
                    files = {'file': uploaded_txt.getvalue()}
                    response = requests.post(f"{API}/api/convertir-plano-txt-a-excel", files=files, timeout=30)

                    if response.status_code == 200:
                        st.success("✅ Conversión exitosa")
                        st.download_button(
                            label="⬇️ Descargar Excel",
                            data=response.content,
                            file_name="plano_siigo_convertido.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.error("Error al convertir archivo")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

        st.divider()

        st.write("### 📋 Qué Incluye el Excel")
        st.markdown("""
        1. **Plano** - Todos los asientos del archivo original
        2. **Validacion** - Balance contable (Débitos vs Créditos)
        3. **Por Cuenta** - Agrupado por cuenta contable
        4. **Por Empleado** - Agrupado por empleado
        """)

        st.write("### 📊 Formato del Archivo TXT")
        st.code(
            "NOMINA;5105;1020304050;Maria Gomez;2200000.00;D\n"
            "NOMINA;237005;1020304050;Maria Gomez;88000.00;C\n"
            "NOMINA;111005;1020304050;Maria Gomez;2112000.00;C",
            language="csv"
        )

    else:
        st.info("📂 Carga un archivo TXT para convertirlo a Excel")


# ========== TAB 9: LIQUIDACIÓN DE PRESTACIONES SOCIALES ==========
with tab9:
    st.subheader("📋 Liquidación de Prestaciones Sociales")
    st.write("Genera PDF profesional con todas las prestaciones por empleado")

    if "resultados" in st.session_state and "uploaded_file" in st.session_state:
        datos = st.session_state.resultados
        empleados = datos['empleados']

        # Selector de empleado
        opciones = {f"{e['nombre']} ({e['documento']})": e['documento'] for e in empleados}

        empleado_seleccionado = st.selectbox(
            "Selecciona un empleado para generar PDF:",
            options=list(opciones.keys()),
            key="select_prestaciones"
        )

        if empleado_seleccionado:
            documento = opciones[empleado_seleccionado]
            emp = next((e for e in empleados if e['documento'] == documento), None)

            if emp:
                # Mostrar resumen del empleado
                st.divider()
                st.subheader(f"👤 {emp['nombre']}")

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Documento", emp['documento'])
                with col2:
                    st.metric("Salario", f"${emp['salario_mensual']:,.0f}")
                with col3:
                    st.metric("Auxilio", f"${emp['auxilio_transporte']:,.0f}")
                with col4:
                    dias_prest = st.number_input(
                        "Días Laborados",
                        min_value=1,
                        max_value=360,
                        value=int(emp['dias_laborados']),
                        key=f"dias_prest_{documento}"
                    )
                with col5:
                    base_prest = emp['salario_mensual'] + emp['auxilio_transporte']
                    cesantias_prest = (base_prest * dias_prest) / 360
                    intereses_prest = (cesantias_prest * 0.12 * dias_prest) / 360
                    prima_prest = (base_prest * dias_prest) / 360
                    vacaciones_prest = (emp['salario_mensual'] * dias_prest) / 720
                    total_prest = cesantias_prest + intereses_prest + prima_prest + vacaciones_prest
                    st.metric("Total Prestaciones", f"${total_prest:,.0f}")

                st.divider()

                # Desglose de prestaciones
                st.subheader("💰 Desglose de Prestaciones")

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.info(f"**Cesantías**\n\n${cesantias_prest:,.2f}")
                with col2:
                    st.info(f"**Intereses**\n\n${intereses_prest:,.2f}")
                with col3:
                    st.info(f"**Prima**\n\n${prima_prest:,.2f}")
                with col4:
                    st.info(f"**Vacaciones**\n\n${vacaciones_prest:,.2f}")

                st.divider()

                # Botón para descargar PDF
                if st.button("📄 Descargar PDF Liquidación", use_container_width=True, type="primary", key="download_liquidacion_pdf"):
                    with st.spinner("Generando PDF de liquidación..."):
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
                                    file_name=f"liquidacion_{emp['nombre'].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                    key="btn_download_liquidacion"
                                )
                                st.success("✅ PDF generado correctamente")
                            else:
                                st.error("Error al generar PDF")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    else:
        st.info("📤 Carga un archivo primero para generar liquidaciones")


# ========== TAB 10: CONFIGURACIÓN ==========
with tab10:
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

