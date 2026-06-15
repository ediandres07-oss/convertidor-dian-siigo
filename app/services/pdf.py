"""
Generador de PDF Profesional para Liquidación de Prestaciones
"""

from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os


class GeneradorPDFLiquidacion:
    """Genera PDF profesional de liquidación"""

    COLOR_ENCABEZADO = colors.HexColor('#1f4788')
    COLOR_TOTAL = colors.HexColor('#FFE6E6')
    COLOR_ALTERNADO = colors.HexColor('#F5F5F5')
    MARGEN = 0.5 * inch

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos()

    def _crear_estilos(self):
        """Crea estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='TituloEmpresa',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.COLOR_ENCABEZADO,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.COLOR_ENCABEZADO,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

    def generar_pdf(self, datos: dict, resultados: dict, ruta_salida: str = None) -> bytes:
        """
        Genera PDF de liquidación

        Args:
            datos: Dict con nombre, documento, cargo, salario, auxilio, fechas, empresa
            resultados: Dict con cesantias, intereses, prima, vacaciones, total
            ruta_salida: Ruta para guardar (opcional)

        Returns:
            Bytes del PDF o ruta del archivo
        """
        # Crear buffer
        if ruta_salida:
            buffer = ruta_salida
            # Crear carpeta si no existe
            os.makedirs(os.path.dirname(ruta_salida) if os.path.dirname(ruta_salida) else ".", exist_ok=True)
        else:
            buffer = BytesIO()

        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=self.MARGEN,
            leftMargin=self.MARGEN,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        story = []

        # Encabezado
        empresa = datos.get('empresa', 'EMPRESA S.A.S')
        story.append(Paragraph(empresa, self.styles['TituloEmpresa']))
        story.append(Paragraph("LIQUIDACIÓN DE PRESTACIONES SOCIALES", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2 * inch))

        # Datos del empleado
        datos_empleado = [
            [
                Paragraph("<b>Nombre</b>", self.styles['Normal']),
                Paragraph(datos.get('nombre', ''), self.styles['Normal']),
                Paragraph("<b>Documento</b>", self.styles['Normal']),
                Paragraph(datos.get('documento', ''), self.styles['Normal']),
            ],
            [
                Paragraph("<b>Cargo</b>", self.styles['Normal']),
                Paragraph(datos.get('cargo', ''), self.styles['Normal']),
                Paragraph("<b>Fecha Ingreso</b>", self.styles['Normal']),
                Paragraph(str(datos.get('fecha_ingreso', '')), self.styles['Normal']),
            ],
            [
                Paragraph("<b>Fecha Retiro</b>", self.styles['Normal']),
                Paragraph(str(datos.get('fecha_retiro', '')), self.styles['Normal']),
                Paragraph("<b>Salario</b>", self.styles['Normal']),
                Paragraph(f"${datos.get('salario', 0):,.0f}", self.styles['Normal']),
            ],
        ]

        tabla_datos = Table(datos_empleado, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch])
        tabla_datos.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(tabla_datos)
        story.append(Spacer(1, 0.2 * inch))

        # Tabla de prestaciones
        story.append(Paragraph("<b>PRESTACIONES</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        tabla_prestaciones = [
            [
                Paragraph("<b>CONCEPTO</b>", self.styles['Normal']),
                Paragraph("<b>VALOR</b>", self.styles['Normal']),
            ],
            [
                Paragraph("Cesantías", self.styles['Normal']),
                Paragraph(f"${resultados.get('cesantias', 0):,.2f}", self.styles['Normal']),
            ],
            [
                Paragraph("Intereses Cesantías", self.styles['Normal']),
                Paragraph(f"${resultados.get('intereses', 0):,.2f}", self.styles['Normal']),
            ],
            [
                Paragraph("Prima de Servicios", self.styles['Normal']),
                Paragraph(f"${resultados.get('prima', 0):,.2f}", self.styles['Normal']),
            ],
            [
                Paragraph("Vacaciones", self.styles['Normal']),
                Paragraph(f"${resultados.get('vacaciones', 0):,.2f}", self.styles['Normal']),
            ],
            [
                Paragraph("<b>TOTAL DEVENGADO</b>", self.styles['Normal']),
                Paragraph(f"<b>${resultados.get('total', 0):,.2f}</b>", self.styles['Normal']),
            ],
        ]

        t = Table(tabla_prestaciones, colWidths=[3.5 * inch, 1.75 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ENCABEZADO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), self.COLOR_TOTAL),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, self.COLOR_ALTERNADO]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(t)
        story.append(Spacer(1, 0.3 * inch))

        # Firmas
        story.append(Paragraph("<b>AUTORIZACIÓN Y RECIBIDO</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.15 * inch))

        firmas = [
            [
                Paragraph("_________________________", self.styles['Normal']),
                Paragraph("", self.styles['Normal']),
                Paragraph("_________________________", self.styles['Normal']),
            ],
            [
                Paragraph("Firma del Empleado", self.styles['Normal']),
                Paragraph("", self.styles['Normal']),
                Paragraph("Firma de la Empresa", self.styles['Normal']),
            ],
            [
                Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", self.styles['Normal']),
                Paragraph("", self.styles['Normal']),
                Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", self.styles['Normal']),
            ],
        ]

        tabla_firmas = Table(firmas, colWidths=[1.8 * inch, 0.5 * inch, 1.8 * inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        story.append(tabla_firmas)

        # Construir PDF
        doc.build(story)

        if not ruta_salida:
            buffer.seek(0)
            return buffer.getvalue()
        else:
            return ruta_salida


def generar_pdf_liquidacion(datos: dict, resultados: dict) -> str:
    """
    Función compatible con código anterior

    Args:
        datos: Dict con información del empleado
        resultados: Dict con cálculos de prestaciones

    Returns:
        Ruta del archivo PDF generado
    """
    # Crear carpeta outputs si no existe
    os.makedirs("outputs", exist_ok=True)

    # Generar nombre del archivo
    nombre = datos.get('nombre', 'liquidacion').replace(' ', '_')
    ruta = f"outputs/{nombre}.pdf"

    # Generar PDF
    generador = GeneradorPDFLiquidacion()
    generador.generar_pdf(datos, resultados, ruta)

    return ruta
