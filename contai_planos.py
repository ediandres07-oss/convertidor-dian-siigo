"""
Generador de Planos para Contai-Ilimitada
Convierte archivos de Balance y Ventas a formato compatible
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pathlib import Path
import pandas as pd
from datetime import datetime
import io


class ContaiPlanoGenerator:
    """Genera planos en formato Contai-Ilimitada desde Excel"""

    THIN_BORDER = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    HEADER_FILL = PatternFill(start_color="1a3a5c", end_color="1a3a5c", fill_type="solid")
    HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)

    def __init__(self, balance_path=None, ventas_path=None):
        self.balance_path = balance_path
        self.ventas_path = ventas_path
        self.balance_data = None
        self.ventas_data = None

    def cargar_balance(self):
        """Carga balance de prueba desde Excel"""
        if not self.balance_path:
            return False

        try:
            df = pd.read_excel(self.balance_path, sheet_name='Datos', skiprows=3)
            self.balance_data = df
            return True
        except Exception as e:
            print(f"Error cargando balance: {e}")
            return False

    def cargar_ventas(self):
        """Carga plano de ventas desde Excel"""
        if not self.ventas_path:
            return False

        try:
            df = pd.read_excel(self.ventas_path, sheet_name=0)
            self.ventas_data = df
            return True
        except Exception as e:
            print(f"Error cargando ventas: {e}")
            return False

    def generar_plano_contai(self):
        """Genera archivo plano en formato Contai-Ilimitada"""
        if self.ventas_data is None:
            return None

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Plano Contai"

        # Headers
        headers = [
            'Cuenta', 'Comprobante', 'Fecha', 'Documento Ref',
            'NIT', 'Detalle', 'Tipo', 'VALORES', 'BASE',
            'Centro de Costo', 'Transacciones Externas', 'Plazo'
        ]

        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(1, col_idx)
            cell.value = header
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = self.THIN_BORDER

        # Datos
        row_idx = 2
        for _, row in self.ventas_data.iterrows():
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row_idx, col_idx)

                if header == 'Cuenta':
                    cell.value = row.get('Cuenta', '')
                elif header == 'Comprobante':
                    cell.value = row.get('Comprobante', '')
                elif header == 'Fecha':
                    cell.value = row.get('Fecha(mm/dd/yyyy)', '')
                elif header == 'Documento Ref':
                    cell.value = row.get('Documento Ref.', '')
                elif header == 'NIT':
                    cell.value = row.get('Nit', '')
                elif header == 'Detalle':
                    cell.value = row.get('Detalle', '')
                elif header == 'Tipo':
                    cell.value = row.get('Tipo', '')
                elif header == 'VALORES':
                    cell.value = row.get('VALORES', '')
                    cell.number_format = '#,##0.00'
                elif header == 'BASE':
                    cell.value = row.get('BASE', '')
                    cell.number_format = '#,##0.00'
                elif header == 'Centro de Costo':
                    cell.value = row.get('Centro de Costo', '')
                elif header == 'Transacciones Externas':
                    cell.value = row.get('Trans. Ext', '')
                elif header == 'Plazo':
                    cell.value = row.get('Plazo', '')

                cell.border = self.THIN_BORDER
                cell.alignment = Alignment(horizontal="left", vertical="center")

            row_idx += 1

        # Auto-ajustar columnas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = min(adjusted_width, 50)

        # Guardar a bytes
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    def generar_reporte_balance(self):
        """Genera reporte formateado del balance de prueba"""
        if self.balance_data is None:
            return None

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Balance Formateado"

        # Encabezado
        ws['A1'] = "BALANCE DE PRUEBA"
        ws['A1'].font = Font(bold=True, size=14, color="FFFFFF")
        ws['A1'].fill = self.HEADER_FILL
        ws.merge_cells('A1:I1')
        ws['A1'].alignment = Alignment(horizontal="center", vertical="center")

        # Fecha
        ws['A2'] = f"Generado: {datetime.now().strftime('%d-%m-%Y')}"
        ws.merge_cells('A2:I2')

        # Copiar datos con formato
        headers = self.balance_data.columns.tolist()

        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(4, col_idx)
            cell.value = header
            cell.font = self.HEADER_FONT
            cell.fill = self.HEADER_FILL
            cell.border = self.THIN_BORDER
            cell.alignment = Alignment(horizontal="center", vertical="center")

        for row_idx, row in enumerate(self.balance_data.itertuples(index=False), 5):
            for col_idx, value in enumerate(row, 1):
                cell = ws.cell(row_idx, col_idx)
                cell.value = value
                cell.border = self.THIN_BORDER

                # Formatear números
                if col_idx > 2:  # Columnas numéricas
                    try:
                        if isinstance(value, (int, float)):
                            cell.number_format = '#,##0.00'
                    except:
                        pass

        # Auto-ajustar
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            ws.column_dimensions[column].width = min(max_length + 2, 50)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output


def validar_archivos_contai(balance_path, ventas_path):
    """Valida que los archivos sean válidos para Contai"""
    errores = []

    try:
        balance_df = pd.read_excel(balance_path, sheet_name='Datos', skiprows=3)
        if balance_df.empty:
            errores.append("Balance vacío")
    except Exception as e:
        errores.append(f"Balance inválido: {str(e)}")

    try:
        ventas_df = pd.read_excel(ventas_path, sheet_name=0)
        if ventas_df.empty:
            errores.append("Plano de ventas vacío")

        required_cols = ['Cuenta', 'Nit', 'VALORES']
        missing = [col for col in required_cols if col not in ventas_df.columns]
        if missing:
            errores.append(f"Columnas faltantes en ventas: {', '.join(missing)}")
    except Exception as e:
        errores.append(f"Ventas inválido: {str(e)}")

    return len(errores) == 0, errores
