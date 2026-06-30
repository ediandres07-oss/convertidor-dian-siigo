# Instrucciones de Ejecución - Automatizador Exógena → Ayuda Renta

## 📋 PASO 1: REQUISITOS PREVIOS

### 1.1 Verificar que Python 3.7+ esté instalado
```bash
python3 --version
```
Deberías ver algo como: `Python 3.9.x` o superior

### 1.2 Ubicación de archivos requeridos
- ✓ **Exógena**: `/Users/edison/Library/Containers/net.whatsapp.WhatsApp/Data/tmp/documents/0141329A-8688-45CB-9787-E5FD5051A852/reporteExogena2024Elizabeth.xlsx`
- ✓ **Ayuda Renta**: `/Users/edison/Downloads/Programa-Ayuda-Renta-DIAN-2025/AyudaRenta 2025 V1.0 .xlsm`
- ✓ **Script**: `/Users/edison/Desktop/proyecto-subir info a siigo nube/exogena_to_ayuda_renta.py`

---

## 🔧 PASO 2: INSTALAR DEPENDENCIAS

### 2.1 Abrir Terminal

### 2.2 Ejecutar comando de instalación
```bash
pip3 install pandas openpyxl
```

**Esperado**: Algo como:
```
Successfully installed pandas-1.5.3 openpyxl-3.10.0
```

Si ya tienes `pandas` u `openpyxl`, simplemente se omitirán.

---

## ⚙️ PASO 3: PERSONALIZAR CONFIGURACIÓN (OPCIONAL)

Si necesitas cambiar rutas o celdas de destino:

### 3.1 Abrir el script con un editor (VSCode, Sublime, etc.)
```bash
code /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/exogena_to_ayuda_renta.py
```

### 3.2 Buscar la sección `CONFIG` (línea ~20)

### 3.3 Ajustar si es necesario:

**Si cambió la ruta del Exógena:**
```python
"exogena_file": "/tu/nueva/ruta/reporteExogena2024Elizabeth.xlsx",
```

**Si cambió la ruta del Ayuda Renta:**
```python
"ayuda_renta_file": "/tu/nueva/ruta/AyudaRenta 2025 V1.0 .xlsm",
```

**Si necesitas cambiar celdas de destino** (ej. para Retenciones):
```python
"R132 Retenciones año gravable a declarar": {
    "hoja": "Retenciones",
    "celda": "C32",  # ← Cambiar aquí si necesario
    "type": "sum",
    "descripcion": "Retenciones practicadas CDT y retiros pensión"
},
```

---

## ▶️ PASO 4: EJECUTAR EL SCRIPT

### 4.1 Abrir Terminal en el directorio del proyecto
```bash
cd /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/
```

### 4.2 Ejecutar el script
```bash
python3 exogena_to_ayuda_renta.py
```

### 4.3 Monitorear el proceso

Deberías ver en Terminal algo como:

```
2025-06-22 14:30:45,123 - INFO - ================================================================================
2025-06-22 14:30:45,124 - INFO - AUTOMATIZADOR: Exógena DIAN → Ayuda Renta 2025
2025-06-22 14:30:45,125 - INFO - ================================================================================
2025-06-22 14:30:45,200 - INFO - Leyendo archivo Exógena...
2025-06-22 14:30:47,150 - INFO - ✓ Se leyeron 59 registros del Exógena
2025-06-22 14:30:47,200 - INFO - Procesando datos del Exógena...
2025-06-22 14:30:47,250 - INFO - ✓ 14 categorías procesadas
2025-06-22 14:30:47,300 - INFO - Abriendo archivo Ayuda Renta...
2025-06-22 14:30:47,400 - INFO - ✓ Archivo cargado (macros preservadas)
2025-06-22 14:30:47,500 - INFO -   ✓ Retenciones!C32 = $1,362,514
2025-06-22 14:30:47,600 - INFO -   ✓ Patrimonio!D14 = $335,626,272
...
2025-06-22 14:30:47,700 - INFO - ✓ 8 inyecciones realizadas
2025-06-22 14:30:47,800 - INFO - Guardando archivo: /Users/edison/Desktop/proyecto-subir info a siigo nube/AyudaRenta_Diligenciado.xlsm
2025-06-22 14:30:48,500 - INFO - ✓ Archivo guardado exitosamente (2.45 MB)
2025-06-22 14:30:48,600 - INFO - ================================================================================
2025-06-22 14:30:48,601 - INFO - ✓ PROCESO COMPLETADO EXITOSAMENTE
2025-06-22 14:30:48,602 - INFO -   Archivo generado: /Users/edison/Desktop/proyecto-subir info a siigo nube/AyudaRenta_Diligenciado.xlsm
2025-06-22 14:30:48,603 - INFO - ================================================================================
```

