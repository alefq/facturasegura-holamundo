# Reglas de este repositorio

El índice para agentes está en [AGENTS.md](../AGENTS.md).

Cada archivo de `rules/` es una regla enrutable. El frente YAML trae `paths` (Claude Code) y `globs` (el mismo filtro con el nombre que usan otros agentes). `alwaysApply: false` significa que la regla se abre solo cuando la tarea o los archivos coinciden.

| Regla | Se usa para |
|---|---|
| [rules/flujo-esi.md](rules/flujo-esi.md) | Contrato del flujo ESI. Leela antes de probar o de agregar un caso. |
| [rules/probar-esi.md](rules/probar-esi.md) | Ejecutar los ejemplos que ya existen. |
| [rules/agregar-casos.md](rules/agregar-casos.md) | Sumar un caso siguiendo la documentación o un ejemplo ya escrito. |
