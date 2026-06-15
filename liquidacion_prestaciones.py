"""
Liquidación de Prestaciones Sociales
Calcula y genera reporte en PDF de cesantías, prima, vacaciones e intereses
"""

import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from io import BytesIO


def calcular_prestaciones(empleados_df):
    """
    Calcula todas las prestaciones sociales para un grupo de empleados

    Args:
        empleados_df: DataFrame con columnas: documento, nombre, salario_mensual, dias_laborados
                     (También acepta variaciones como 'dias', 'dias_trabajados', etc.)

    Returns:
        DataFrame con cálculo de prestaciones
    """

    prestaciones = []

    # CAMBIO: Mapeo flexible de nombres de columnas
    columnas_documento = ['documento', 'doc', 'cedula', 'id']
    columnas_nombre = ['nombre', 'name', 'empleado']
    columnas_salario = ['salario_mensual', 'salario', 'salary', 'sueldo']
    columnas_dias = ['dias_laborados', 'dias', 'dias_trabajados', 'dias_trabajo', 'days']

    # Obtener nombres de columnas reales
    col_doc = next((col for col in columnas_documento if col in empleados_df.columns), None)
    col_nombre = next((col for col in columnas_nombre if col in empleados_df.columns), None)
    col_salario = next((col for col in columnas_salario if col in empleados_df.columns), None)
    col_dias = next((col for col in columnas_dias if col in empleados_df.columns), None)

    # Validar que todas las columnas existan
    if not col_doc:
        raise ValueError("No se encontró columna de documento (esperado: documento, doc, cedula, id)")
    if not col_nombre:
        raise ValueError("No se encontró columna de nombre (esperado: nombre, name, empleado)")
    if not col_salario:
        raise ValueError("No se encontró columna de salario (esperado: salario_mensual, salario, sueldo)")
    if not col_dias:
        raise ValueError("No se encontró columna de días (esperado: dias_laborados, dias, dias_trabajados)")

    for idx, emp in empleados_df.iterrows():
        documento = str(emp.get(col_doc, '')).strip()
        nombre = str(emp.get(col_nombre, '')).strip()
        salario = float(emp.get(col_salario, 0) or 0)
        dias = float(emp.get(col_dias, 0) or 0)

        # ============================================
        # CESANTÍAS
        # ============================================
        # Fórmula: (Salario × Días) / 360
        cesantias = round((salario * dias) / 360, 2)

        # ============================================
        # INTERESES DE CESANTÍAS
        # ============================================
        # Fórmula: (Cesantías × 12%) / 12 × meses
        # Aproximado: Cesantías × 1% × días/30
        intereses_cesantias = round((cesantias * dias) / 360, 2)

        # ============================================
        # PRIMA DE SERVICIOS
        # ============================================
        # Fórmula: (Salario × Días) / 360
        prima = round((salario * dias) / 360, 2)

        # ============================================
        # VACACIONES PROPORCIONALES
        # ============================================
        # Fórmula: (Salario × Días) / 720
        vacaciones = round((salario * dias) / 720, 2)

        # ============================================
        # TOTAL PRESTACIONES
        # ============================================
        total_prestaciones = cesantias + intereses_cesantias + prima + vacaciones

        prestaciones.append({
            'Documento': documento,
            'Nombre': nombre,
            'Salario Mensual': salario,
            'Días Trabajados': dias,
            'Cesantías': cesantias,
            'Intereses Cesantías': intereses_cesantias,
            'Prima de Servicios': prima,
            'Vacaciones': vacaciones,
            'Total Prestaciones': total_prestaciones
        })

    return pd.DataFrame(prestaciones)


