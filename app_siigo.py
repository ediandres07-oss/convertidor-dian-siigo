"""
Convertidor de Archivo Plano SIIGO TXT a Excel
Convierte archivos planos de SIIGO a formato Excel para validación
"""

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

# ================================
# CONFIGURACIÓN
# ================================
COLUMNAS = [
    "tipo",
    "cuenta",
    "documento",
    "nombre",
    "valor",
    "naturaleza"
]

CUENTAS_DESCRIPCIONES = {
    "5105": "Salarios",
    "510530": "Cesantías",
    "510533": "Intereses Cesantías",
    "510536": "Prima de Servicios",
    "510539": "Vacaciones",
    "237005": "Salud",
    "238030": "Pensión",
    "238095": "Fondo Solidaridad",
    "236540": "Retención en la Fuente",
    "111005": "Bancos"
}

# ================================
# PROCESAMIENTO
# ================================
def convertir_txt_a_excel(ruta_txt, ruta_salida=None):
    """
    Convierte archivo plano TXT de SIIGO a Excel

    Args:
        ruta_txt: Ruta del archivo TXT
        ruta_salida: Ruta de salida (si no se especifica, usa el mismo nombre)

    Returns:
        Ruta del archivo generado
    """

    if ruta_salida is None:
        ruta_salida = ruta_txt.replace(".txt", ".xlsx")

    # Leer archivo
    df = pd.read_csv(
        ruta_txt,
        sep=";",
        header=None,
        names=COLUMNAS,
        dtype={"cuenta": str, "documento": str}
    )

    # Convertir valores a número
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

    # Agregar descripción de cuenta
    df["descripcion_cuenta"] = df["cuenta"].map(CUENTAS_DESCRIPCIONES).fillna("Otros")

    # =========================
    # VALIDACIÓN CONTABLE
    # =========================
    debitos = df[df["naturaleza"] == "D"]["valor"].sum()
    creditos = df[df["naturaleza"] == "C"]["valor"].sum()
    diferencia = abs(debitos - creditos)
    balanceado = diferencia < 0.01

    validacion = pd.DataFrame([{
        "Total Débitos": round(debitos, 2),
        "Total Créditos": round(creditos, 2),
        "Diferencia": round(diferencia, 2),
        "Estado": "✅ BALANCEADO" if balanceado else "❌ DESBALANCEADO"
    }])

    # =========================
    # RESUMEN POR CUENTA
    # =========================
    resumen_cuenta = df.groupby(["cuenta", "descripcion_cuenta", "naturaleza"])["valor"].sum().reset_index()
    resumen_cuenta.columns = ["Cuenta", "Descripción", "Naturaleza", "Valor"]
    resumen_cuenta = resumen_cuenta.sort_values("Valor", ascending=False)

    # =========================
    # RESUMEN POR EMPLEADO
    # =========================
    resumen_empleado = df.groupby(["documento", "nombre"])["valor"].sum().reset_index()
    resumen_empleado.columns = ["Documento", "Nombre", "Total"]
    resumen_empleado = resumen_empleado.sort_values("Total", ascending=False)

    # =========================
    # RESUMEN POR NATURALEZA
    # =========================
    resumen_naturaleza = df.groupby("naturaleza")["valor"].sum().reset_index()
    resumen_naturaleza.columns = ["Naturaleza", "Valor"]
    resumen_naturaleza["Naturaleza"] = resumen_naturaleza["Naturaleza"].map({
        "D": "Débitos",
        "C": "Créditos"
    })

    # =========================
    # EXPORTACIÓN
    # =========================
    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        # Hoja 1: Plano completo
        df_export = df[["tipo", "cuenta", "descripcion_cuenta", "documento", "nombre", "valor", "naturaleza"]]
        df_export.columns = ["Tipo", "Cuenta", "Descripción", "Documento", "Nombre", "Valor", "Naturaleza"]
        df_export.to_excel(writer, sheet_name="Plano", index=False)

        # Hoja 2: Validación
        validacion.to_excel(writer, sheet_name="Validacion", index=False)

        # Hoja 3: Resumen por Cuenta
        resumen_cuenta.to_excel(writer, sheet_name="Por Cuenta", index=False)

        # Hoja 4: Resumen por Empleado
        resumen_empleado.to_excel(writer, sheet_name="Por Empleado", index=False)

        # Hoja 5: Resumen por Naturaleza
        resumen_naturaleza.to_excel(writer, sheet_name="Por Naturaleza", index=False)

    return ruta_salida, balanceado, debitos, creditos


