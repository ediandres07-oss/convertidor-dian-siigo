"""
Generador de PDF Profesional para Liquidación de Prestaciones
Crea documentos PDF legalizado con formato de empresa
"""

from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from calculadora_prestaciones import DatosEmpleado, ResultadosPrestaciones, CalculadoraPrestaciones


class GeneradorPDFPrestaciones:
    """Genera PDF profesional de liquidación de prestaciones"""

    # Configuración de estilos
    MARGEN = 0.5 * inch
    ANCHO_PAGINA = letter[0] - (2 * MARGEN)
    COLOR_ENCABEZADO = colors.HexColor('#1f4788')
    COLOR_TOTAL = colors.HexColor('#FFE6E6')
    COLOR_ALTERNADO = colors.HexColor('#F5F5F5')

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()

    def _crear_estilos_personalizados(self):
        """Crea estilos personalizados para el documento"""
        self.styles.add(ParagraphStyle(
            name='TituloEmpresa',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.COLOR_ENCABEZADO,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.COLOR_ENCABEZADO,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Firma',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            spaceAfter=2,
            alignment=TA_CENTER
        ))

    def generar_pdf(
        self,
        datos: DatosEmpleado,
        resultados: ResultadosPrestaciones,
        ruta_salida: str = None
    ) -> BytesIO:
        """
        Genera el PDF de liquidación de prestaciones

        Args:
            datos: DatosEmpleado con información del empleado
            resultados: ResultadosPrestaciones con cálculos
            ruta_salida: Ruta para guardar (opcional, devuelve BytesIO si no)

        Returns:
            BytesIO con contenido PDF
        """
        if ruta_salida:
            buffer = ruta_salida
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

        # Contenido del documento
        story = []

        # ============ ENCABEZADO ============
        story.append(Paragraph(datos.empresa, self.styles['TituloEmpresa']))
        story.append(Paragraph("LIQUIDACIÓN DE PRESTACIONES SOCIALES", self.styles['Subtitulo']))
        story.append(Spacer(1, 0.2 * inch))

        # ============ INFORMACIÓN DEL EMPLEADO ============
        story.append(Paragraph("DATOS DEL EMPLEADO", self.styles['Seccion']))

        fecha_generacion = datetime.now()
        datos_empleado = [
            ["Campo", "Valor", "Campo", "Valor"],
            [
                Paragraph("<b>Nombre</b>", self.styles['Normal']),
                Paragraph(datos.nombre, self.styles['Normal']),
                Paragraph("<b>Documento</b>", self.styles['Normal']),
                Paragraph(datos.documento, self.styles['Normal']),
            ],
            [
                Paragraph("<b>Cargo</b>", self.styles['Normal']),
                Paragraph(datos.cargo, self.styles['Normal']),
                Paragraph("<b>Empresa</b>", self.styles['Normal']),
                Paragraph(datos.empresa, self.styles['Normal']),
            ],
            [
                Paragraph("<b>Fecha Ingreso</b>", self.styles['Normal']),
                Paragraph(CalculadoraPrestaciones.formato_fecha(datos.fecha_ingreso), self.styles['Normal']),
                Paragraph("<b>Fecha Retiro</b>", self.styles['Normal']),
                Paragraph(CalculadoraPrestaciones.formato_fecha(datos.fecha_retiro), self.styles['Normal']),
            ],
            [
                Paragraph("<b>Días Laborados</b>", self.styles['Normal']),
                Paragraph(str(resultados.dias_laborados), self.styles['Normal']),
                Paragraph("<b>Salario Mensual</b>", self.styles['Normal']),
                Paragraph(CalculadoraPrestaciones.formato_moneda(datos.salario_mensual), self.styles['Normal']),
            ],
        ]

        tabla_empleado = Table(datos_empleado, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch])
        tabla_empleado.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (3, 0), self.COLOR_ENCABEZADO),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLOR_ALTERNADO]),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(tabla_empleado)
        story.append(Spacer(1, 0.2 * inch))

        # ============ TABLA DE PRESTACIONES ============
        story.append(Paragraph("LIQUIDACIÓN DE PRESTACIONES", self.styles['Seccion']))

        tabla_datos = [
            [
                Paragraph("<b>CONCEPTO</b>", self.styles['Normal']),
                Paragraph("<b>VALOR</b>", self.styles['Normal']),
            ],
            [
                Paragraph("Cesantías", self.styles['Normal']),
                Paragraph(
                    CalculadoraPrestaciones.formato_moneda(resultados.cesantias),
                    ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT)
                ),
            ],
            [
                Paragraph("Intereses sobre Cesantías", self.styles['Normal']),
                Paragraph(
                    CalculadoraPrestaciones.formato_moneda(resultados.intereses_cesantias),
                    ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT)
                ),
            ],
            [
                Paragraph("Prima de Servicios", self.styles['Normal']),
                Paragraph(
                    CalculadoraPrestaciones.formato_moneda(resultados.prima_servicios),
                    ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT)
                ),
            ],
            [
                Paragraph("Vacaciones Proporcionales", self.styles['Normal']),
                Paragraph(
                    CalculadoraPrestaciones.formato_moneda(resultados.vacaciones),
                    ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT)
                ),
            ],
            [
                Paragraph("<b>TOTAL DEVENGADO</b>", self.styles['Normal']),
                Paragraph(
                    CalculadoraPrestaciones.formato_moneda(resultados.total_devengado),
                    ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold')
                ),
            ],
        ]

        # Agregar descuentos si los hay
        if resultados.descuentos > 0:
            tabla_datos.append([
                Paragraph("<i>Menos: Descuentos</i>", self.styles['Normal']),
                Paragraph(
                    CalculadoraPrestaciones.formato_moneda(resultados.descuentos),
                    ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT)
                ),
            ])

        tabla_datos.append([
            Paragraph("<b>NETO A PAGAR</b>", self.styles['Normal']),
            Paragraph(
                CalculadoraPrestaciones.formato_moneda(resultados.neto_pagar),
                ParagraphStyle('RightAlign', parent=self.styles['Normal'], alignment=TA_RIGHT, fontName='Helvetica-Bold')
            ),
        ])

        tabla_prestaciones = Table(tabla_datos, colWidths=[3.5 * inch, 1.75 * inch])
        tabla_prestaciones.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ENCABEZADO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, -2), (-1, -2), colors.HexColor('#E8E8E8')),
            ('BACKGROUND', (0, -1), (-1, -1), self.COLOR_TOTAL),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -2), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -3), [colors.white, self.COLOR_ALTERNADO]),
            ('FONTSIZE', (0, 1), (-1, -3), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(tabla_prestaciones)
        story.append(Spacer(1, 0.3 * inch))

        # ============ RESUMEN EN LETRAS ============
        total_letras = self._numero_a_letras(int(resultados.neto_pagar))
        story.append(Paragraph(
            f"<b>Son: </b>{total_letras}",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.3 * inch))

        # ============ FIRMAS ============
        story.append(Paragraph("AUTORIZACIÓN Y RECIBIDO", self.styles['Seccion']))
        story.append(Spacer(1, 0.15 * inch))

        firmas = [
            [
                Paragraph("_________________________", self.styles['Firma']),
                Paragraph("", self.styles['Normal']),
                Paragraph("_________________________", self.styles['Firma']),
            ],
            [
                Paragraph("Firma del Empleado", self.styles['Firma']),
                Paragraph("", self.styles['Normal']),
                Paragraph("Firma de la Empresa", self.styles['Firma']),
            ],
            [
                Paragraph("C.C. ___________________", self.styles['Firma']),
                Paragraph("", self.styles['Normal']),
                Paragraph("Autorizado por: ________", self.styles['Firma']),
            ],
            [
                Paragraph(f"Fecha: {CalculadoraPrestaciones.formato_fecha(fecha_generacion)}", self.styles['Firma']),
                Paragraph("", self.styles['Normal']),
                Paragraph(f"Fecha: {CalculadoraPrestaciones.formato_fecha(fecha_generacion)}", self.styles['Firma']),
            ],
        ]

        tabla_firmas = Table(firmas, colWidths=[1.8 * inch, 0.5 * inch, 1.8 * inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))

        story.append(tabla_firmas)
        story.append(Spacer(1, 0.2 * inch))

        # ============ PIE DE PÁGINA ============
        story.append(Spacer(1, 0.1 * inch))
        pie = Paragraph(
            "<i><font size=8 color=#999999>Documento generado automáticamente por el Sistema de Liquidación de Prestaciones. "
            "Este documento tiene validez como comprobante de pago de prestaciones sociales.</font></i>",
            self.styles['Normal']
        )
        story.append(pie)

        # Construir PDF
        doc.build(story)

        if not ruta_salida:
            buffer.seek(0)

        return buffer if not ruta_salida else ruta_salida

    @staticmethod
    def _numero_a_letras(numero: int) -> str:
        """Convierte número a letras en español"""
        if numero == 0:
            return "CERO PESOS COLOMBIANOS"

        unidades = ["", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
        decenas_esp = ["diez", "once", "doce", "trece", "catorce", "quince",
                       "dieciséis", "diecisiete", "dieciocho", "diecinueve"]
        decenas = ["", "", "veinte", "treinta", "cuarenta", "cincuenta",
                   "sesenta", "setenta", "ochenta", "noventa"]
        centenas = ["", "ciento", "doscientos", "trescientos", "cuatrocientos",
                    "quinientos", "seiscientos", "setecientos", "ochocientos", "novecientos"]

        def convertir_grupo(n):
            """Convierte un número de 0-999 a letras"""
            if n == 0:
                return ""

            resultado = ""
            c = n // 100
            d = (n % 100) // 10
            u = n % 10

            if c > 0:
                resultado += centenas[c] + " "

            if d == 1:
                resultado += decenas_esp[u] + " "
            else:
                if d > 1:
                    resultado += decenas[d]
                    if u > 0:
                        resultado += " y " + unidades[u]
                    resultado += " "
                elif u > 0:
                    resultado += unidades[u] + " "

            return resultado

        millones = numero // 1000000
        miles = (numero % 1000000) // 1000
        unidades_val = numero % 1000

        resultado = ""

        if millones > 0:
            mill_texto = convertir_grupo(millones).strip()
            if millones == 1:
                resultado += "un millón "
            else:
                resultado += mill_texto + "millones "

        if miles > 0:
            mil_texto = convertir_grupo(miles).strip()
            if miles == 1:
                resultado += "mil "
            else:
                resultado += mil_texto + "mil "

        if unidades_val > 0:
            resultado += convertir_grupo(unidades_val)

        return resultado.strip().upper() + " PESOS COLOMBIANOS"
