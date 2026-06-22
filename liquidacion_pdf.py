"""
Generador de PDF para Acta de Liquidación Definitiva de Contrato Laboral
Formato colombiano estándar
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from datetime import datetime
import io


def generar_liquidacion_pdf(datos_empleado: dict, datos_liquidacion: dict) -> io.BytesIO:
    """
    Genera PDF de liquidación laboral en formato colombiano.

    datos_empleado: {
        'nombre': 'Edison Monsalve',
        'cedula': '1234567890',
        'salario': 1880500,
        'fecha_inicio': '2020-01-15',
        'fecha_retiro': '2026-07-21',
        'empresa': 'EMPRESA GIMÉNEZ ASOCIADOS',
        'empresa_nit': '123456789'
    }

    datos_liquidacion: {
        'cesantias': 500000,
        'prima': 450000,
        'vacaciones': 300000,
        'intereses_cesantias': 50000,
        'otros_devengos': 0,
        'aporte_pension': -100000,
        'aporte_salud': -80000,
        'otros_descuentos': 0
    }
    """

    # Crear PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    style_title = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=11,
        textColor=colors.black,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    style_section = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )

    # Encabezado
    title = f"[LOGO EMPRESA] - ACTA DE LIQUIDACIÓN DEFINITIVA DE CONTRATO LABORAL"
    elements.append(Paragraph(title, style_title))
    elements.append(Spacer(1, 0.2*inch))

    # Sección 1: DATOS GENERALES
    elements.append(Paragraph("1. DATOS GENERALES", style_section))

    datos_gen_data = [
        ['Empleado:', datos_empleado.get('nombre', '')],
        ['C.C./Documento Identidad:', datos_empleado.get('cedula', '')],
        ['Salario Mensual (Básico):', f"${datos_empleado.get('salario', 0):,.2f}"],
        ['Fecha Inicio:', datos_empleado.get('fecha_inicio', '')],
        ['Fecha Retiro:', datos_empleado.get('fecha_retiro', '')],
        ['Periodo de Liquidación:', f"{datos_empleado.get('fecha_inicio', '')} a {datos_empleado.get('fecha_retiro', '')}"],
    ]

    table_gen = Table(datos_gen_data, colWidths=[2.5*inch, 3.5*inch])
    table_gen.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    elements.append(table_gen)
    elements.append(Spacer(1, 0.2*inch))

    # Sección 2: DEVENGOS DE LIQUIDACIÓN
    elements.append(Paragraph("2. DEVENGOS DE LIQUIDACIÓN (LEGALES)", style_section))

    devengos_data = [
        ['Concepto', 'Valor ($)'],
        ['Cesantías', f"${datos_liquidacion.get('cesantias', 0):,.2f}"],
        ['Prima de Servicios', f"${datos_liquidacion.get('prima', 0):,.2f}"],
        ['Vacaciones no Disfrutadas', f"${datos_liquidacion.get('vacaciones', 0):,.2f}"],
        ['Intereses sobre Cesantías', f"${datos_liquidacion.get('intereses_cesantias', 0):,.2f}"],
        ['', ''],
        ['TOTAL DEVENGOS', f"${sum([v for k,v in datos_liquidacion.items() if 'cesantias' in k or 'prima' in k or 'vacaciones' in k or 'intereses' in k]):,.2f}"],
    ]

    table_dev = Table(devengos_data, colWidths=[3.5*inch, 2.5*inch])
    table_dev.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    elements.append(table_dev)
    elements.append(Spacer(1, 0.2*inch))

    # Sección 3: DEDUCCIONES
    elements.append(Paragraph("3. DEDUCCIONES (A CARGO DEL TRABAJADOR)", style_section))

    deduc_data = [
        ['Concepto', 'Valor ($)'],
        ['Aporte Pensión', f"${abs(datos_liquidacion.get('aporte_pension', 0)):,.2f}"],
        ['Aporte Salud', f"${abs(datos_liquidacion.get('aporte_salud', 0)):,.2f}"],
        ['Otros Descuentos', f"${abs(datos_liquidacion.get('otros_descuentos', 0)):,.2f}"],
        ['', ''],
        ['TOTAL DEDUCCIONES', f"${sum([abs(v) for k,v in datos_liquidacion.items() if v < 0]):,.2f}"],
    ]

    table_ded = Table(deduc_data, colWidths=[3.5*inch, 2.5*inch])
    table_ded.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 9),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    elements.append(table_ded)
    elements.append(Spacer(1, 0.2*inch))

    # Sección 4: VALOR NETO A RECIBIR
    elements.append(Paragraph("4. VALOR NETO A RECIBIR (LIQUIDACIÓN DEFINITIVA)", style_section))

    total_dev = sum([v for k,v in datos_liquidacion.items() if v > 0])
    total_ded = sum([abs(v) for k,v in datos_liquidacion.items() if v < 0])
    valor_neto = total_dev - total_ded

    resumen_data = [
        ['TOTAL DEVENGOS', f"${total_dev:,.2f}"],
        ['TOTAL DEDUCCIONES', f"${total_ded:,.2f}"],
        ['VALOR NETO A RECIBIR', f"${valor_neto:,.2f}"],
    ]

    table_res = Table(resumen_data, colWidths=[3.5*inch, 2.5*inch])
    table_res.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
    ]))
    elements.append(table_res)
    elements.append(Spacer(1, 0.3*inch))

    # Sección 5: CERTIFICACIÓN Y FIRMAS
    elements.append(Paragraph("5. CERTIFICACIÓN Y FIRMAS", style_section))
    text_cert = f"He recibido a mi entera satisfacción el pago total y definitivo de mis acreencias laborales por el valor de ${valor_neto:,.2f} como pago total y definitivo de mis acreencias laborales."
    elements.append(Paragraph(text_cert, styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    firma_data = [
        ['Firma del Empleado', 'Firma del Empleador/Representante'],
        ['', ''],
        ['Nombre: ' + datos_empleado.get('nombre', ''), 'Empresa: ' + datos_empleado.get('empresa', '')],
        ['Fecha:', f"Fecha: {datetime.now().strftime('%Y-%m-%d')}"],
    ]

    table_firm = Table(firma_data, colWidths=[3.25*inch, 3.25*inch])
    table_firm.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
        ('ALIGN', (0, 0), (-1, 3), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table_firm)

    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
