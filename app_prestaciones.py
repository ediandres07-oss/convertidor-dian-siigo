"""
Aplicación Web de Liquidación de Prestaciones Sociales
Interfaz Streamlit para calcular y generar PDF de prestaciones
"""

import streamlit as st
from datetime import datetime, timedelta
from io import BytesIO
import pytz

from calculadora_prestaciones import (
    DatosEmpleado,
    CalculadoraPrestaciones
)
from generador_pdf_prestaciones import GeneradorPDFPrestaciones


# ============================================
# CONFIGURACIÓN DE PÁGINA
# ============================================
st.set_page_config(
    page_title="Liquidación de Prestaciones",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo CSS personalizado
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
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    h1 {
        color: #1f4788;
        text-align: center;
        margin-bottom: 2rem;
    }
    h2 {
        color: #1f4788;
        margin-top: 2rem;
        border-bottom: 2px solid #1f4788;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZAR SESIÓN
# ============================================
if 'resultado' not in st.session_state:
    st.session_state.resultado = None
if 'datos' not in st.session_state:
    st.session_state.datos = None


# ============================================
# TÍTULO Y DESCRIPCIÓN
# ============================================
st.title("💼 Liquidación de Prestaciones Sociales")
st.markdown(
    "Sistema profesional para cálculo y generación de reportes de prestaciones "
    "sociales colombianas (Cesantías, Prima, Vacaciones, Intereses)"
)

st.divider()

# ============================================
# FORMULARIO
# ============================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Datos del Empleado")

    nombre = st.text_input(
        "Nombre completo",
        placeholder="Ej: Juan García Pérez",
        help="Nombre completo del empleado"
    )

    documento = st.text_input(
        "Número de documento",
        placeholder="Ej: 1234567890",
        help="Cédula o documento de identificación"
    )

    cargo = st.text_input(
        "Cargo",
        placeholder="Ej: Gerente General",
        help="Cargo o posición del empleado"
    )

with col2:
    st.subheader("💰 Información Salarial")

    salario = st.number_input(
        "Salario mensual ($)",
        min_value=0.0,
        value=2600000.0,
        step=100000.0,
        help="Salario bruto mensual en pesos colombianos"
    )

    auxilio = st.number_input(
        "Auxilio de transporte ($)",
        min_value=0.0,
        value=140000.0,
        step=10000.0,
        help="Auxilio de transporte mensual (aplica a salarios ≤ 2SMLV)"
    )

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("📅 Fechas Laborales")

    fecha_ingreso = st.date_input(
        "Fecha de ingreso",
        value=datetime.now() - timedelta(days=365),
        help="Fecha en que comenzó a trabajar"
    )

with col4:
    st.subheader("")
    st.write("")  # Espaciador para alineación

    fecha_retiro = st.date_input(
        "Fecha de retiro",
        value=datetime.now(),
        help="Fecha en que termina la relación laboral"
    )

st.divider()

empresa = st.text_input(
    "Nombre de la empresa",
    value="EMPRESA S.A.S",
    help="Nombre de la empresa para incluir en el PDF"
)

# ============================================
# BOTÓN PRINCIPAL
# ============================================
st.markdown("")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    if st.button(
        "✅ LIQUIDAR PRESTACIONES",
        use_container_width=True,
        type="primary",
        key="btn_liquidar"
    ):
        # Validaciones
        errores = []

        if not nombre or not nombre.strip():
            errores.append("⚠️ Ingresa el nombre del empleado")

        if not documento or not documento.strip():
            errores.append("⚠️ Ingresa el número de documento")

        if not cargo or not cargo.strip():
            errores.append("⚠️ Ingresa el cargo")

        if salario <= 0:
            errores.append("⚠️ El salario debe ser mayor a 0")

        if fecha_retiro < fecha_ingreso:
            errores.append("⚠️ La fecha de retiro no puede ser anterior a la de ingreso")

        if errores:
            st.error("\n".join(errores))
        else:
            try:
                # Crear datos del empleado
                datos = DatosEmpleado(
                    nombre=nombre.strip(),
                    documento=documento.strip(),
                    cargo=cargo.strip(),
                    salario_mensual=salario,
                    auxilio_transporte=auxilio,
                    fecha_ingreso=datetime.combine(fecha_ingreso, datetime.min.time()),
                    fecha_retiro=datetime.combine(fecha_retiro, datetime.min.time()),
                    empresa=empresa.strip() if empresa.strip() else "EMPRESA S.A.S"
                )

                # Calcular prestaciones
                calculadora = CalculadoraPrestaciones()
                resultado = calculadora.calcular_prestaciones(datos)

                # Guardar en sesión
                st.session_state.resultado = resultado
                st.session_state.datos = datos

                st.success("✅ Prestaciones calculadas correctamente")

            except ValueError as e:
                st.error(f"❌ Error en los datos: {str(e)}")
            except Exception as e:
                st.error(f"❌ Error al calcular: {str(e)}")

# ============================================
# MOSTRAR RESULTADOS
# ============================================
if st.session_state.resultado:
    resultado = st.session_state.resultado
    datos = st.session_state.datos

    st.divider()
    st.subheader("📊 Resultados del Cálculo")

    # Información resumida
    col_info1, col_info2, col_info3 = st.columns(3)

    with col_info1:
        st.metric(
            "Días Laborados",
            f"{resultado.dias_laborados} días"
        )

    with col_info2:
        st.metric(
            "Salario Base",
            f"${datos.salario_mensual:,.0f}"
        )

    with col_info3:
        st.metric(
            "Total Devengado",
            f"${resultado.total_devengado:,.2f}",
            delta=f"${resultado.neto_pagar:,.2f} neto"
        )

    # Desglose de prestaciones
    st.markdown("#### 📋 Desglose de Prestaciones")

    col_p1, col_p2, col_p3, col_p4 = st.columns(4)

    with col_p1:
        st.info(
            f"**Cesantías**\n\n{CalculadoraPrestaciones.formato_moneda(resultado.cesantias)}"
        )

    with col_p2:
        st.info(
            f"**Intereses**\n\n{CalculadoraPrestaciones.formato_moneda(resultado.intereses_cesantias)}"
        )

    with col_p3:
        st.info(
            f"**Prima Servicios**\n\n{CalculadoraPrestaciones.formato_moneda(resultado.prima_servicios)}"
        )

    with col_p4:
        st.info(
            f"**Vacaciones**\n\n{CalculadoraPrestaciones.formato_moneda(resultado.vacaciones)}"
        )

    # Tabla detallada
    st.markdown("#### 📄 Detalle Completo")

    tabla_datos = {
        "Concepto": [
            "Cesantías",
            "Intereses sobre Cesantías",
            "Prima de Servicios",
            "Vacaciones Proporcionales",
            "TOTAL DEVENGADO",
            "Descuentos",
            "NETO A PAGAR"
        ],
        "Valor": [
            CalculadoraPrestaciones.formato_moneda(resultado.cesantias),
            CalculadoraPrestaciones.formato_moneda(resultado.intereses_cesantias),
            CalculadoraPrestaciones.formato_moneda(resultado.prima_servicios),
            CalculadoraPrestaciones.formato_moneda(resultado.vacaciones),
            CalculadoraPrestaciones.formato_moneda(resultado.total_devengado),
            CalculadoraPrestaciones.formato_moneda(resultado.descuentos),
            CalculadoraPrestaciones.formato_moneda(resultado.neto_pagar)
        ]
    }

    st.dataframe(
        tabla_datos,
        use_container_width=True,
        hide_index=True
    )

    # ============================================
    # GENERAR PDF
    # ============================================
    st.divider()
    st.subheader("📥 Exportar Documento")

    col_pdf1, col_pdf2 = st.columns([2, 1])

    with col_pdf1:
        st.markdown(
            "Haz clic en el botón de descarga para obtener el PDF profesional "
            "listo para imprimir y firmar."
        )

    # Generar PDF
    try:
        generador = GeneradorPDFPrestaciones()
        buffer_pdf = generador.generar_pdf(datos, resultado)

        nombre_archivo = f"Liquidacion_Prestaciones_{datos.nombre.replace(' ', '_')}.pdf"

        st.download_button(
            label="⬇️ Descargar PDF Profesional",
            data=buffer_pdf.getvalue() if isinstance(buffer_pdf, BytesIO) else buffer_pdf,
            file_name=nombre_archivo,
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

        st.success("✅ PDF listo para descargar")

    except Exception as e:
        st.error(f"❌ Error al generar PDF: {str(e)}")

    # Información adicional
    st.divider()
    st.markdown("#### ℹ️ Información Importante")

    with st.expander("📖 Fórmulas Utilizadas"):
        st.markdown("""
        **Según regulaciones colombianas:**

        - **Cesantías** = (Salario + Auxilio) × Días / 360
        - **Intereses Cesantías** = Cesantías × 12% × Días / 360
        - **Prima de Servicios** = (Salario + Auxilio) × Días / 360
        - **Vacaciones** = Salario × Días / 720

        Donde:
        - 360 = días base anual
        - 720 = 2 × 360 (para vacaciones: 15 días anuales)
        - 12% = tasa de intereses anual sobre cesantías
        """)

    with st.expander("⚖️ Notas Legales"):
        st.markdown("""
        Este documento es generado automáticamente y tiene validez como comprobante
        de pago de prestaciones sociales.

        **Validez Legal:**
        - Documento válido en Colombia
        - Cumple con normativa del Ministerio de Trabajo
        - Requiere firma del empleado y empresa

        **Conservación:**
        - El empleador debe guardar una copia
        - El empleado debe mantener una copia
        - Validez: mínimo 2 años
        """)

# ============================================
# INFORMACIÓN EN SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("### 🎯 Sistema de Prestaciones")

    st.markdown("""
    **Módulos incluidos:**
    - Cálculo automático de días
    - Fórmulas colombianas
    - PDF profesional
    - Validaciones integradas

    **Campos calculados:**
    - Cesantías
    - Intereses
    - Prima
    - Vacaciones
    - Total devengado
    - Neto a pagar

    **Diseño:**
    - Interfaz intuitiva
    - Validaciones en tiempo real
    - PDF listo para firma
    """)

    st.divider()

    st.markdown("### 📞 Soporte")
    st.info(
        "Para reportar errores o sugerencias, contacta con el área de "
        "Recursos Humanos."
    )

    st.divider()

    st.markdown(f"### 📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")
