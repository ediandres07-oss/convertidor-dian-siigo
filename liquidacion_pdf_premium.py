"""
Generador Premium de PDF para Acta de Liquidación Definitiva de Contrato Laboral
Con logo, colores personalizados, campos adicionales y preparación para firma digital
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import os


class LiquidacionPDFPremium:
    """Generador avanzado de liquidación laboral con personalización completa."""

    # Colores personalizados
    COLOR_ENCABEZADO = colors.HexColor('#1a3a5c')  # Azul oscuro
    COLOR_TABLA_HEADER = colors.HexColor('#2980b9')  # Azul
    COLOR_TABLA_TOTAL = colors.HexColor('#d6eaf8')  # Azul claro
    COLOR_FIRMA = colors.HexColor('#059669')  # Verde
    COLOR_TEXTO = colors.HexColor('#1a1a1a')  # Negro

    def __init__(self, datos_empleado: dict, datos_liquidacion: dict, logo_path: str = None, empresa_data: dict = None):
        self.datos_empleado = datos_empleado
        self.datos_liquidacion = datos_liquidacion
        self.logo_path = logo_path
        self.empresa_data = empresa_data or {}
        self.buffer = io.BytesIO()

    def generar(self) -> io.BytesIO:
        """Genera el PDF completo."""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            topMargin=0.4*inch,
            bottomMargin=0.4*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        style_title = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=12,
            textColor=self.COLOR_ENCABEZADO,
            alignment=TA_CENTER,
            spaceAfter=4,
            fontName='Helvetica-Bold',
            leading=14
        )

        style_subtitle = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.COLOR_ENCABEZADO,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        style_section = ParagraphStyle(
            'Section',
            parent=styles['Normal'],
            fontSize=9.5,
            textColor=colors.white,
            alignment=TA_LEFT,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            leading=11
        )

        # 1. Encabezado con logo
        encabezado = []
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo = Image(self.logo_path, width=0.8*inch, height=0.8*inch)
                encabezado.append(logo)
            except:
                pass

        empresa_nombre = self.empresa_data.get('nombre', 'EMPRESA GIMÉNEZ ASOCIADOS')
        encabezado_data = [[empresa_nombre]]
        tabla_enc = Table(encabezado_data, colWidths=[6.5*inch])
        tabla_enc.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_ENCABEZADO),
        ]))
        elements.append(tabla_enc)

        # Título principal
        elements.append(Paragraph(
            "ACTA DE LIQUIDACIÓN DEFINITIVA DE CONTRATO LABORAL",
            style_title
        ))
        elements.append(Spacer(1, 0.15*inch))

        # 2. DATOS GENERALES - Mejorado
        elements.append(Paragraph("1. DATOS GENERALES", style_subtitle))

        datos_gen = [
            ['Empleado:', self.datos_empleado.get('nombre', ''), 'C.C./Nit:', self.datos_empleado.get('cedula', '')],
            ['Cargo:', self.datos_empleado.get('cargo', ''), 'Departamento:', self.datos_empleado.get('departamento', '')],
            ['Salario Base Mensual:', f"${self.datos_empleado.get('salario', 0):,.2f}", 'Tipo Contrato:', self.datos_empleado.get('tipo_contrato', 'Indefinido')],
            ['Fecha Inicio Labores:', self.datos_empleado.get('fecha_inicio', ''), 'Fecha Retiro:', self.datos_empleado.get('fecha_retiro', '')],
            ['Días Trabajados:', self.datos_empleado.get('dias_trabajados', ''), 'Periodo Liquidación:', f"{self.datos_empleado.get('fecha_inicio', '')} a {self.datos_empleado.get('fecha_retiro', '')}"],
        ]

        tabla_gen = Table(datos_gen, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        tabla_gen.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 8.5),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 8.5),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_TEXTO),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tabla_gen)
        elements.append(Spacer(1, 0.15*inch))

        # 3. DEVENGOS - Mejorado
        elements.append(Paragraph("2. DEVENGOS DE LIQUIDACIÓN (LEGALES)", style_subtitle))

        devengos = [
            ['Concepto', 'Días', 'Vr. Diario', 'Valor ($)'],
            ['Cesantías', self.datos_liquidacion.get('dias_cesantias', ''), self.datos_liquidacion.get('vr_diario_cesantias', ''), f"${self.datos_liquidacion.get('cesantias', 0):,.2f}"],
            ['Prima de Servicios', self.datos_liquidacion.get('dias_prima', ''), self.datos_liquidacion.get('vr_diario_prima', ''), f"${self.datos_liquidacion.get('prima', 0):,.2f}"],
            ['Vacaciones no Disfrutadas', self.datos_liquidacion.get('dias_vacaciones', ''), self.datos_liquidacion.get('vr_diario_vacaciones', ''), f"${self.datos_liquidacion.get('vacaciones', 0):,.2f}"],
            ['Intereses Cesantías', '', '', f"${self.datos_liquidacion.get('intereses_cesantias', 0):,.2f}"],
        ]

        tabla_dev = Table(devengos, colWidths=[2.5*inch, 0.7*inch, 1*inch, 1.3*inch])
        tabla_dev.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 8.5),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.5),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_TEXTO),
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_TABLA_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tabla_dev)
        elements.append(Spacer(1, 0.1*inch))

        # Total devengos
        total_dev = sum([v for k,v in self.datos_liquidacion.items() if v > 0])
        total_dev_data = [['TOTAL DEVENGOS', '', '', f"${total_dev:,.2f}"]]
        tabla_total_dev = Table(total_dev_data, colWidths=[2.5*inch, 0.7*inch, 1*inch, 1.3*inch])
        tabla_total_dev.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_TABLA_HEADER),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tabla_total_dev)
        elements.append(Spacer(1, 0.15*inch))

        # 4. DEDUCCIONES - Mejorado
        elements.append(Paragraph("3. DEDUCCIONES (A CARGO DEL TRABAJADOR)", style_subtitle))

        deduc = [
            ['Concepto', 'Valor ($)'],
            ['Aporte Pensión', f"${abs(self.datos_liquidacion.get('aporte_pension', 0)):,.2f}"],
            ['Aporte Salud', f"${abs(self.datos_liquidacion.get('aporte_salud', 0)):,.2f}"],
            ['Aporte Fondo Solidaridad', f"${abs(self.datos_liquidacion.get('aporte_solidaridad', 0)):,.2f}"],
            ['Embargos/Retenciones', f"${abs(self.datos_liquidacion.get('embargos', 0)):,.2f}"],
            ['Otras Deducciones', f"${abs(self.datos_liquidacion.get('otros_descuentos', 0)):,.2f}"],
        ]

        tabla_ded = Table(deduc, colWidths=[4.5*inch, 2*inch])
        tabla_ded.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 8.5),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.5),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_TEXTO),
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_TABLA_HEADER),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tabla_ded)
        elements.append(Spacer(1, 0.1*inch))

        # Total deducciones
        total_ded = sum([abs(v) for k,v in self.datos_liquidacion.items() if v < 0])
        total_ded_data = [['TOTAL DEDUCCIONES', f"${total_ded:,.2f}"]]
        tabla_total_ded = Table(total_ded_data, colWidths=[4.5*inch, 2*inch])
        tabla_total_ded.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLOR_TABLA_HEADER),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(tabla_total_ded)
        elements.append(Spacer(1, 0.15*inch))

        # 5. VALOR NETO - Destacado
        elements.append(Paragraph("4. VALOR NETO A RECIBIR (LIQUIDACIÓN DEFINITIVA)", style_subtitle))

        valor_neto = total_dev - total_ded
        neto_data = [
            ['TOTAL DEVENGOS', f"${total_dev:,.2f}"],
            ['(-) TOTAL DEDUCCIONES', f"${total_ded:,.2f}"],
            ['= VALOR NETO A RECIBIR', f"${valor_neto:,.2f}"],
        ]

        tabla_neto = Table(neto_data, colWidths=[4.5*inch, 2*inch])
        tabla_neto.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica-Bold', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (1, 0), self.COLOR_TABLA_HEADER),
            ('BACKGROUND', (0, 1), (1, 1), colors.HexColor('#e74c3c')),  # Rojo para deducciones
            ('BACKGROUND', (0, 2), (1, 2), self.COLOR_FIRMA),  # Verde para total
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(tabla_neto)
        elements.append(Spacer(1, 0.2*inch))

        # 6. DATOS DE PAGO ADICIONALES
        elements.append(Paragraph("5. DATOS DE PAGO", style_subtitle))

        pago_data = [
            ['Método de Pago:', self.datos_empleado.get('metodo_pago', 'Transferencia Bancaria'), 'Banco:', self.datos_empleado.get('banco', '')],
            ['Tipo Cuenta:', self.datos_empleado.get('tipo_cuenta', ''), 'No. Cuenta:', self.datos_empleado.get('numero_cuenta', '')],
        ]

        tabla_pago = Table(pago_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        tabla_pago.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 8.5),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 8.5),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 8.5),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_TEXTO),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ]))
        elements.append(tabla_pago)
        elements.append(Spacer(1, 0.2*inch))

        # 7. CERTIFICACIÓN Y FIRMAS
        elements.append(Paragraph("6. CERTIFICACIÓN Y FIRMAS", style_subtitle))

        cert_text = f"""
        He recibido a mi entera satisfacción la suma de <b>${valor_neto:,.2f}</b> como pago total y definitivo
        de mis acreencias laborales derivadas de mi contrato de trabajo con {self.empresa_data.get('nombre', 'la empresa')},
        declarando queda completamente finiquitada y extinguida toda obligación laboral entre las partes.
        """

        elements.append(Paragraph(cert_text, ParagraphStyle(
            'Cert',
            parent=styles['Normal'],
            fontSize=8.5,
            textColor=self.COLOR_TEXTO,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=10
        )))
        elements.append(Spacer(1, 0.15*inch))

        # Tabla de firmas
        firma_data = [
            ['FIRMA DEL EMPLEADO', '', 'FIRMA DEL EMPLEADOR'],
            ['', '', ''],
            ['_' * 30, '', '_' * 30],
            ['Nombre: ' + self.datos_empleado.get('nombre', ''), '', 'Nombre: ' + self.empresa_data.get('representante', '')],
            ['C.C./Nit: ' + self.datos_empleado.get('cedula', ''), '', 'Nit Empresa: ' + self.empresa_data.get('nit', '')],
            ['Fecha: ' + datetime.now().strftime('%Y-%m-%d'), '', 'Fecha: ' + datetime.now().strftime('%Y-%m-%d')],
        ]

        tabla_firma = Table(firma_data, colWidths=[2.1*inch, 0.3*inch, 2.1*inch])
        tabla_firma.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_TEXTO),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('GRID', (0, 0), (-1, -1), 0, colors.transparent),
        ]))
        elements.append(tabla_firma)

        # Generar PDF
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer


def generar_liquidacion_pdf_premium(datos_empleado: dict, datos_liquidacion: dict, logo_path: str = None, empresa_data: dict = None) -> io.BytesIO:
    """Wrapper para generar PDF premium."""
    generador = LiquidacionPDFPremium(datos_empleado, datos_liquidacion, logo_path, empresa_data)
    return generador.generar()