✓ **Si ves este mensaje, ¡el proceso fue exitoso!**

---

## 📁 PASO 5: VERIFICAR RESULTADO

### 5.1 Buscar el archivo generado

El archivo se guardó en:
```
/Users/edison/Desktop/proyecto-subir info a siigo nube/AyudaRenta_Diligenciado.xlsm
```

### 5.2 Abrir el archivo en Excel
```bash
open /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/AyudaRenta_Diligenciado.xlsm
```

### 5.3 Verificaciones
- ✓ Las macros deberían estar intactas (sin advertencia de "contenido deshabilitado")
- ✓ Los valores inyectados aparecen en las hojas especificadas
- ✓ Los cálculos automáticos (SUM, ROUND, etc.) funcionan normalmente

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "ModuleNotFoundError: No module named 'pandas'"

**Solución:**
```bash
pip3 install pandas openpyxl
```

### Problema: "FileNotFoundError: Archivo Exógena no encontrado"

**Solución:**
1. Verifica que la ruta en `CONFIG["exogena_file"]` sea correcta
2. Verifica que el archivo exista en esa ruta
3. Si cambió la ruta, actualízala en el script

### Problema: "Data Validation extension is not supported and will be removed"

**No es un error**, es solo una advertencia de openpyxl. El archivo se guardará correctamente, pero algunas validaciones de datos se perderán. Esto es normal.

### Problema: Las macros desaparecieron

**Prevención futura:**
- El script usa `keep_vba=True` para preservarlas
- Si aún así desaparecen, es posible que Excel las haya removido al abrir el archivo

---

## 🔄 PRÓXIMAS EJECUCIONES

Cada vez que tengas un nuevo Exógena:

```bash
cd /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/
python3 exogena_to_ayuda_renta.py
```

Esto creará un nuevo archivo `AyudaRenta_Diligenciado.xlsm` (sobrescribiendo el anterior).

---

## 📚 REFERENCIA RÁPIDA DEL MAPEO

| Categoría Exógena | Destino | Hoja | Celda | Tipo |
|---|---|---|---|---|
| R132 Retenciones | Retenciones practicadas | Retenciones | C32 | SUM |
| Patrimonio Bruto (CDT) | Inversiones | Patrimonio | D14 | Direct |
| Patrimonio Bruto (Catastral) | Bienes raíces | Patrimonio | D18 | Direct |
| Cuentas Bancarias | Saldos bancarios | Efectivo_Bancos_Cuentas | E7+ | List |
| CDT Inversiones | Consignaciones | Inversiones | E7+ | List |
| Ingresos Laborales | Salarios | Salarios_Demas_Pagos_Laborales | E7+ | List |
| Rendimientos CDT | Intereses | Inter_Rend_Finan | E7+ | List |

---

## 📞 AYUDA ADICIONAL

Si necesitas:
- **Cambiar el mapeo**: Edita la sección `CONFIG["data_mapping"]` en el script
- **Ajustar celdas**: Ubica la hoja exacta en Ayuda Renta y anota la celda destino
- **Ver logs detallados**: Cambia `level=logging.INFO` a `level=logging.DEBUG`

---

**¡Listo! Ahora puedes ejecutar el script con confianza.** ✓
