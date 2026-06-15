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
    st.subheader("🎓 Liquidación de Prestaciones Sociales")
    st.write("Calcula cesantías, prima, vacaciones e intereses - Genera PDF")

    if "uploaded_file" in st.session_state:
        if st.button("🧮 Liquidar Prestaciones", use_container_width=True, key="calc_prestaciones"):
            with st.spinner("Calculando prestaciones..."):
                try:
                    import sys
                    sys.path.insert(0, '/Users/edison/Desktop/proyecto-subir info a siigo nube')
                    from liquidacion_prestaciones import calcular_prestaciones, generar_pdf_prestaciones

                    # Leer archivo
                    excel_file = st.session_state.uploaded_file
                    df_empleados = pd.read_excel(excel_file, sheet_name='Empleados', dtype={'documento': str})

                    # CAMBIO: Validación flexible de columnas
                    columnas_documento = ['documento', 'doc', 'cedula', 'id']
                    columnas_nombre = ['nombre', 'name', 'empleado']
                    columnas_salario = ['salario_mensual', 'salario', 'salary', 'sueldo']
                    columnas_dias = ['dias_laborados', 'dias', 'dias_trabajados', 'dias_trabajo', 'days']
                    # CAMBIO: Agregar columnas de fechas (incluye fecha entrada/retiro)
                    columnas_fecha_inicio = ['fecha_inicio', 'fecha_ingreso', 'start_date', 'fecha_inicio_periodo', 'fecha entrada', 'fecha_entrada']
                    columnas_fecha_fin = ['fecha_fin', 'fecha_salida', 'end_date', 'fecha_fin_periodo', 'fecha_termino', 'fecha retiro', 'fecha_retiro']

                    tiene_doc = any(col in df_empleados.columns for col in columnas_documento)
                    tiene_nombre = any(col in df_empleados.columns for col in columnas_nombre)
                    tiene_salario = any(col in df_empleados.columns for col in columnas_salario)
                    tiene_dias = any(col in df_empleados.columns for col in columnas_dias)
                    # CAMBIO: Verificar fechas
                    tiene_fecha_inicio = any(col in df_empleados.columns for col in columnas_fecha_inicio)
                    tiene_fecha_fin = any(col in df_empleados.columns for col in columnas_fecha_fin)

                    columnas_faltantes = []
                    if not tiene_doc:
                        columnas_faltantes.append(f"documento ({', '.join(columnas_documento)})")
                    if not tiene_nombre:
                        columnas_faltantes.append(f"nombre ({', '.join(columnas_nombre)})")
                    if not tiene_salario:
                        columnas_faltantes.append(f"salario ({', '.join(columnas_salario)})")
                    if not tiene_dias:
                        columnas_faltantes.append(f"días ({', '.join(columnas_dias)})")

                    # CAMBIO: Mostrar advertencia pero permitir continuar con 30 días por defecto
                    if not tiene_dias and (not tiene_fecha_inicio or not tiene_fecha_fin):
                        st.warning(
                            "⚠️ **No se encontró columna de días ni fechas completas**\n\n"
                            "El sistema usará **30 días por defecto** (un mes estándar) para cada empleado.\n\n"
                            "Para cálculo automático, elige una opción:\n"
                            "• **Opción 1:** Agrega columna `dias_laborados` (o `dias`, `dias_trabajados`, etc.)\n"
                            "• **Opción 2:** Agrega AMBAS columnas `fecha_entrada` y `fecha_retiro`\n\n"
                            "**Columnas detectadas en tu archivo:**"
                        )

                        st.divider()
                        for col in df_empleados.columns:
                            st.write(f"• `{col}`")
                    else:
                        # Calcular prestaciones
                        df_prestaciones = calcular_prestaciones(df_empleados)
                        st.session_state.prestaciones_data = df_prestaciones

                        # Mostrar resumen
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            st.metric("👥 Empleados", len(df_prestaciones))
                        with col2:
                            total_cesantias = df_prestaciones['Cesantías'].sum()
                            st.metric("🏦 Cesantías", f"${total_cesantias:,.0f}")
                        with col3:
                            total_intereses = df_prestaciones['Intereses Cesantías'].sum()
                            st.metric("📈 Int. Cesantías", f"${total_intereses:,.0f}")
                        with col4:
                            total_prima = df_prestaciones['Prima de Servicios'].sum()
                            st.metric("💼 Prima", f"${total_prima:,.0f}")
                        with col5:
                            total_vacaciones = df_prestaciones['Vacaciones'].sum()
                            st.metric("🏖️ Vacaciones", f"${total_vacaciones:,.0f}")

                        st.divider()

                        # Total general
                        total_prestaciones = df_prestaciones['Total Prestaciones'].sum()
                        st.info(f"💰 **Total Prestaciones: ${total_prestaciones:,.2f}**")

                        st.divider()

                        # Tabla de detalles
                        st.write("### Detalle por Empleado")
                        df_display = df_prestaciones.copy()
                        st.dataframe(df_display, use_container_width=True, hide_index=True)

                        st.divider()

                        # Botón para descargar PDF
                        st.write("### 📥 Descargar Reporte")
                        if st.button("📄 Descargar PDF", use_container_width=True, key="download_pdf_prestaciones"):
                            try:
                                # Generar PDF
                                pdf_bytes = generar_pdf_prestaciones(df_prestaciones)

                                # Crear botón de descarga
                                st.download_button(
                                    label="⬇️ Descargar Prestaciones.pdf",
                                    data=pdf_bytes,
                                    file_name="prestaciones_sociales.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"❌ Error generando PDF: {str(e)}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.write(traceback.format_exc())

        # Mostrar datos si ya existen
        if "prestaciones_data" in st.session_state:
            df_prestaciones = st.session_state.prestaciones_data

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("👥 Empleados", len(df_prestaciones))
            with col2:
                total_cesantias = df_prestaciones['Cesantías'].sum()
                st.metric("🏦 Cesantías", f"${total_cesantias:,.0f}")
            with col3:
                total_intereses = df_prestaciones['Intereses Cesantías'].sum()
                st.metric("📈 Int. Cesantías", f"${total_intereses:,.0f}")
            with col4:
                total_prima = df_prestaciones['Prima de Servicios'].sum()
                st.metric("💼 Prima", f"${total_prima:,.0f}")
            with col5:
                total_vacaciones = df_prestaciones['Vacaciones'].sum()
                st.metric("🏖️ Vacaciones", f"${total_vacaciones:,.0f}")

            st.divider()

            total_prestaciones = df_prestaciones['Total Prestaciones'].sum()
            st.info(f"💰 **Total Prestaciones: ${total_prestaciones:,.2f}**")

    else:
        st.info("📤 Carga un archivo para calcular prestaciones sociales")


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
