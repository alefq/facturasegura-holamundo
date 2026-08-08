# Ejemplos de Llamadas a la API ESI de Factura Segura

Este documento muestra ejemplos reales (con datos de prueba) de las llamadas al endpoint ESI (`/misife00/v1/esi`) y, al final, un **complemento** para listar facturas emitidas vía MSF (`/misife00/v1/msf`, operación `lst_de`).

**Base URL de pruebas:** `https://apitest.facturasegura.com.py`

**Header de autenticación (siempre requerido):**
```http
Authentication-Token: <tu-token>
```

---

## 1. Login (obtener token)

```bash
curl -X POST https://apitest.facturasegura.com.py/login?include_auth_token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tu-email@ejemplo.com",
    "password": "tu-password"
  }'
```

**Respuesta (resumida):**
```json
{
  "meta": { "code": 200 },
  "response": {
    "user": {
      "authentication_token": "eyJ2ZGVyIjoiNSIsInVpZCI6I..."
    }
  }
}
```

Usa el valor de `authentication_token` en el header `Authentication-Token` de todas las llamadas posteriores.

---

## 2. Canary Pre-Flight (get_estado_sifen)

Se recomienda siempre consultar primero un CDC conocido antes de generar documentos reales.

```bash
curl -X POST https://apitest.facturasegura.com.py/misife00/v1/esi \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: TU_TOKEN" \
  -d '{
    "operation": "get_estado_sifen",
    "params": {
      "CDC": "01009643435001001000003812024070716524190789",
      "dRucEm": "964343"
    }
  }'
```

**Respuesta de ejemplo (en ambiente de TEST):**
```json
{
  "code": 0,
  "description": "OK",
  "operation_info": {
    "id": "05f2afe4-07e6-4304-af94-ca463c64227b"
  },
  "results": [
    {
      "estado_sifen": "Rechazado",
      "desc_sifen": "1101 - TEST - Número de timbrado inválido",
      "error_sifen": "",
      "fch_sifen": "2025-01-03 14:09:07",
      "estado_can": "",
      "desc_can": "",
      "error_can": "",
      "fch_can": "",
      "estado_inu": "",
      "desc_inu": "",
      "error_inu": "",
      "fch_inu": "",
      "reintentos": "0"
    }
  ]
}
```

> Si `code != 0` → no continúes con la generación.

---

## 3. calcular_de (DE resumido)

Envías solo los datos de entrada. La API te devuelve el DE completo con todos los cálculos.

```bash
curl -X POST https://apitest.facturasegura.com.py/misife00/v1/esi \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: TU_TOKEN" \
  -d '{
    "operation": "calcular_de",
    "params": {
      "DE": {
        "iTipEmi": "1",
        "iTiDE": "1",
        "dNumTim": "00964343",
        "dFeIniT": "2024-04-02",
        "dEst": "001",
        "dPunExp": "001",
        "dNumDoc": "1000002",
        "dFeEmiDE": "2026-06-06T12:00:00",
        "iTipTra": "1",
        "iTImp": "1",
        "cMoneOpe": "PYG",
        "dCondTiCam": "1",
        "dTiCam": "1",
        "dRucEm": "964343",
        "dDVEmi": "5",
        "iTipCont": "2",
        "dNomEmi": "EMISOR DE PRUEBA",
        "dDirEmi": "DIRECCION FISCAL DEL EMISOR",
        "dNumCas": "123",
        "cDepEmi": "1",
        "dDesDepEmi": "CAPITAL",
        "cCiuEmi": "1",
        "dDesCiuEmi": "ASUNCION (DISTRITO)",
        "dTelEmi": "021123456",
        "dEmailE": "emisor.pruebas@ejemplo.com",
        "gActEco": [
          {"cActEco": "62010", "dDesActEco": "Actividades de programación informática"},
          {"cActEco": "62020", "dDesActEco": "Actividades de consultoría y gestión de servicios informáticos"},
          {"cActEco": "74909", "dDesActEco": "Otras actividades profesionales, científicas y técnicas n.c.p."}
        ],
        "iNatRec": "1",
        "iTiOpe": "1",
        "cPaisRec": "PRY",
        "iTiContRec": "1",
        "dRucRec": "80056313",
        "dDVRec": "1",
        "iTipIDRec": "0",
        "dNumIDRec": "0",
        "dNomRec": "RECEPTOR DE PRUEBA S.A.",
        "dEmailRec": "receptor.pruebas@ejemplo.com",
        "iIndPres": "1",
        "iCondOpe": "2",
        "iCondCred": "1",
        "dPlazoCre": "30 dias",
        "gCamItem": [
          {
            "dCodInt": "DSW001",
            "dDesProSer": "Desarrollo de software",
            "cUniMed": "77",
            "dCantProSer": "1",
            "dPUniProSer": "5500000",
            "dDescItem": "0",
            "dDescGloItem": "0",
            "dAntPreUniIt": "0",
            "dAntGloPreUniIt": "0",
            "iAfecIVA": "1",
            "dPropIVA": "100",
            "dTasaIVA": "10"
          }
        ]
      }
    }
  }'
```

