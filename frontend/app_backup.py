import streamlit as st
import requests
import pandas as pd
import io
import time

API_URL = "http://127.0.0.1:8000"

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
    st.write("Use este panel para cargar su archivo Excel con las siguientes hojas:")
    st.info("""
    **Hojas requeridas:**
    - **Empleados**: nombre, documento, salario_mensual, dias_laborados

    **Hojas opcionales:**
    - **Parametros**: salud, pension, fondo_solidaridad
    - **Novedades**: documento, tipo_novedad, valor
    """)

# Área principal
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📤 Cargar Archivo",
    "📊 Liquidación Completa",
    "💼 Prima Servicios",
    "🏖️ Vacaciones",
    "👤 Individual",
    "📈 Comparativas",
    "⚙️ Configuración"
])

# TAB 1: Cargar Archivo
with tab1:
    st.subheader("Carga tu archivo Excel")

    uploaded_file = st.file_uploader(
        "Selecciona un archivo Excel (.xlsx)",
        type=["xlsx", "xls"],
        help="El archivo debe contener al menos la hoja 'Empleados'"
    )

    if uploaded_file is not None:
        # Guardar el archivo en sesión
        st.session_state.uploaded_file = uploaded_file
        st.session_state.archivo_name = uploaded_file.name

        # Mostrar información del archivo
        st.success(f"✅ Archivo cargado: {uploaded_file.name}")

        # Crear dos columnas
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔍 Procesar Archivo", key="process_btn", use_container_width=True):
                with st.spinner("Procesando archivo..."):
                    try:
                        # Hacer request al API
                        files = {'file': uploaded_file.getvalue()}
                        response = requests.post(
                            f"{API_URL}/api/procesar-completo",
                            files=files,
                            timeout=30
                        )

                        if response.status_code == 200:
                            data = response.json()
                            if "error" in data:
                                st.error(f"❌ Error: {data['error']}")
                            else:
                                st.session_state.resultados = data
                                st.success(f"✅ Procesado exitosamente!")
                                st.info(f"📊 Total empleados: {data['total_empleados']} | Total neto: ${data['total_neto']:,.2f}")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error(f"Error en el servidor: {response.status_code}")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ No se puede conectar con el servidor. ¿Está corriendo el backend en puerto 8000?")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        with col2:
            # Mostrar vista previa del archivo
            if st.button("👁️ Ver Vista Previa", key="preview_btn", use_container_width=True):
                st.write("**Vista previa de datos:**")
                try:
                    df = pd.read_excel(uploaded_file, sheet_name='Empleados')
                    st.dataframe(df.head(10), use_container_width=True)
                except Exception as e:
                    st.error(f"Error al leer archivo: {e}")

        st.divider()

        # Descargas rápidas
        st.subheader("📥 Descargar Resultados")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📊 Excel Consolidado", key="download_excel", use_container_width=True):
                with st.spinner("Generando Excel..."):
                    try:
                        files = {'file': uploaded_file.getvalue()}
                        response = requests.post(
                            f"{API_URL}/api/exportar-excel-desde-excel",
                            files=files,
                            timeout=30
                        )

                        if response.status_code == 200:
                            st.download_button(
                                label="⬇️ Descargar Excel",
                                data=response.content,
                                file_name="liquidaciones.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        else:
                            st.error("Error al generar Excel")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col2:
            if st.button("📄 ZIP de PDFs", key="download_zip", use_container_width=True):
                with st.spinner("Generando ZIP..."):
                    try:
                        files = {'file': uploaded_file.getvalue()}
                        response = requests.post(
                            f"{API_URL}/api/exportar-pdf-zip-desde-excel",
                            files=files,
                            timeout=30
                        )

                        if response.status_code == 200:
                            st.download_button(
                                label="⬇️ Descargar ZIP",
                                data=response.content,
                                file_name="liquidaciones.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                        else:
                            st.error("Error al generar ZIP")

                    except Exception as e:
                        st.error(f"Error: {str(e)}")

        with col3:
            st.info("💡 Ve a la pestaña 'Individual' para descargar un PDF específico")


# TAB 2: Resultados
with tab2:
    st.subheader("📊 Resultados de la Liquidación")

    if "resultados" in st.session_state:
        datos = st.session_state.resultados

        # Métricas globales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👥 Total Empleados", datos['total_empleados'])

        with col2:
            total_devengos = sum(e['total_devengos'] for e in datos['empleados'])
            st.metric("💰 Total Devengos", f"${total_devengos:,.2f}")

        with col3:
            total_deducciones = sum(e['total_deducciones'] for e in datos['empleados'])
            st.metric("📉 Total Deducciones", f"${total_deducciones:,.2f}")

        with col4:
            st.metric("💵 Total Neto", f"${datos['total_neto']:,.2f}")

        st.divider()

        # Tabla detallada
        st.subheader("📋 Detalle por Empleado")

        df_display = pd.DataFrame(datos['empleados'])

        # Seleccionar columnas importantes para mostrar
        cols_display = ['nombre', 'documento', 'salario_mensual', 'dias_laborados',
                        'total_devengos', 'total_deducciones', 'neto_pagar']

        df_show = df_display[cols_display].copy()
        df_show.columns = ['Nombre', 'Documento', 'Salario', 'Días', 'Devengos', 'Deducciones', 'Neto']

        # Formatear números
        for col in ['Salario', 'Devengos', 'Deducciones', 'Neto']:
            df_show[col] = df_show[col].apply(lambda x: f"${x:,.2f}")

        st.dataframe(df_show, use_container_width=True, hide_index=True)

        # Opciones de búsqueda
        st.divider()
        st.subheader("🔍 Búsqueda Avanzada")

        search_term = st.text_input("Buscar por nombre o documento:", placeholder="Ej: Juan García")

        if search_term:
            df_filtered = df_display[
                (df_display['nombre'].str.contains(search_term, case=False)) |
                (df_display['documento'].str.contains(search_term))
            ]

            if not df_filtered.empty:
                st.write(f"Se encontraron {len(df_filtered)} coincidencias:")
                st.dataframe(df_filtered[cols_display], use_container_width=True, hide_index=True)
            else:
                st.warning("No se encontraron resultados")

    else:
        st.info("📤 Carga un archivo en la pestaña 'Cargar Archivo' para ver los resultados")


# TAB 3: Individual
with tab3:
    st.subheader("👤 Descargar PDF Individual")

    if "resultados" in st.session_state:
        datos = st.session_state.resultados
        empleados = datos['empleados']

        # Crear lista de opciones
        opciones = {f"{e['nombre']} ({e['documento']})": e['documento'] for e in empleados}

        empleado_seleccionado = st.selectbox(
            "Selecciona un empleado:",
            options=list(opciones.keys()),
            help="Elige el empleado del que deseas descargar el PDF"
        )

        if empleado_seleccionado:
            documento = opciones[empleado_seleccionado]

            # Encontrar empleado en los resultados
            emp = next((e for e in empleados if e['documento'] == documento), None)

            if emp:
                # Mostrar información del empleado
                st.write("### Información del Empleado")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Nombre", emp['nombre'])
                with col2:
                    st.metric("Documento", emp['documento'])
                with col3:
                    st.metric("Salario", f"${emp['salario_mensual']:,.2f}")
                with col4:
                    st.metric("Días", int(emp['dias_laborados']))

                st.divider()

                # Mostrar liquidación
                st.write("### Liquidación")

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**DEVENGOS**")
                    st.write(f"- Salario Prorrateado: ${emp['salario_prorr']:,.2f}")
                    st.write(f"- Cesantías: ${emp['cesantias']:,.2f}")
                    st.write(f"- Intereses: ${emp['intereses_cesantias']:,.2f}")
                    st.write(f"- Prima: ${emp['prima']:,.2f}")
                    st.write(f"- Vacaciones: ${emp['vacaciones']:,.2f}")
                    st.write(f"**Total: ${emp['total_devengos']:,.2f}**")

                with col2:
                    st.write("**DEDUCCIONES**")
                    st.write(f"- Salud: ${emp['salud']:,.2f}")
                    st.write(f"- Pensión: ${emp['pension']:,.2f}")
                    if emp['fondo_solidaridad'] > 0:
                        st.write(f"- Fondo Solidaridad: ${emp['fondo_solidaridad']:,.2f}")
                    if emp['retencion'] > 0:
                        st.write(f"- Retención: ${emp['retencion']:,.2f}")
                    st.write(f"**Total: ${emp['total_deducciones']:,.2f}**")

                st.divider()

                # Botón para descargar PDF
                if "uploaded_file" in st.session_state:
                    if st.button("📄 Descargar PDF Individual", key="pdf_individual", use_container_width=True):
                        with st.spinner("Generando PDF..."):
                            try:
                                files = {'file': st.session_state.uploaded_file.getvalue()}
                                params = {'documento': documento}
                                response = requests.post(
                                    f"{API_URL}/api/exportar-pdf-individual-desde-excel",
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
                                else:
                                    st.error("Error al generar PDF")

                            except Exception as e:
                                st.error(f"Error: {str(e)}")

                st.metric("NETO A PAGAR", f"${emp['neto_pagar']:,.2f}", delta=None)

    else:
        st.info("📤 Carga un archivo en la pestaña 'Cargar Archivo' para descargar PDFs individuales")


# TAB 4: Configuración
with tab4:
    st.subheader("⚙️ Configuración del Sistema")

    st.write("### Estado del Servidor")

    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ Backend conectado correctamente")
        else:
            st.error("❌ Backend no responde correctamente")
    except requests.exceptions.ConnectionError:
        st.error("❌ No se puede conectar con el backend en http://127.0.0.1:8000")
        st.info("Asegúrate de ejecutar el servidor con: `uvicorn backend.main:app --reload`")

    st.divider()

    st.write("### Estructura de Archivos Excel")

    st.write("#### Hoja: Empleados (Requerida)")
    st.dataframe(
        pd.DataFrame({
            'Columna': ['nombre', 'documento', 'salario_mensual', 'dias_laborados', 'cesantias_acum', 'vacaciones_acum'],
            'Tipo': ['Texto', 'Texto/Número', 'Número', 'Número', 'Número', 'Número'],
            'Descripción': [
                'Nombre del empleado',
                'Número de documento',
                'Salario mensual',
                'Días laborados en el período',
                'Cesantías acumuladas',
                'Vacaciones acumuladas'
            ]
        }),
        use_container_width=True,
        hide_index=True
    )

    st.write("#### Hoja: Parametros (Opcional)")
    st.dataframe(
        pd.DataFrame({
            'Columna': ['parametro', 'valor'],
            'Ejemplo': ['salud', '4']
        }),
        use_container_width=True,
        hide_index=True
    )

    st.write("#### Hoja: Novedades (Opcional)")
    st.dataframe(
        pd.DataFrame({
            'Columna': ['documento', 'tipo_novedad', 'valor'],
            'Ejemplo': ['12345678', 'retencion', '50000']
        }),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.write("### Cálculos Realizados")
    st.info("""
    - **Cesantías**: (Salario × Días) / 360
    - **Intereses Cesantías**: Cesantías × 12%
    - **Prima de Servicios**: (Salario × Días) / 360
    - **Vacaciones**: (Salario × Días) / 720
    - **Salud**: Salario × 4%
    - **Pensión**: Salario × 4%
    - **Fondo de Solidaridad**: Salario × 1% (si aplica)
    - **NETO**: Total Devengos - Total Deducciones
    """)
