---
description: Contrato del flujo ESI. Aplica al leer o editar el flujo, los ejemplos o la documentación de operaciones.
paths:
  - "README.md"
  - "python/README.md"
  - "python/TOKEN.md"
  - "python/Ejemplos-API.md"
  - "python/examples/**"
  - "**/examples/**"
globs:
  - "README.md"
  - "python/README.md"
  - "python/TOKEN.md"
  - "python/Ejemplos-API.md"
  - "python/examples/**"
  - "**/examples/**"
alwaysApply: false
---

# Flujo ESI

ESI es la interoperación de sistemas externos (*External System Integration*) de Factura Segura con el Sistema Integrado de Facturación Electrónica Nacional (SIFEN).

Todo ejemplo, en cualquier lenguaje, sigue este orden. Los nombres de las operaciones no se traducen.

0. **Test de login.** `POST {BASE_URL}/login?include_auth_token` con `email` y `password` en claro. La respuesta útil es `response.user.authentication_token`. Si no está, detené el flujo. No llames al canary ni emitas.
1. **Canary previo.** `POST {BASE_URL}/misife00/v1/esi` con header `Authentication-Token` y operación `get_estado_sifen` sobre un código de control (CDC) conocido de ese emisor. Si `code` no es 0, no generes.
2. **`calcular_de`.** Documento electrónico (DE) resumido. No crea la factura. El DE completo vuelve en `results[0].DE`.
3. **`generar_de`.** Ese DE completo. Guardá `results[0].CDC`.
4. **Canary posterior.** `get_estado_sifen` del CDC nuevo, con el mismo `dRucEm`. `Aprobado` cierra. `SOL.APROBACION` y `ENVIADO_A_SIFEN` siguen en proceso. Un rechazo se lee en `desc_sifen` y `error_sifen`.
5. **Reingreso o número nuevo.** Reingreso: el mismo `dNumDoc`, solo si el documento fue rechazado y no está inutilizado. Si no, el siguiente número de 7 dígitos.

El header de las operaciones es `Authentication-Token`. No uses `Authorization: Bearer` ni `POST /misife00/auth/login` (ese login es de la aplicación del facturador).

`dRucEm` es el Registro Único de Contribuyentes (RUC) sin dígito verificador. Tiene que estar asociado al usuario y coincidir con el RUC dentro del CDC (posiciones 3 a 10, sin ceros a la izquierda).

Cada factura lleva un solo `dEmailRec`. Las descripciones de `gActEco` y la fecha `dFeIniT` se copian del portal, no se redactan.

Detalle de token: `python/TOKEN.md`. Cuerpos JSON: `python/Ejemplos-API.md`. Implementación de referencia: `python/examples/test_esi.py`.