El response contiene el objeto `DE` completo con todos los totales calculados.

---

## 4. generar_de

Se envía el objeto `DE` completo que devolvió `calcular_de` (más algunos campos que a veces hay que asegurar).

```bash
curl -X POST https://apitest.facturasegura.com.py/misife00/v1/esi \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: TU_TOKEN" \
  -d '{
    "operation": "generar_de",
    "params": {
      "DE": { ... objeto DE completo que viene de calcular_de ... }
    }
  }'
```

**Respuesta de éxito:**
```json
{
  "code": 0,
  "description": "OK",
  "operation_info": {
    "id": "b970ae4b-8161-4ce4-9e52-a98b4fa16379"
  },
  "results": [
    {
      "CDC": "01009643435001001100000222026060618047294391"
    }
  ]
}
```

**Respuesta de error común:**
```json
{
  "code": -80003,
  "description": "No se encuentra el parametro: 'CDC'",
  ...
}
```

---

## 5. get_estado_sifen (consulta de estado)

```bash
curl -X POST https://apitest.facturasegura.com.py/misife00/v1/esi \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: TU_TOKEN" \
  -d '{
    "operation": "get_estado_sifen",
    "params": {
      "CDC": "01009643435001001100000222026060618047294391",
      "dRucEm": "964343"
    }
  }'
```

### Ejemplos de respuestas de estado

**En proceso:**
```json
{
  "estado_sifen": "SOL.APROBACION",
  "desc_sifen": "",
  "fch_sifen": "2026-06-06 18:13:05",
  ...
}
```

**Enviado a SIFEN:**
```json
{
  "estado_sifen": "ENVIADO_A_SIFEN",
  "desc_sifen": "0300 - Lote recibido con éxito",
  "fch_sifen": "2026-06-06 18:14:03",
  ...
}
```

**Aprobado:**
```json
{
  "estado_sifen": "Aprobado",
  "desc_sifen": "0260 - Aprobado",
  "fch_sifen": "2026-06-06 18:14:03",
  ...
}
```

**Rechazado (ejemplo por timbrado):**
```json
{
  "estado_sifen": "Rechazado",
  "desc_sifen": "1107 - TEST - Fecha de inicio de vigencia del timbrado incorrecta",
  ...
}
```

**Rechazado (ejemplo por actividad económica):**
```json
{
  "estado_sifen": "Rechazado",
  "desc_sifen": "1262 - TEST - Descripción de la actividad económica no corresponde al código",
  ...
}
```

---

## 6. Reingreso (mismo número de documento)

Para reingresar un documento rechazado (mientras no esté inutilizado), se usa el **mismo `dNumDoc`**.

Ejemplo de cómo modificar el DE antes de reintentar:

```json
{
  "dNumDoc": "1000002",           // ← mismo número
  "dFeEmiDE": "2026-06-06T21:13:03",  // ← actualizar fecha
  ... resto de los datos ...
}
```

Luego se vuelve a llamar `calcular_de` + `generar_de` con ese DE.

El script de Python lo hace automáticamente cuando se usa la bandera `--retry --reingreso`.

---

## 7. Listar facturas emitidas (complemento MSF: `lst_de`)

