# 📦 Generar Ejecutable - Convertidor SIIGO

Instrucciones para crear un ejecutable (.exe) de la aplicación Convertidor SIIGO.

## 🖥️ **Windows**

### **Paso 1: Instalar PyInstaller**

```bash
pip install pyinstaller pillow
```

### **Paso 2: Compilar la Aplicación**

```bash
pyinstaller --onefile --windowed --icon=icono.ico app_siigo.py
```

O usa el script:

```bash
python3 build_windows.py
```

### **Paso 3: Ejecutable Generado**

```
dist/
└── app_siigo.exe (archivo ejecutable)
```

### **Paso 4: Usar la Aplicación**

- Doble clic en `app_siigo.exe`
- Se abre la interfaz gráfica
- Selecciona tu archivo TXT
- Se convierte automáticamente a Excel

---

## 🍎 **macOS**

### **Paso 1: Instalar PyInstaller**

```bash
pip install pyinstaller pillow
```

### **Paso 2: Compilar la Aplicación**

```bash
pyinstaller --onedir --windowed --icon=icono.ico app_siigo.py
```

### **Paso 3: Aplicación Generada**

```
dist/
└── app_siigo.app (aplicación macOS)
```

### **Paso 4: Usar la Aplicación**

- Abre `Finder`
- Navega a la carpeta `dist`
- Haz doble clic en `app_siigo.app`
- La aplicación se abre

---

## 🐧 **Linux**

### **Paso 1: Instalar PyInstaller**

```bash
pip install pyinstaller pillow
```

### **Paso 2: Compilar la Aplicación**

```bash
pyinstaller --onefile --windowed app_siigo.py
```

### **Paso 3: Ejecutable Generado**

```
dist/
└── app_siigo (ejecutable Linux)
```

### **Paso 4: Usar la Aplicación**

```bash
# Dar permisos de ejecución
chmod +x dist/app_siigo

# Ejecutar
./dist/app_siigo
```

---

## 📋 **Requisitos Previos**

- **Python 3.7+** instalado
- **pip** instalado
- Dependencias:
  ```bash
  pip install pandas openpyxl tkinter pillow pyinstaller
  ```

---

## 🎯 **Opciones de Compilación**

| Opción | Descripción |
|--------|-------------|
| `--onefile` | Genera un único archivo ejecutable |
| `--windowed` | No muestra consola (solo interfaz gráfica) |
| `--icon=archivo.ico` | Usa icono personalizado |
| `--name=nombre` | Nombre de la aplicación |
| `--onedir` | Genera carpeta con archivos (más rápido) |

---

## 📦 **Archivo Generado**

El archivo se crea en:
```
dist/
├── app_siigo.exe (Windows)
├── app_siigo.app (macOS)
└── app_siigo (Linux)
```

### **Tamaño Típico**

- **Windows**: ~100-150 MB
- **macOS**: ~150-200 MB
- **Linux**: ~100-150 MB

---

## 🚀 **Distribución**

### **Para Windows**

1. Copia `dist/app_siigo.exe`
2. Distribuye el archivo
3. El usuario lo abre directamente
4. No necesita Python instalado

### **Para macOS**

1. Copia la carpeta `dist/app_siigo.app`
2. Distribuye como ZIP
3. El usuario descomprime y abre
4. No necesita Python instalado

### **Para Linux**

1. Copia `dist/app_siigo`
2. Haz ejecutable: `chmod +x app_siigo`
3. El usuario ejecuta: `./app_siigo`

---

## 🔧 **Solución de Problemas**

### **"Module not found: pandas"**

```bash
pip install pandas openpyxl
pyinstaller --hidden-import=pandas app_siigo.py
```

### **"Module not found: tkinter"**

En Ubuntu/Debian:
```bash
sudo apt-get install python3-tk
```

En Fedora:
```bash
sudo dnf install python3-tkinter
```

### **Antivirus detecta amenaza**

Es falso positivo común. Excluye el archivo o importa desde fuente confiable.

---

## 📚 **Comandos Rápidos**

### **Windows - Crear .exe**

```bash
pip install pyinstaller pandas openpyxl
pyinstaller --onefile --windowed --icon=icono.ico app_siigo.py
# Resultado: dist/app_siigo.exe
```

### **macOS - Crear .app**

```bash
pip install pyinstaller pandas openpyxl
pyinstaller --onedir --windowed --icon=icono.ico app_siigo.py
# Resultado: dist/app_siigo.app
```

### **Linux - Crear ejecutable**

```bash
pip install pyinstaller pandas openpyxl
pyinstaller --onefile --windowed app_siigo.py
chmod +x dist/app_siigo
# Resultado: dist/app_siigo
```

---

## ✅ **Verificación**

Después de compilar:

1. Verifica que el ejecutable existe
2. Haz doble clic/ejecuta
3. Debería abrirse la interfaz gráfica
4. Prueba cargar un archivo TXT
5. Verifica que genera el Excel correctamente

---

**¡Tu aplicación está lista para distribuir!** 🚀