def generar_pdf_prestaciones(df_prestaciones, ruta_salida=None):
    """
    Genera PDF con reporte de prestaciones sociales

    Args:
        df_prestaciones: DataFrame con cálculo de prestaciones
        ruta_salida: Ruta del archivo PDF (si None, retorna BytesIO)

    Returns:
        Ruta del archivo o BytesIO si ruta_salida es None
    """

    if ruta_salida is None:
        pdf_buffer = BytesIO()
    else:
        pdf_buffer = ruta_salida

    # ============================================
    # CREAR DOCUMENTO
    # ============================================
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    # ============================================
    # ESTILOS
    # ============================================
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=1,  # Centro
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=12,
        alignment=1,  # Centro
    )

    normal_style = styles['Normal']

    # ============================================
    # CONTENIDO
    # ============================================
    story = []

    # Título
    story.append(Paragraph("LIQUIDACIÓN DE PRESTACIONES SOCIALES", title_style))

    # Fecha
    fecha = datetime.now().strftime("%d de %B de %Y")
    story.append(Paragraph(f"Generado: {fecha}", subtitle_style))

    story.append(Spacer(1, 0.15*inch))

    # ============================================
    # TABLA DE DATOS
    # ============================================
    data = [
        [
            Paragraph("<b>Documento</b>", normal_style),
            Paragraph("<b>Nombre</b>", normal_style),
            Paragraph("<b>Salario</b>", normal_style),
            Paragraph("<b>Días</b>", normal_style),
            Paragraph("<b>Cesantías</b>", normal_style),
            Paragraph("<b>Int. Cesantías</b>", normal_style),
            Paragraph("<b>Prima</b>", normal_style),
            Paragraph("<b>Vacaciones</b>", normal_style),
            Paragraph("<b>Total</b>", normal_style),
        ]
    ]

    total_cesantias = 0
    total_intereses = 0
    total_prima = 0
    total_vacaciones = 0
    total_general = 0

    for idx, row in df_prestaciones.iterrows():
        data.append([
            Paragraph(str(row['Documento']), normal_style),
            Paragraph(str(row['Nombre']), normal_style),
            Paragraph(f"${row['Salario Mensual']:,.0f}", normal_style),
            Paragraph(f"{row['Días Trabajados']:.0f}", normal_style),
            Paragraph(f"${row['Cesantías']:,.2f}", normal_style),
            Paragraph(f"${row['Intereses Cesantías']:,.2f}", normal_style),
            Paragraph(f"${row['Prima de Servicios']:,.2f}", normal_style),
            Paragraph(f"${row['Vacaciones']:,.2f}", normal_style),
            Paragraph(f"${row['Total Prestaciones']:,.2f}", normal_style),
        ])

        total_cesantias += row['Cesantías']
        total_intereses += row['Intereses Cesantías']
        total_prima += row['Prima de Servicios']
        total_vacaciones += row['Vacaciones']
        total_general += row['Total Prestaciones']

    # Fila de totales
    data.append([
        Paragraph("<b>TOTAL</b>", normal_style),
        Paragraph("", normal_style),
        Paragraph("", normal_style),
        Paragraph("", normal_style),
        Paragraph(f"<b>${total_cesantias:,.2f}</b>", normal_style),
        Paragraph(f"<b>${total_intereses:,.2f}</b>", normal_style),
        Paragraph(f"<b>${total_prima:,.2f}</b>", normal_style),
        Paragraph(f"<b>${total_vacaciones:,.2f}</b>", normal_style),
        Paragraph(f"<b>${total_general:,.2f}</b>", normal_style),
    ])

    # Crear tabla
    table = Table(data, colWidths=[
        0.9*inch,  # Documento
        1.2*inch,  # Nombre
        0.9*inch,  # Salario
        0.6*inch,  # Días
        0.8*inch,  # Cesantías
        0.85*inch,  # Int Cesantías
        0.8*inch,  # Prima
        0.85*inch,  # Vacaciones
        0.8*inch,  # Total
    ])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8E8E8')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F5F5F5')]),
        ('FONTSIZE', (0, 1), (-1, -2), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(table)

    story.append(Spacer(1, 0.2*inch))

    # ============================================
    # RESUMEN
    # ============================================
    resumen_data = [
        ['Concepto', 'Total'],
        ['Cesantías', f'${total_cesantias:,.2f}'],
        ['Intereses Cesantías', f'${total_intereses:,.2f}'],
        ['Prima de Servicios', f'${total_prima:,.2f}'],
        ['Vacaciones', f'${total_vacaciones:,.2f}'],
        ['TOTAL PRESTACIONES', f'${total_general:,.2f}'],
    ]

    resumen_table = Table(resumen_data, colWidths=[3*inch, 1.5*inch])
    resumen_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFE6E6')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9F9F9')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))

    story.append(resumen_table)

    story.append(Spacer(1, 0.3*inch))

    # Footer
    footer_text = "Este documento fue generado automáticamente por el Sistema de Liquidaciones"
    story.append(Paragraph(f"<i><font size=8 color=#999999>{footer_text}</font></i>", styles['Normal']))

    # ============================================
    # GENERAR PDF
    # ============================================
    doc.build(story)

    if ruta_salida is None:
        pdf_buffer.seek(0)
        return pdf_buffer
    else:
        return ruta_salida


# ================================================================
# EJEMPLO DE USO
# ================================================================
if __name__ == "__main__":
    # Datos de ejemplo
    empleados = pd.DataFrame([
        {
            'documento': '1020304050',
            'nombre': 'JUAN GARCÍA PÉREZ',
            'salario_mensual': 2500000,
            'dias_laborados': 180,
        },
        {
            'documento': '1020304051',
            'nombre': 'MARÍA RODRÍGUEZ GARCÍA',
            'salario_mensual': 3000000,
            'dias_laborados': 200,
        },
    ])

    # Calcular prestaciones
    print("📊 Calculando prestaciones sociales...")
    df_prestaciones = calcular_prestaciones(empleados)

    print("\n✅ Resultados:")
    print(df_prestaciones.to_string(index=False))

    # Generar PDF
    print("\n📄 Generando PDF...")
    pdf_bytes = generar_pdf_prestaciones(df_prestaciones)

    # Guardar
    with open("prestaciones_sociales.pdf", "wb") as f:
        f.write(pdf_bytes.getvalue())

    print("✅ PDF generado: prestaciones_sociales.pdf")
