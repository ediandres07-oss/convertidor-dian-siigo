import pandas as pd
from typing import List, Dict
from datetime import datetime


def calcular_prima(df_empleados: pd.DataFrame) -> List[Dict]:
    """
    Calcula prima de servicios: (salario + auxilio) * dias / 360
    """
    resultados = []

    for _, emp in df_empleados.iterrows():
        try:
            documento = str(emp.get('documento', ''))
            nombre = str(emp.get('nombre', ''))
            salario = float(emp.get('salario_mensual', 0))
            dias = float(emp.get('dias_laborados', 30))
            auxilio = float(emp.get('auxilio_transporte', 0))

            base_prima = salario + auxilio
            valor_prima = (base_prima * dias) / 360

            resultados.append({
                'nombre': nombre,
                'documento': documento,
                'salario_mensual': round(salario, 2),
                'auxilio_transporte': round(auxilio, 2),
                'dias_laborados': dias,
                'base_prima': round(base_prima, 2),
                'valor_prima': round(valor_prima, 2)
            })
        except Exception as e:
            print(f"Error procesando prima para {emp.get('nombre', 'unknown')}: {str(e)}")
            continue

    return resultados


def calcular_vacaciones(df_empleados: pd.DataFrame) -> List[Dict]:
    """
    Calcula vacaciones proporcionales: salario * dias / 720
    """
    resultados = []

    for _, emp in df_empleados.iterrows():
        try:
            documento = str(emp.get('documento', ''))
            nombre = str(emp.get('nombre', ''))
            salario = float(emp.get('salario_mensual', 0))
            dias = float(emp.get('dias_laborados', 30))

            valor_vacaciones = (salario * dias) / 720

            resultados.append({
                'nombre': nombre,
                'documento': documento,
                'salario_mensual': round(salario, 2),
                'dias_laborados': dias,
                'valor_vacaciones': round(valor_vacaciones, 2)
            })
        except Exception as e:
            print(f"Error procesando vacaciones para {emp.get('nombre', 'unknown')}: {str(e)}")
            continue

    return resultados


def calcular_liquidacion(df_empleados: pd.DataFrame, df_parametros: pd.DataFrame = None, df_novedades: pd.DataFrame = None) -> List[Dict]:
    """
    Calcula liquidación de nómina para empleados

    Parámetros esperados:
    - df_empleados: nombre, documento, salario_mensual, dias_laborados, cesantias_acum, vacaciones_acum
    - df_parametros: aportes (salud%, pensión%, fondo%)
    - df_novedades: documento, tipo_novedad, valor
    """

    resultados = []

    # Configuración por defecto si no se proporcionan parámetros
    parametros = {
        'salud': 0.04,
        'pension': 0.04,
        'fondo_solidaridad': 0.01,
        'dias_ano': 360
    }

    if df_parametros is not None and not df_parametros.empty:
        for _, row in df_parametros.iterrows():
            if 'salud' in str(row.get('parametro', '')).lower():
                parametros['salud'] = float(row.get('valor', 0.04)) / 100
            elif 'pension' in str(row.get('parametro', '')).lower():
                parametros['pension'] = float(row.get('valor', 0.04)) / 100
            elif 'fondo' in str(row.get('parametro', '')).lower():
                parametros['fondo_solidaridad'] = float(row.get('valor', 0.01)) / 100

    # Procesar cada empleado
    for _, emp in df_empleados.iterrows():
        try:
            documento = str(emp.get('documento', ''))
            nombre = str(emp.get('nombre', ''))
            salario = float(emp.get('salario_mensual', 0))
            dias = float(emp.get('dias_laborados', 30))
            cesantias_acum = float(emp.get('cesantias_acum', 0))
            vacaciones_acum = float(emp.get('vacaciones_acum', 0))

            # Calcular devengos
            salario_prorr = (salario * dias) / 30 if dias < 30 else salario

            # Cesantías: se calcula sobre días trabajados
            cesantias = (salario * dias) / parametros['dias_ano']

            # Intereses sobre cesantías: 12% anual
            intereses_cesantias = cesantias * 0.12

            # Prima de servicios: se calcula sobre días trabajados
            prima = (salario * dias) / parametros['dias_ano']

            # Vacaciones: se calcula sobre días trabajados
            vacaciones = (salario * dias) / (parametros['dias_ano'] * 2)

            # Total devengos (sin incluir acumulados)
            total_devengos = salario_prorr + cesantias + intereses_cesantias + prima + vacaciones

            # Calcular deducciones
            salud = salario_prorr * parametros['salud']
            pension = salario_prorr * parametros['pension']

            # Fondo de solidaridad (aplica solo si el salario es mayor a 4 SMMLV aprox)
            fondo_solidaridad = 0
            if salario > 2_000_000:  # Aproximadamente 4 SMMLV
                fondo_solidaridad = salario_prorr * parametros['fondo_solidaridad']

            # Retención en la fuente (por novedades)
            retencion = 0
            if df_novedades is not None and not df_novedades.empty:
                novedad_emp = df_novedades[df_novedades['documento'] == documento]
                if not novedad_emp.empty:
                    for _, nov in novedad_emp.iterrows():
                        if 'retenci' in str(nov.get('tipo_novedad', '')).lower():
                            retencion += float(nov.get('valor', 0))

            total_deducciones = salud + pension + fondo_solidaridad + retencion

            # Neto a pagar
            neto_pagar = total_devengos - total_deducciones

            resultados.append({
                'nombre': nombre,
                'documento': documento,
                'salario_mensual': salario,
                'dias_laborados': dias,
                'salario_prorr': round(salario_prorr, 2),
                'cesantias': round(cesantias, 2),
                'intereses_cesantias': round(intereses_cesantias, 2),
                'prima': round(prima, 2),
                'vacaciones': round(vacaciones, 2),
                'cesantias_acum': round(cesantias_acum, 2),
                'vacaciones_acum': round(vacaciones_acum, 2),
                'salud': round(salud, 2),
                'pension': round(pension, 2),
                'fondo_solidaridad': round(fondo_solidaridad, 2),
                'retencion': round(retencion, 2),
                'total_devengos': round(total_devengos, 2),
                'total_deducciones': round(total_deducciones, 2),
                'neto_pagar': round(neto_pagar, 2)
            })
        except Exception as e:
            print(f"Error procesando empleado {emp.get('nombre', 'unknown')}: {str(e)}")
            continue

    return resultados