El **ESI** (External System Integration) documentado en el Manual Técnico (`/misife00/v1/esi`) **no** expone una operación de listado de documentos. Para consultar los **documentos electrónicos (DE)** ya emitidos de un emisor se usa el endpoint **MSF** con la operación `lst_de`, reutilizando el mismo header `Authentication-Token` del login.

| Concepto | Valor |
|----------|--------|
| Endpoint | `POST /misife00/v1/msf` |
| Operación | `lst_de` |
| Autenticación | `Authentication-Token` (mismo del login ESI) |
| Uso típico | Conciliación, tablero, “¿qué facturas hay en test?” |

**Parámetros:**

| Parámetro | Descripción |
|-----------|-------------|
| `dRucEm` | Registro Único de Contribuyente (RUC) del emisor, **sin** dígito verificador |
| `iTiDE` | Tipo de DE. `1` = factura electrónica (el caso más habitual en este ejemplo) |
| `page` | Página de resultados (entero positivo). El tamaño de página lo define el servidor |

**Requisitos del usuario:** cuenta activa y permisos para invocar `/misife00/v1/msf` sobre el RUC consultado (en pruebas suele bastar un usuario con rol de cliente de API asociado al emisor). Si el login funciona para ESI pero `lst_de` devuelve 401/403 o `code` negativo, revisá roles y asociación al emisor con soporte de Factura Segura.

```bash
curl -X POST https://apitest.facturasegura.com.py/misife00/v1/msf \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: TU_TOKEN" \
  -d '{
    "operation": "lst_de",
    "params": {
      "dRucEm": "964343",
      "iTiDE": "1",
      "page": "1"
    }
  }'
```

**Respuesta de ejemplo (ambiente de TEST, resumida):**
```json
{
  "code": 0,
  "description": "OK",
  "operation_info": {
    "id": "074e5103-d97f-4731-8609-eb715ac3a567"
  },
  "results": [
    {
      "total": 89,
      "page": 1,
      "page_size": 10,
      "list": [
        {
          "id": "4461",
          "dEst": "001",
          "dPunExp": "001",
          "dNumDoc": "1000004",
          "dFeEmiDe": "2026-06-11T21:33:58",
          "cdc": "01009643435001001100000412026061110298577961",
          "dRucRec": "2595733-3",
          "dNomRec": "Azpa",
          "estado_sifen": "Aprobado",
          "desc_sifen": "0260 - Aprobado",
          "error_sifen": "",
          "cmoneope": "PYG",
          "dtotgralope": "27000",
          "dNumTim": "00964343",
          "iTiDE": "1",
          "fch_sifen": "2026-06-11 21:34:04.000",
          "fch_upd": "2026-06-11 21:34:14.150"
        }
      ]
    }
  ]
}
```

**Campos útiles de cada ítem en `list`:**

| Campo | Significado |
|-------|-------------|
| `dNumDoc` | Número de documento |
| `dEst` / `dPunExp` | Establecimiento y punto de expedición |
| `cdc` | Código de Control (CDC) del DE |
| `estado_sifen` | Estado en SIFEN (`Aprobado`, `Rechazado`, `Reingresado`, etc.) |
| `dtotgralope` | Total de la operación |
| `dNomRec` / `dRucRec` | Receptor |

**Script de referencia en este repo:**

```bash
python examples/list_facturas.py --ruc 964343 --page 1
python examples/list_facturas.py --ruc 964343 --page 1 --json
```

> **No confundir** con `get_estado_sifen` (consulta **un** CDC conocido vía ESI). `lst_de` es un **listado paginado** de DE del emisor vía MSF.

---

## Notas importantes

- El campo `operation_info.id` que viene en todas las respuestas es muy útil para debugging con el equipo de soporte de Factura Segura.
- En ambiente de **TEST** es normal recibir rechazos con prefijo "TEST -". Sirven para validar que la integración está bien hecha.
- Siempre actualiza `dFeEmiDE` en cada intento (nuevo o reingreso).
- El listado de facturas (`lst_de`) es una operación **complementaria** al flujo ESI de generación; no reemplaza el canary ni el envío a SIFEN.

---

Estos ejemplos están basados en pruebas reales realizadas contra el ambiente de test de Factura Segura usando el RUC emisor **964343-5** y receptor **80056313-1**.