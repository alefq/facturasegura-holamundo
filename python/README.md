# Factura Segura ESI - Hola Mundo (Python)

**Proyecto de ejemplo abierto** para promover el uso del **ESI (External System Integration)** de [Factura Segura](https://facturasegura.com.py), la plataforma oficial de facturación electrónica de Paraguay (SIFEN - DNIT).

Este repositorio contiene ejemplos prácticos y bien documentados en Python para integrarte con la API de Factura Segura de forma segura y siguiendo las mejores prácticas que descubrimos durante pruebas reales.

## 🎯 Objetivo

- Facilitar el onboarding de desarrolladores e integradores al ecosistema ESI de Factura Segura.
- Proporcionar código listo para copiar, adaptar y usar en producción.
- Compartir lecciones aprendidas de la documentación oficial + pruebas reales en ambiente de test.
- Servir como base para proyectos más complejos (facturación masiva, integración con ERPs, etc.).

**Licencia:** Apache License 2.0

## 🚀 Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-org/facturasegura-holamundo.git
cd facturasegura-holamundo/python
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar credenciales (¡nunca commitees datos reales!)

Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Edita `.env` con tus datos de **pruebas** (nunca uses credenciales de producción aquí):

```env
BASE_URL=https://apitest.facturasegura.com.py

ESI_EMAIL=tu-usuario-esi@ejemplo.com
ESI_PASSWORD=tu-password-de-pruebas
```

> **Nota de seguridad**: Aunque puedes pasar `--email` y `--password` por línea de comandos, esto los expone en el historial del shell (`history`). Es **recomendable** usar variables de entorno (el script carga `.env` automáticamente gracias a `python-dotenv`).

### 4. Ejecutar el flujo completo de prueba

```bash
python examples/test_esi.py --email "$ESI_EMAIL" --password "$ESI_PASSWORD"
```

Este script hace:
1. Login y obtención de `Authentication-Token`
2. **Canary pre-flight** (consulta de estado de un CDC conocido) → actúa como "health check" antes de generar nada.
3. `calcular_de` (envía datos resumidos y recibe el DE completo con todos los totales calculados).
4. `generar_de` (envía el DE completo, genera XML, firma y envía a SIFEN).
5. **Canary post** (consulta el estado del CDC recién generado).
6. Soporte de **reingreso** (mismo número de documento) o nuevo número vía flags.

### 5. Opciones útiles del script

```bash
# Solo consultar el estado de un CDC (sin generar nada)
python examples/test_esi.py --email "$ESI_EMAIL" --password "$ESI_PASSWORD" \
  --get-estado 01009643435001001100000222026060612022117504 --dRucEm 964343

# Especificar número de documento exacto (evita colisiones en producción)
python examples/test_esi.py --email "$ESI_EMAIL" --password "$ESI_PASSWORD" \
  --num-doc 1000005

# Generar con reintento (siguiente número de documento)
python examples/test_esi.py --email "$ESI_EMAIL" --password "$ESI_PASSWORD" --retry

# Reingreso con el MISMO número de documento (protocolo SIFEN)
python examples/test_esi.py --email "$ESI_EMAIL" --password "$ESI_PASSWORD" --retry --reingreso
```

**Mejoras implementadas** (basadas en feedback):
- `BASE_URL` se puede configurar vía variable de entorno (o `.env`) y se centralizó en ambos scripts.
- Soporte nativo de `.env` con `python-dotenv` (los scripts cargan automáticamente BASE_URL, ESI_EMAIL y ESI_PASSWORD).
- Mejor manejo de errores de red (timeouts, connection errors, HTTP errors con mensajes claros).
- `--num-doc` para controlar el número de documento desde línea de comandos (evita hardcode y colisiones).
- `BASE_URL` centralizado (fácil cambiar entre test y producción).

### 6. Polling de estado (útil para monitorear)

```bash
python examples/poll_cdc_status.py \
  --email "$ESI_EMAIL" --password "$ESI_PASSWORD" \
  --cdc 01009643435001001100000222026060612022117504 \
  --ruc 964343 \
  --interval 10 \
  --max-seconds 120
```

El script de polling también respeta `BASE_URL` desde el entorno.

## 📚 Lecciones Aprendidas de la Documentación y Pruebas Reales

### 1. Autenticación (lo más importante al principio)
- Se hace un login normal contra `/login?include_auth_token`.
- El token importante es `authentication_token` (no el csrf_token).
- Se envía en el header `Authentication-Token` (no Authorization Bearer).
- El token puede dejar de funcionar después de un tiempo o si cambias la contraseña. Siempre refresca antes de flujos importantes.

### 2. Operaciones principales del ESI
- **`calcular_de`**: Envías un DE "resumido" (solo datos de entrada). El sistema te devuelve el DE completo con todos los totales, bases gravadas, IVA, etc. calculados según reglas de SIFEN. **Muy recomendado** antes de generar.
- **`generar_de`**: Envías el DE completo. El sistema genera el XML, lo firma, genera el KuDE y lo envía a SIFEN.
- **`get_estado_sifen`**: Consulta el estado actual en SIFEN (Aprobado, Rechazado, SOL.APROBACION, ENVIADO_A_SIFEN, etc.). Muy útil como **canary test**.

### 3. El "Canary Test" (nuestra mejor práctica)
Antes de generar cualquier documento real:
- Siempre consulta primero el estado de un CDC conocido (aunque esté rechazado).
- Si el `code` del response no es 0 → algo está mal con el token, permisos o conectividad → **NO continues** con la generación.

Esto evita generar documentos "a ciegas" cuando hay problemas de autenticación o autorización del ESI.

### 4. Datos del Emisor - Deben coincidir exactamente
Uno de los errores más comunes (y frustrantes) es:

> "1262 - TEST - Descripción de la actividad económica no corresponde al código"

**Regla de oro:**  
Las descripciones en `gActEco` (`dDesActEco`) **deben ser exactamente** las que tienes registradas en el portal de Factura Segura para ese RUC. No uses descripciones libres como "Desarrollo de software". Usa las oficiales:
- "Actividades de programación informática"
- "Actividades de consultoría y gestión de servicios informáticos"
- etc.

Lo mismo aplica para:
- `dFeIniT` (fecha de inicio del timbrado)
- Nombre del emisor, dirección, teléfono, email, etc.

### 5. Timbrado y Numeración
- `dNumTim`, `dEst`, `dPunExp` y `dNumDoc` deben estar dentro de los rangos autorizados para el emisor.
- En ambiente de **TEST** es muy común recibir rechazos tipo "1101 - TEST - Número de timbrado inválido" o "1107 - TEST - Fecha de inicio de vigencia del timbrado incorrecta". Son normales mientras configuras los datos de prueba.

### 6. Reingreso vs Nuevo Documento
Según el protocolo de SIFEN:
- Si un documento es rechazado **y no ha sido inutilizado**, puedes **reingresarlo** usando el **mismo número de documento**.
- El sistema generará un **nuevo CDC**.
- Para hacer reingreso, usa la misma combinación de timbrado + establecimiento + punto + número de documento.
- Si quieres "olvidar" el intento anterior, puedes inutilizar el número y usar uno nuevo.

El script soporta ambos modos mediante `--retry` y `--reingreso`.

### 7. Estados comunes de SIFEN (interpretación práctica)
- `SOL.APROBACION` / `ENVIADO_A_SIFEN`: Normal justo después de generar. Espera unos segundos/minutos.
- `Aprobado` / `Aprobado con observación`: ¡Éxito!
- `Rechazado`: Revisa `desc_sifen`. Los más comunes en TEST son por timbrado o actividad económica.
- Rechazos con código 11xx suelen ser validaciones de timbrado/datos del emisor.

### 8. Estructura del DE
- Usa siempre `calcular_de` primero. Te ahorra errores de cálculo manual de bases gravadas, IVA por ítem, totales, etc.
- Para **crédito**: `iCondOpe: "2"`, `iCondCred: "1"`, `dPlazoCre: "30 dias"` (o el que corresponda).
- El receptor **siempre** debe tener `dEmailRec` (obligatorio para Factura Segura aunque no lo sea estrictamente para SIFEN).
- `cUniMed` casi siempre es "77" (UNIDAD) en la mayoría de integraciones simples.

## Estructura del Proyecto

```
facturasegura-holamundo/python/
├── examples/
│   ├── test_esi.py              # Script principal (login + flujo completo + reingreso)
│   └── poll_cdc_status.py       # Polling de estado (útil para monitoreo)
├── requirements.txt
├── .env.example
├── README.md
└── LICENSE
```

## Variables de Entorno Recomendadas

Usa un archivo `.env` (nunca lo subas a git):

```env
ESI_EMAIL=tu-usuario-esi@ejemplo.com
ESI_PASSWORD=tu-password-seguro
```

El script acepta los valores también por argumentos de línea de comandos (más seguro para CI/CD).

## Consejos de Producción

- Nunca hardcodees credenciales.
- Usa el canary pre-flight antes de cualquier generación masiva.
- Maneja reintentos con backoff cuando recibas estados intermedios.
- Guarda el CDC generado + el response completo para auditoría.
- En producción considera usar colas y workers para no bloquear procesos de facturación.
- Monitorea los rechazos de SIFEN (muchos son por datos del emisor desactualizados).

## Contribuir

¡Este proyecto es un punto de partida! Si tienes mejoras, más ejemplos (notas de crédito, remisiones, cancelaciones, inutilizaciones, etc.), o lecciones aprendidas, por favor abre un Pull Request o Issue.

## Licencia

Este proyecto está licenciado bajo la **Apache License 2.0** - ver el archivo [LICENSE](LICENSE) para más detalles.

## Agradecimientos

- Al equipo de Factura Segura por la plataforma y la documentación del ESI.
- A la comunidad que está integrando SIFEN y compartiendo conocimiento.

---

**¿Empezando con ESI?**  
Este repositorio es intencionalmente simple y bien comentado. Lee el código de los ejemplos + este README. Es la forma más rápida de entender cómo funciona realmente la integración.

¡Éxitos con tu integración! Si te sirve, considera darle una estrella al repositorio para que más gente lo encuentre. 🚀