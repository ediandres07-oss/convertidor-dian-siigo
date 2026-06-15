# ⚡ INICIO RÁPIDO - Sistema de Liquidación de Prestaciones

> Activa la aplicación en 3 pasos

---

## 📦 Paso 1: Instalar

```bash
pip install streamlit reportlab pytz
```

O si prefieres usar el archivo de dependencias:

```bash
pip install -r requirements_prestaciones.txt
```

---

## 🚀 Paso 2: Ejecutar

```bash
streamlit run app_prestaciones.py
```

**Automáticamente se abrirá:**
- http://localhost:8501

Si no se abre automáticamente, abre ese link en tu navegador.

---

## ✨ Paso 3: Usar

### En la Interfaz Web:

1. **Completa el formulario:**
   - Nombre: Juan García Pérez
   - Documento: 1234567890
   - Cargo: Gerente
   - Salario: 2,600,000
   - Auxilio: 140,000
   - Fecha Ingreso: Elige una fecha
   - Fecha Retiro: Elige una fecha más reciente

2. **Haz clic en el botón grande:**
   - ✅ **LIQUIDAR PRESTACIONES**

3. **Descarga el PDF:**
   - ⬇️ **Descargar PDF Profesional**

**¡Listo!** Tienes tu liquidación completa en PDF

---

## 💻 Alternativa: Uso Sin Interfaz

Si prefieres no usar la web, ejecuta:

```bash
python3 ejemplo_uso_completo.py
```

Esto genera varios PDFs de ejemplo con diferentes escenarios.

---

## ✅ Verificar que todo funciona

Ejecuta este comando para verificar que los módulos carguen correctamente:

```bash
python3 -c "from calculadora_prestaciones import CalculadoraPrestaciones; print('✅ OK')"
```

Si ves `✅ OK`, está todo listo.

---

## 🎯 Qué hace el Sistema

| Acción | Resultado |
|--------|-----------|
| Ingresas datos | ✓ Sistema calcula automáticamente |
| Presionas botón | ✓ Valida todos los datos |
| Se genera PDF | ✓ Documento profesional y legalizado |
| Descargas | ✓ Puedes imprimir e firmar |

---

## 📊 Qué Calcula

Automáticamente calcula:

- ✅ Días laborados entre dos fechas
- ✅ **Cesantías** = (Salario + Auxilio) × Días / 360
- ✅ **Intereses** = Cesantías × 12% × Días / 360
- ✅ **Prima** = (Salario + Auxilio) × Días / 360
- ✅ **Vacaciones** = Salario × Días / 720
- ✅ **Total Devengado** (suma de todo)
- ✅ **Neto a Pagar** (con descuentos si existen)

---

## 🎨 El PDF Incluye

```
✓ Datos del empleado
✓ Tabla de prestaciones detallada
✓ Valores en formato moneda colombiana
✓ Total en letras (legal)
✓ Espacios para firmas
✓ Formato profesional tipo documento legal
```

---

## ⚙️ Si hay Problemas

### "No encuentro la aplicación"

```bash
# Ve a la carpeta del proyecto primero
cd "/Users/edison/Desktop/proyecto-subir info a siigo nube"

# Luego ejecuta
streamlit run app_prestaciones.py
```

### "ImportError: No module named streamlit"

```bash
pip install streamlit reportlab pytz
```

### "El PDF no se genera"

Verifica que los módulos se carguen:

```bash
python3 -c "from generador_pdf_prestaciones import GeneradorPDFPrestaciones; print('OK')"
```

---

## 📁 Archivos Principales

- **`app_prestaciones.py`** ← Ejecuta esto
- `calculadora_prestaciones.py` ← Lógica interna
- `generador_pdf_prestaciones.py` ← Generación de PDF
- `GUIA_LIQUIDADOR_PRESTACIONES.md` ← Documentación completa

---

## 🎓 Documentación

Para aprender más:

- 📖 **`README_PRESTACIONES.md`** - Resumen general
- 📘 **`GUIA_LIQUIDADOR_PRESTACIONES.md`** - Documentación completa
- 📝 **`ejemplo_uso_completo.py`** - 5 ejemplos prácticos

---

## 🎉 ¡Listo!

Ya puedes:

1. ✅ Ingresar datos de empleados
2. ✅ Calcular prestaciones automáticamente
3. ✅ Generar PDFs profesionales
4. ✅ Descargar y firmar documentos

---

## 📞 Soporte Rápido

| Problema | Solución |
|----------|----------|
| App no abre | `pip install streamlit` |
| PDF error | `pip install reportlab` |
| Comando no funciona | Verifica ruta correcta |
| Cálculos incorrectos | Revisa que fechas sean correctas |

---

**¡Que disfrutes el sistema!** 🚀

Para más detalles, lee: **`GUIA_LIQUIDADOR_PRESTACIONES.md`**
