# Instrucciones para agentes

Este archivo es la entrada para cualquier agente (Claude Code, Cursor, Codex, Grok u otro). Leelo antes de editar o de ejecutar ejemplos.

El repositorio es el ejemplo abierto de interoperación de sistemas externos (ESI, *External System Integration*) de Factura Segura hacia el Sistema Integrado de Facturación Electrónica Nacional (SIFEN). La referencia ejecutable está en `python/`.

## Cómo se rutean las reglas

Las reglas viven en `.agents/rules/`. Cada una tiene un frente YAML:

- `description`: cuándo usarla.
- `paths`: globs al estilo Claude Code. Si el trabajo toca esos archivos, aplicá esa regla.
- `globs`: los mismos patrones, para agentes que rutean con ese nombre.
- `alwaysApply`: si es `false`, no la cargues en tareas que no coinciden.

Si tu entorno no carga reglas por archivo, seguí esta tabla y abrí el markdown antes de actuar.

| Si la tarea es | Leé |
|---|---|
| Cualquier cambio de flujo, operación o ejemplo ESI | `.agents/rules/flujo-esi.md` |
| Probar login, canary, emisión, estado, listado o polling | `.agents/rules/flujo-esi.md` y `.agents/rules/probar-esi.md` |
| Agregar un caso, otro tipo de documento o otro lenguaje | `.agents/rules/flujo-esi.md` y `.agents/rules/agregar-casos.md` |

`flujo-esi.md` es el contrato. Las otras dos dicen cómo ejecutarlo o cómo extenderlo. No inventes un flujo paralelo.

## Qué no hace este repositorio

La asociación de un usuario ESI a un Registro Único de Contribuyentes (RUC) la hace el dueño de ese RUC en el portal. No agregues aquí pantallas de consola de administración ni un alta manual de usuarios.

No subas `.env`, contraseñas ni el `authentication_token` completo. El archivo de ejemplo es `python/.env.example`.

## Dónde está la documentación

- Token y paso 0: `python/TOKEN.md`
- Cuerpos de las llamadas: `python/Ejemplos-API.md`
- Flujo que todo lenguaje debe repetir: `README.md`
- Ejemplo Python: `python/examples/test_esi.py`
