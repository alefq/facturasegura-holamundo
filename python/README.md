# Factura Segura ESI - Hola Mundo (Python)

Esta carpeta contiene la **implementación de referencia** del proyecto [Factura Segura ESI – Hola Mundo](..).

**Proyecto de ejemplo abierto** para promover el uso del **ESI (External System Integration)** de [Factura Segura](https://facturasegura.com.py), un proveedor de servicios de facturación electrónica en Paraguay que actúa como intermediario hacia **SIFEN** (Sistema Integrado de Facturación Electrónica Nacional), el sistema oficial del Estado administrado por la DNIT.

Este es el ejemplo más completo y didáctico del repositorio. Sirve como **implementación de referencia y plantilla** para quien quiera crear una implementación en otro lenguaje o plataforma (Node.js, PHP, Go, integraciones con Odoo, ERPNext, etc.).

Cada nuevo subproyecto debería:
- Seguir el mismo flujo canónico de 6 pasos.
- Incluir un canary pre-flight como gate.
- Documentar patrones recomendados y errores comunes.
- Mantener un nivel de claridad similar al de este README.

Ver también el [README general del proyecto](../README.md) (especialmente las secciones de [Patrones recomendados](../README.md#patrones-recomendados-mejores-prácticas-que-surgieron-de-las-pruebas) y [Errores comunes](../README.md#errores-comunes-faq-rápida)) para entender la visión multi-plataforma y las guías de contribución.

## 🎯 Objetivo

Este README y los scripts que lo acompañan tienen dos propósitos:

- Facilitar el onboarding de desarrolladores e integradores al ecosistema ESI de Factura Segura.
- Servir como **plantilla y referencia de calidad** para otras implementaciones dentro de este repositorio multi-plataforma.

Al copiar esta estructura a un nuevo lenguaje o ERP, se espera que el nuevo `README.md` mantenga un nivel similar de claridad, ejemplos prácticos y explicación de patrones (ver también el [README general](../README.md)).

- Proporcionar código listo para copiar, adaptar y usar en producción.
- Compartir lecciones aprendidas de la documentación oficial + pruebas reales en ambiente de test.
- Servir como base para proyectos más complejos (facturación masiva, integración con ERPs, etc.).

**Licencia:** Apache License 2.0 (ver [LICENSE](../LICENSE) en la raíz del repositorio).

> **Documentación oficial del ESI**  
> Para solicitar el Manual Técnico completo del ESI y resolver dudas técnicas sobre la integración, escribí a:  
> **soporte@facturasegura.com.py**

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

### 6. Ejemplos detallados de llamadas a la API

Para ver los payloads completos de `calcular_de`, `generar_de`, `get_estado_sifen` (incluyendo respuestas reales de diferentes estados), reingreso y **listado de facturas emitidas**, consulta el archivo:

→ **[Ejemplos de Llamadas a la API](Ejemplos-API.md)**

Este documento es especialmente útil si estás implementando en otro lenguaje y quieres ver exactamente qué JSON se envía y qué se recibe.

**Mejoras implementadas** (basadas en feedback):
- `BASE_URL` se puede configurar vía variable de entorno (o `.env`) y se centralizó en los scripts.
- Soporte nativo de `.env` con `python-dotenv` (los scripts cargan automáticamente BASE_URL, ESI_EMAIL y ESI_PASSWORD).
- Mejor manejo de errores de red (timeouts, connection errors, HTTP errors con mensajes claros).
- `--num-doc` para controlar el número de documento desde línea de comandos (evita hardcode y colisiones).
- `BASE_URL` centralizado (fácil cambiar entre test y producción).
- Ejemplo didáctico de **listado de facturas emitidas** (`list_facturas.py` + sección 7 de [Ejemplos-API.md](Ejemplos-API.md)).

> **Este README como referencia**  
> Si estás creando una implementación en otro lenguaje, te recomendamos usar este archivo como ejemplo del nivel de detalle y claridad que se espera en cada subcarpeta. El [README general del proyecto](../README.md) también contiene las secciones de patrones y errores comunes que deberían estar reflejadas (adaptadas) en cada implementación.

### 7. Polling de estado (útil para monitorear)

```bash
python examples/poll_cdc_status.py \
  --email "$ESI_EMAIL" --password "$ESI_PASSWORD" \
  --cdc 01009643435001001100000222026060612022117504 \
  --ruc 964343 \
  --interval 10 \
  --max-seconds 120
```

El script de polling también respeta `BASE_URL` desde el entorno.

### 8. Listar facturas emitidas (complemento al ESI)

El flujo canónico del **ESI** (External System Integration) genera y consulta **un** documento (por Código de Control, CDC). Para **listar** los documentos electrónicos (DE) ya emitidos de un emisor se usa la operación `lst_de` en el endpoint **MSF** (`/misife00/v1/msf`), con el mismo `Authentication-Token` del login.

```bash
# Tabla resumen (página 1, facturas iTiDE=1, RUC del .env o default de prueba)
python examples/list_facturas.py

# Página concreta + RUC explícito
python examples/list_facturas.py --ruc 964343 --page 1

# Respuesta JSON completa (útil al portar a otro lenguaje)
python examples/list_facturas.py --ruc 964343 --page 1 --json
```

Detalles de payload, respuesta y campos: sección **7** de [Ejemplos-API.md](Ejemplos-API.md).

> **Importante:** `lst_de` **no** forma parte del contrato del Manual Técnico ESI sobre `/misife00/v1/esi`. Es un complemento de consulta. El usuario debe tener permisos sobre `/msf` y sobre el Registro Único de Contribuyente (RUC) emisor.

## 📚 Lecciones Aprendidas de la Documentación y Pruebas Reales

> **Nota**: Los patrones recomendados y la lista de errores comunes también están documentados de forma más general en el [README del proyecto](../README.md#patrones-recomendados-mejores-prácticas-que-surgieron-de-las-pruebas) y en la sección de [Errores comunes](../README.md#errores-comunes-faq-rápida).

### 1. Autenticación (lo más importante al principio)
- Se hace un login normal contra `/login?include_auth_token`.
- El token importante es `authentication_token` (no el csrf_token).
- Se envía en el header `Authentication-Token` (no Authorization Bearer).
- El token puede dejar de funcionar después de un tiempo o si cambias la contraseña. Siempre refresca antes de flujos importantes.

**Cómo obtener la documentación oficial del ESI**  
Para solicitar el Manual Técnico completo y resolver dudas, escribí a:  
**soporte@facturasegura.com.py**

### 2. Operaciones principales del ESI
- **`calcular_de`**: Envías un DE "resumido" (solo datos de entrada). El sistema te devuelve el DE completo con todos los totales, bases gravadas, IVA, etc. calculados según reglas de SIFEN. **Muy recomendado** antes de generar.
- **`generar_de`**: Envías el DE completo. El sistema genera el XML, lo firma, genera el KuDE y lo envía a SIFEN.
- **`get_estado_sifen`**: Consulta el estado actual en SIFEN (Aprobado, Rechazado, SOL.APROBACION, ENVIADO_A_SIFEN, etc.). Muy útil como **canary test**.

### 2.1. Complemento: listar DE emitidos (MSF, no ESI)
- **`lst_de`** en `POST /misife00/v1/msf`: listado paginado por emisor (`dRucEm`) y tipo (`iTiDE`). Mismo token de login.
- Sirve para conciliación y para verificar en test “qué hay emitido” sin conocer de antemano el CDC.
- Ver `examples/list_facturas.py` y la sección 7 de [Ejemplos-API.md](Ejemplos-API.md).

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
- Si un documento es rechazado **y no ha sido inutilizado**, puedes **reingresarlo** usando el **mismo número de documento** (`--retry --reingreso`).
- El sistema generará un **nuevo CDC**.
- Para hacer reingreso, usa la misma combinación de timbrado + establecimiento + punto + número de documento.
- Si quieres "olvidar" el intento anterior, avanza al siguiente número (`--retry` sin `--reingreso`).

El script de Python implementa ambos comportamientos de forma explícita y es la referencia para cómo debería manejarse esto en otras plataformas.

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
│   ├── poll_cdc_status.py       # Polling de estado (útil para monitoreo)
│   └── list_facturas.py         # Listado paginado de DE emitidos (MSF lst_de)
├── requirements.txt
├── .env.example
├── Ejemplos-API.md
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

## Agradecimientos

- Al equipo de Factura Segura por la plataforma y la documentación del ESI.
- A la comunidad que está integrando SIFEN y compartiendo conocimiento.

---

**¿Empezando con ESI?**  
Este repositorio es intencionalmente simple y bien comentado. Lee el código de los ejemplos + este README. Es la forma más rápida de entender cómo funciona realmente la integración.

¡Éxitos con tu integración! Si te sirve, considera darle una estrella al repositorio para que más gente lo encuentre. 🚀