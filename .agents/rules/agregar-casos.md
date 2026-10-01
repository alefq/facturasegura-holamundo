---
description: Cómo agregar un caso de prueba ESI copiando la documentación o un ejemplo existente. Otro documento, otra operación u otro lenguaje.
paths:
  - "python/**"
  - "**/examples/**"
  - "**/README.md"
  - "python/Ejemplos-API.md"
globs:
  - "python/**"
  - "**/examples/**"
  - "**/README.md"
  - "python/Ejemplos-API.md"
alwaysApply: false
---

# Agregar un caso

Leé antes `.agents/rules/flujo-esi.md`. Un caso de este repositorio es un ejemplo ejecutable, del mismo estilo que `python/examples/`, más el cuerpo documentado en `python/Ejemplos-API.md` cuando el JSON es nuevo. No agregues un framework de tests.

## De dónde se copia

1. Buscá la operación en `python/Ejemplos-API.md`.
2. Si ya hay script, partí de ese archivo: `test_esi.py` para emitir, `poll_cdc_status.py` para esperar un estado, `list_facturas.py` para el listado.
3. El DE resumido de la factura de prueba sale de `build_resumido_de()` o del JSON de `calcular_de` en `Ejemplos-API.md`. No armes campos de emisor, timbrado ni actividades económicas desde cero.

## Qué tiene que cumplir el caso nuevo

- Empieza por el login (`/login?include_auth_token`). Si no hay `authentication_token`, el caso termina ahí.
- Después corre el canary (`get_estado_sifen`) antes de crear un documento.
- Usa `BASE_URL` del entorno y el header `Authentication-Token`.
- `dNumDoc` son 7 dígitos libres. No reutilices un número aprobado. El reingreso usa el mismo número solo en un documento rechazado y no inutilizado.
- Un solo `dEmailRec` por documento.
- `gActEco` y `dFeIniT` quedan iguales a lo ya registrado en el ejemplo, salvo que la documentación del caso diga otro valor copiado del portal.
- Conservá `operation_info.id` en la salida.

Si el caso es otra operación del manual (`sol_cancelacion`, `sol_inutilizacion`, otro tipo de documento electrónico), documentá el request y una respuesta de ejemplo en `python/Ejemplos-API.md`, con el mismo nivel que las secciones que ya existen. El script nuevo va en `python/examples/` y se nombra por la operación.

## Otro lenguaje

Copiá la carpeta `python/` como base. Mantené los nombres `calcular_de`, `generar_de` y `get_estado_sifen`. El `README.md` de esa carpeta explica el paso 0, el canary, el reingreso y trae un `.env.example` sin secretos. La estructura esperada está en `README.md` del repositorio.

No documentes en el caso el alta del usuario ni la asociación al RUC. Eso lo hace el dueño del RUC en el portal. El caso empieza cuando el usuario ya puede pedir token.
