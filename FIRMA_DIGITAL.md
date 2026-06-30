# Firma Digital de Liquidaciones

## Opción 1: Certificado Digital Real (Legal)

### Dónde obtener en Colombia:

1. **Entidades Certificadoras Autorizadas:**
   - AC Asesor: https://www.acasesor.com.co
   - Entidad Certificadora de Tecnología (ACT): https://www.act.com.co
   - Camara de Comercio de Bogotá: https://www.ccb.org.co
   - BANCOLOMBIA (para clientes): https://www.bancolombia.com

2. **Tipos disponibles:**
   - **Certificado Personal**: $150-300k/año
   - **Certificado Jurídico**: $500-800k/año (personas jurídicas)
   - **Certificado de Servidor**: $1000-2000k/año

3. **Pasos:**
   - Ir a la AC elegida
   - Completar solicitud con datos de identidad
   - Pagar arancel
   - Retirar certificado en formato .p12 o .pfx
   - Guardar con su contraseña

### Usar en la App:

```python
from firma_digital import FirmaDigitalPDF

# Configurar
firma = FirmaDigitalPDF(
    cert_path='/ruta/certificado.p12',
    cert_password='tu_contraseña'
)

# Firmar PDF
pdf_firmado = firma.firmar_pdf(pdf_bytes, signer_name="Tu Nombre")
```

---

## Opción 2: Certificado de Prueba (Testing)

```python
from firma_digital import generar_certificado_prueba

# Generar certificado autofirmado para testing
generar_certificado_prueba('/tmp/test_cert.p12', password='123456')
```

⚠️ **NO VÁLIDO LEGALMENTE** - Solo para pruebas

---

## Certificados Populares en Colombia:

| Proveedor | Costo Anual | Link |
|-----------|-----------|------|
| AC Asesor | $200k | https://www.acasesor.com.co |
| ACT | $250k | https://www.act.com.co |
| BanColombia | Gratis (clientes) | https://www.bancolombia.com |
| CCB | $300k | https://www.ccb.org.co |

---

## Integración en la App

El módulo `firma_digital.py` está listo para:

1. ✅ Cargar certificados (.p12, .pfx, .pem)
2. ✅ Firmar PDFs digitalmente
3. ✅ Validar cadena de firma
4. ✅ Generar certificados de prueba

Para activar, contacta a soporte con tu certificado.

---

## Verificar Firma Digital

Después de firmar, verifica en Adobe Reader o Google Chrome:
- Abre el PDF
- Menú: Verificar → Firmas Digitales
- Debe mostrar "Firmado por: [Tu Nombre]"

---

## Seguridad

- 🔒 Los certificados se guardan **SOLO en el servidor**
- 🔐 La contraseña se solicita al usuario (no se almacena)
- ✅ Las firmas son **válidas legalmente** en Colombia

Contacta con soporte para configurar tu certificado.
