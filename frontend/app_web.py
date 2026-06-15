"""
Frontend Web - Liquidación de Prestaciones Sociales
Interfaz Streamlit conectada con API FastAPI
"""

import streamlit as st
from datetime import datetime, timedelta
import requests
import pandas as pd
from io import BytesIO

# ============================================
# CONFIGURACIÓN
# ============================================
st.set_page_config(
    page_title="Liquidación de Prestaciones",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL del backend
API_URL = "http://localhost:8000/api"

# Estilos CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 10px;
    }
    h1 {
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# SESIÓN
# ============================================
if 'resultado' not in st.session_state:
    st.session_state.resultado = None
if 'datos' not in st.session_state:
    st.session_state.datos = None


# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.title("⚙️ Configuración")
    modo = st.radio(
        "Modo de operación:",
        ["Liquidación Individual", "Calcular Prestaciones", "Ver Liquidaciones"]
    )

    st.divider()

    st.markdown("### 📊 Información")
    st.info(
        "**Sistema de Liquidación de Prestaciones Sociales**\n\n"
        "Calcula cesantías, prima, vacaciones e intereses según "
        "regulaciones colombianas."
    )


# ============================================
# PÁGINA PRINCIPAL
# ============================================
st.title("💼 Liquidación de Prestaciones Sociales")
st.markdown(
    "Sistema profesional para cálculo de prestaciones con generación automática de PDF"
)

st.divider()


# ============================================
# MODO 1: LIQUIDACIÓN INDIVIDUAL
# ============================================
if modo == "Liquidación Individual":
    st.subheader("📝 Datos del Empleado")

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre completo", placeholder="Juan García Pérez")
        documento = st.text_input("Número de documento", placeholder="1234567890")
        cargo = st.text_input("Cargo", placeholder="Gerente")

    with col2:
        salario = st.number_input(
            "Salario mensual ($)",
            min_value=0.0,
            value=2600000.0,
            step=100000.0
        )
        auxilio = st.number_input(
            "Auxilio de transporte ($)",
            min_value=0.0,
            value=140000.0,
            step=10000.0
        )
        empresa = st.text_input("Empresa", value="EMPRESA S.A.S")

    st.divider()

    st.subheader("📅 Fechas Laborales")

    col3, col4 = st.columns(2)

    with col3:
        fecha_ingreso = st.date_input(
            "Fecha de ingreso",
            value=datetime.now() - timedelta(days=365)
        )

    with col4:
        fecha_retiro = st.date_input(
            "Fecha de retiro",
            value=datetime.now()
        )

    st.divider()

    # Botón principal
    if st.button("✅ LIQUIDAR PRESTACIONES", use_container_width=True, type="primary"):
        # Validaciones
        errores = []
        if not nombre:
            errores.append("Ingresa el nombre")
        if not documento:
            errores.append("Ingresa el documento")
        if not cargo:
            errores.append("Ingresa el cargo")
        if salario <= 0:
            errores.append("El salario debe ser mayor a 0")
        if fecha_retiro < fecha_ingreso:
            errores.append("La fecha de retiro no puede ser anterior a ingreso")

        if errores:
            st.error("\n".join(["⚠️ " + e for e in errores]))
        else:
            # Llamar API
            try:
                with st.spinner("Liquidando prestaciones..."):
                    payload = {
                        "nombre": nombre,
                        "documento": documento,
                        "cargo": cargo,
                        "salario": salario,
                        "auxilio": auxilio,
                        "fecha_ingreso": fecha_ingreso.strftime("%Y-%m-%d"),
                        "fecha_retiro": fecha_retiro.strftime("%Y-%m-%d"),
                        "empresa": empresa
                    }

                    response = requests.post(
                        f"{API_URL}/liquidar-individual",
                        json=payload,
                        timeout=10
                    )

                    if response.status_code == 200:
                        resultado = response.json()
                        st.session_state.resultado = resultado
                        st.session_state.datos = payload

                        st.success("✅ Prestaciones calculadas correctamente")

                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Error desconocido')}")

            except requests.exceptions.ConnectionError:
                st.error("❌ No se puede conectar con el backend. Asegúrate de que esté corriendo en puerto 8000")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    # Mostrar resultados
    if st.session_state.resultado:
        resultado = st.session_state.resultado
        datos = st.session_state.datos

        st.divider()
        st.subheader("📊 Resultados")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Días Laborados", f"{resultado['dias_laborados']} días")

        with col2:
            st.metric("Salario", f"${datos['salario']:,.0f}")

        with col3:
            st.metric("Total Devengado", f"${resultado['total_devengado']:,.2f}")

        with col4:
            st.metric("Neto a Pagar", f"${resultado['neto_pagar']:,.2f}",
                     delta=f"-${resultado['total_devengado'] - resultado['neto_pagar']:,.2f}")

        st.divider()
        st.subheader("💰 Desglose de Prestaciones")

        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            st.info(
                f"**Cesantías**\n\n${resultado['cesantias']:,.2f}"
            )

        with col_p2:
            st.info(
                f"**Intereses**\n\n${resultado['intereses_cesantias']:,.2f}"
            )

        with col_p3:
            st.info(
                f"**Prima**\n\n${resultado['prima_servicios']:,.2f}"
            )

        with col_p4:
            st.info(
                f"**Vacaciones**\n\n${resultado['vacaciones']:,.2f}"
            )

        st.divider()

        # Descargar PDF
        if resultado.get('pdf'):
            try:
                with open(resultado['pdf'], 'rb') as f:
                    pdf_data = f.read()

                st.download_button(
                    label="⬇️ Descargar PDF",
                    data=pdf_data,
                    file_name=f"Liquidacion_{datos['nombre'].replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
                st.success("📄 PDF generado y listo para descargar")

            except FileNotFoundError:
                st.warning("El archivo PDF no se encontró")


# ============================================
# MODO 2: CALCULAR PRESTACIONES
# ============================================
elif modo == "Calcular Prestaciones":
    st.subheader("🧮 Calculadora Rápida de Prestaciones")

    col1, col2, col3 = st.columns(3)

    with col1:
        salario = st.number_input("Salario ($)", value=2600000, step=100000)

    with col2:
        auxilio = st.number_input("Auxilio ($)", value=140000, step=10000)

    with col3:
        dias = st.number_input("Días laborados", value=30, min_value=1)

    if st.button("Calcular", use_container_width=True, type="primary"):
        try:
            response = requests.post(
                f"{API_URL}/calcular-prestaciones",
                params={
                    "salario": salario,
                    "auxilio": auxilio,
                    "dias": dias
                },
                timeout=10
            )

            if response.status_code == 200:
                resultado = response.json()

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Cesantías", f"${resultado['cesantias']:,.2f}")

                with col2:
                    st.metric("Intereses", f"${resultado['intereses_cesantias']:,.2f}")

                with col3:
                    st.metric("Prima", f"${resultado['prima_servicios']:,.2f}")

                with col4:
                    st.metric("Vacaciones", f"${resultado['vacaciones']:,.2f}")

                st.success(f"**Total: ${resultado['neto_pagar']:,.2f}**")

            else:
                st.error("Error al calcular")

        except requests.exceptions.ConnectionError:
            st.error("❌ No se puede conectar con el backend")


# ============================================
# MODO 3: VER LIQUIDACIONES
# ============================================
elif modo == "Ver Liquidaciones":
    st.subheader("📂 Liquidaciones Generadas")

    try:
        response = requests.get(f"{API_URL}/liquidaciones", timeout=10)

        if response.status_code == 200:
            datos = response.json()
            archivos = datos.get('archivos', [])

            if archivos:
                st.success(f"✅ Total de liquidaciones: {len(archivos)}")

                for archivo in archivos:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"📄 {archivo}")

                    with col2:
                        if st.button("📥", key=archivo):
                            try:
                                with open(f"outputs/{archivo}", 'rb') as f:
                                    st.download_button(
                                        "Descargar",
                                        f.read(),
                                        file_name=archivo,
                                        mime="application/pdf"
                                    )
                            except:
                                st.error("Error al descargar")

            else:
                st.info("No hay liquidaciones generadas aún")

        else:
            st.error("Error al obtener liquidaciones")

    except requests.exceptions.ConnectionError:
        st.error("❌ No se puede conectar con el backend")


# ============================================
# FOOTER
# ============================================
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "**Sistema de Liquidación de Prestaciones**\n\n"
        "✅ Cálculos colombianos\n"
        "✅ PDF profesional\n"
        "✅ Almacenamiento automático"
    )

with col2:
    st.markdown(
        "**Prestaciones Incluidas**\n\n"
        "• Cesantías\n"
        "• Intereses\n"
        "• Prima\n"
        "• Vacaciones"
    )

with col3:
    st.markdown(
        f"**Estado del Sistema**\n\n"
        f"Backend: [Verificar](http://localhost:8000/docs)\n"
        f"Fecha: {datetime.now().strftime('%d/%m/%Y')}\n"
        f"Hora: {datetime.now().strftime('%H:%M:%S')}"
    )