# ================================
# INTERFAZ GRÁFICA
# ================================
class ConvertidorSIIGO:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Convertidor Plano SIIGO TXT a Excel")
        self.ventana.geometry("500x400")
        self.ventana.resizable(False, False)

        # Color principal
        self.color_principal = "#1f4788"
        self.color_boton = "#007BFF"

        # ======================
        # FRAME PRINCIPAL
        # ======================
        frame_principal = tk.Frame(ventana, bg="white")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = tk.Label(
            frame_principal,
            text="🧮 Convertidor SIIGO",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.color_principal
        )
        titulo.pack(pady=10)

        # Subtítulo
        subtitulo = tk.Label(
            frame_principal,
            text="Convierte archivo plano TXT de SIIGO a Excel",
            font=("Arial", 10),
            bg="white",
            fg="#666"
        )
        subtitulo.pack(pady=5)

        # Separador
        tk.Frame(frame_principal, bg="#ddd", height=2).pack(fill=tk.X, pady=10)

        # Instrucciones
        instrucciones = tk.Label(
            frame_principal,
            text="""Pasos:
1. Selecciona un archivo TXT (plano SIIGO)
2. Se convertirá automáticamente a Excel
3. Se validará el balance contable
4. Se generarán múltiples hojas de resumen""",
            font=("Arial", 9),
            bg="white",
            fg="#333",
            justify=tk.LEFT
        )
        instrucciones.pack(pady=10, anchor=tk.W)

        # Separador
        tk.Frame(frame_principal, bg="#ddd", height=2).pack(fill=tk.X, pady=10)

        # Botón principal
        self.boton_convertir = tk.Button(
            frame_principal,
            text="📂 Seleccionar archivo TXT",
            command=self.seleccionar_archivo,
            bg=self.color_boton,
            fg="white",
            font=("Arial", 11, "bold"),
            width=30,
            height=2,
            cursor="hand2"
        )
        self.boton_convertir.pack(pady=15)

        # Label de estado
        self.label_estado = tk.Label(
            frame_principal,
            text="Esperando seleccionar archivo...",
            font=("Arial", 9),
            bg="white",
            fg="#999"
        )
        self.label_estado.pack(pady=10)

        # Separador
        tk.Frame(frame_principal, bg="#ddd", height=1).pack(fill=tk.X, pady=10)

        # Info
        info = tk.Label(
            frame_principal,
            text="Versión 1.0 | Compatible con SIIGO",
            font=("Arial", 8),
            bg="white",
            fg="#ccc"
        )
        info.pack(pady=5)

    def seleccionar_archivo(self):
        """Abre diálogo para seleccionar archivo TXT"""

        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo TXT de SIIGO",
            filetypes=[("Archivos TXT", "*.txt"), ("Todos", "*.*")]
        )

        if archivo:
            self.procesar_archivo(archivo)

    def procesar_archivo(self, ruta_txt):
        """Procesa y convierte el archivo TXT"""

        try:
            self.label_estado.config(text="⏳ Procesando...", fg="#FFA500")
            self.ventana.update()

            # Convertir
            ruta_salida, balanceado, debitos, creditos = convertir_txt_a_excel(ruta_txt)

            # Actualizar estado
            self.label_estado.config(
                text=f"✅ Conversión exitosa",
                fg="#28A745"
            )

            # Mensaje de éxito
            mensaje = f"""✅ CONVERSIÓN EXITOSA

Archivo generado:
{ruta_salida}

Balance Contable:
  Débitos:   ${debitos:,.2f}
  Créditos:  ${creditos:,.2f}
  Estado:    {'✅ BALANCEADO' if balanceado else '❌ DESBALANCEADO'}

Hojas generadas:
  1. Plano - Todos los asientos
  2. Validacion - Balance contable
  3. Por Cuenta - Agrupado por cuenta
  4. Por Empleado - Agrupado por empleado
  5. Por Naturaleza - Débitos y Créditos"""

            messagebox.showinfo("Éxito", mensaje)

            # Preguntar si abrir el archivo
            if messagebox.askyesno("Abrir archivo", "¿Deseas abrir el archivo Excel?"):
                if hasattr(os, 'startfile'):  # Windows
                    os.startfile(ruta_salida)
                elif hasattr(os, 'system'):  # Mac/Linux
                    os.system(f'open "{ruta_salida}"')

        except Exception as e:
            self.label_estado.config(text="❌ Error en conversión", fg="#DC3545")
            messagebox.showerror(
                "Error",
                f"No se pudo convertir el archivo:\n\n{str(e)}"
            )


# ================================
# EJECUTAR
# ================================
def crear_app():
    """Crea y ejecuta la aplicación"""
    ventana = tk.Tk()
    app = ConvertidorSIIGO(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    crear_app()
