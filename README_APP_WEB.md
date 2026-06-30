# 🌐 Aplicación Web: Declaración de Renta DIAN 2025

**Una aplicación web moderna y completa para automatizar tu declaración de renta.**

## ✨ Características

✅ **Interfaz gráfica moderna** - Diseño limpio y profesional  
✅ **Carga de Exógena** - Arrastra y suelta o selecciona archivo  
✅ **Procesamiento automático** - Mapea y llena Ayuda Renta al instante  
✅ **Descarga directa** - Obtén tu archivo diligenciado listo para presentar  
✅ **Sin instalación** - Solo abre en tu navegador  

## 🚀 Cómo usar

### Opción 1: Ejecutar desde script (RECOMENDADO)

```bash
cd /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/
./INICIAR_APP.sh
```

Luego abre en tu navegador: **http://127.0.0.1:5000/**

### Opción 2: Ejecutar manualmente

```bash
cd /Users/edison/Desktop/proyecto-subir\ info\ a\ siigo\ nube/
pip3 install flask openpyxl pandas
python3 app_declaracion_renta.py
```

## 📋 Pasos para usar la aplicación

1. **Descarga tu Exógena de la DIAN**
2. **Abre la aplicación web** en tu navegador
3. **Arrastra y suelta** tu Exógena en el área de carga
4. **Haz clic en "Procesar"**
5. **Descarga** tu Ayuda Renta completamente diligenciada

## 🎯 Qué hace la aplicación

✓ Lee tu reporte de Información Exógena  
✓ Extrae automáticamente los valores tributarios  
✓ Los mapea a las celdas correctas en Ayuda Renta  
✓ Genera un archivo XLSM listo para presentar  
✓ Preserva todas las macros del original  

## 📊 Valores que procesa

- ✓ Retenciones (R132)
- ✓ Patrimonio (CDTs, Bienes, Cuentas)
- ✓ Ingresos de Trabajo (Salarios, Pensiones)
- ✓ Rendimientos e Inversiones
- ✓ Y muchas más categorías...

## 🔧 Requisitos

- Python 3.7+
- Librerías: flask, openpyxl, pandas (se instalan automáticamente)
- Archivo: Ayuda Renta 2025 V1.0 .xlsm

## 💡 Tips

- **Mejor con Chrome o Safari** - Para mejor compatibilidad
- **Un archivo a la vez** - Procesa de uno en uno
- **Guarda el resultado** - Descarga y guarda el archivo en un lugar seguro
- **Verifica antes de presentar** - Revisa los valores antes de enviar a la DIAN

## ❓ Problemas comunes

**"Archivo Ayuda Renta base no encontrado"**
- Verifica que esté en: `/Users/edison/Downloads/Programa-Ayuda-Renta-DIAN-2025/`

**"Puerto 5000 en uso"**
- Cierra otras aplicaciones que usen ese puerto o cambia el puerto en el código

**"Valores no aparecen"**
- Asegúrate que tu Exógena sea el archivo descargado de la DIAN directamente

## 📞 Soporte

Para problemas o preguntas, revisa:
- `INSTRUCCIONES_EJECUCION.md` - Guía detallada
- `MAPEO_DETALLADO.md` - Explicación técnica
- `app_declaracion_renta.py` - Código comentado

---

**Versión 1.0** • Automatizador de Declaración de Renta DIAN 2025  
**¡Listo para usar! 🚀**