def generar_pdf(empleado: Dict, numero_documento: str = "") -> bytes:
    """
    Genera un PDF con la liquidación del empleado
    """
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from io import BytesIO
    from datetime import datetime

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        alignment=1  # centered
    )

    story.append(Paragraph("LIQUIDACIÓN DE NÓMINA", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Información del empleado
    emp_data = [
        ['DATOS DEL EMPLEADO', ''],
        ['Nombre:', empleado.get('nombre', '')],
        ['Documento:', empleado.get('documento', '')],
        ['Salario Mensual:', f"${empleado.get('salario_mensual', 0):,.2f}"],
        ['Días Laborados:', str(empleado.get('dias_laborados', 30))],
    ]

    emp_table = Table(emp_data, colWidths=[2*inch, 4*inch])
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))

    story.append(emp_table)
    story.append(Spacer(1, 0.2*inch))

    # Devengos
    devengos_data = [
        ['DEVENGOS', 'VALOR'],
        ['Salario Prorratead', f"${empleado.get('salario_prorr', 0):,.2f}"],
        ['Cesantías', f"${empleado.get('cesantias', 0):,.2f}"],
        ['Intereses Cesantías', f"${empleado.get('intereses_cesantias', 0):,.2f}"],
        ['Prima', f"${empleado.get('prima', 0):,.2f}"],
        ['Vacaciones', f"${empleado.get('vacaciones', 0):,.2f}"],
    ]

    if empleado.get('cesantias_acum', 0) > 0:
        devengos_data.append(['Cesantías Acumuladas', f"${empleado.get('cesantias_acum', 0):,.2f}"])
    if empleado.get('vacaciones_acum', 0) > 0:
        devengos_data.append(['Vacaciones Acumuladas', f"${empleado.get('vacaciones_acum', 0):,.2f}"])

    devengos_data.append(['TOTAL DEVENGOS', f"${empleado.get('total_devengos', 0):,.2f}"])

    devengos_table = Table(devengos_data, colWidths=[3.5*inch, 2.5*inch])
    devengos_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#d0d0d0')),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))

    story.append(devengos_table)
    story.append(Spacer(1, 0.2*inch))

    # Deducciones
    deducciones_data = [
        ['DEDUCCIONES', 'VALOR'],
        ['Salud (4%)', f"${empleado.get('salud', 0):,.2f}"],
        ['Pensión (4%)', f"${empleado.get('pension', 0):,.2f}"],
    ]

    if empleado.get('fondo_solidaridad', 0) > 0:
        deducciones_data.append(['Fondo Solidaridad (1%)', f"${empleado.get('fondo_solidaridad', 0):,.2f}"])
    if empleado.get('retencion', 0) > 0:
        deducciones_data.append(['Retención en la Fuente', f"${empleado.get('retencion', 0):,.2f}"])

    deducciones_data.append(['TOTAL DEDUCCIONES', f"${empleado.get('total_deducciones', 0):,.2f}"])

    deducciones_table = Table(deducciones_data, colWidths=[3.5*inch, 2.5*inch])
    deducciones_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#c0504d')),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (1, 0), 10),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#d0d0d0')),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f0f0f0')]),
    ]))

    story.append(deducciones_table)
    story.append(Spacer(1, 0.3*inch))

    # Neto a pagar (destacado)
    neto_style = ParagraphStyle(
        'NetoStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2d5016'),
        spaceAfter=10,
        alignment=2  # right aligned
    )

    neto_text = f"NETO A PAGAR: ${empleado.get('neto_pagar', 0):,.2f}"
    story.append(Paragraph(neto_text, neto_style))

    story.append(Spacer(1, 0.2*inch))

    # Pie de página
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1
    )

    story.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
