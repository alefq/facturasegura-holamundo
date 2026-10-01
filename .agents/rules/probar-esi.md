---
description: Cómo probar el ESI con los ejemplos que ya están en el repositorio. Login, canary, emisión, estado, listado y polling.
paths:
  - "python/examples/**"
  - "python/.env.example"
  - "python/TOKEN.md"
  - "python/Ejemplos-API.md"
  - "python/README.md"
globs:
  - "python/examples/**"
  - "python/.env.example"
  - "python/TOKEN.md"
  - "python/Ejemplos-API.md"
  - "python/README.md"
alwaysApply: false
---

# Probar los ejemplos ESI

Leé antes `.agents/rules/flujo-esi.md`. No saltees el paso 0.

Trabajá en `python/`, con el entorno virtual activo y las dependencias de `requirements.txt`. Copiá `.env.example` a `.env` si no existe. No commitees `.env`.

Variables: `BASE_URL`, `ESI_EMAIL`, `ESI_PASSWORD`. Para el listado, `EMISOR_RUC`. En pruebas, `BASE_URL` es `https://apitest.facturasegura.com.py`. Producción solo si quien pide la prueba lo dice.

## Qué comando corre qué

Desde `python/`:

```bash
# Paso 0. Solo login. Si falla, no sigas.
python examples/test_esi.py --login-only

# Flujo completo. dNumDoc de 7 dígitos que no esté aprobado.
python examples/test_esi.py --num-doc 1000091 --retry

# Canary o estado de un CDC, sin emitir.
python examples/test_esi.py --get-estado CDC_DE_44_DIGITOS --dRucEm 964343

# Esperar el estado final de un CDC recién emitido.
python examples/poll_cdc_status.py --cdc CDC_DE_44_DIGITOS --ruc 964343 --interval 10 --max-seconds 120

# Listado. No es operación ESI: es POST /misife00/v1/msf, operación lst_de, con el mismo token.
python examples/list_facturas.py --ruc 964343 --page 1
```

Los scripts leen `ESI_EMAIL` y `ESI_PASSWORD` del entorno. Podés pasar `--email` y `--password` solo en local. No los dejes en un historial que se vaya a publicar.

## Qué tiene que verse

- Paso 0: HTTP 200 y `authentication_token`. En la salida del script alcanza con el prefijo del token.
- Canary previo: `code` 0. Si no, no ejecutes `generar_de`.
- `calcular_de`: `code` 0 y `results[0].DE`.
- `generar_de`: `code` 0 y un CDC de 44 dígitos.
- Canary posterior: `estado_sifen`. Esperá cerca de un minuto antes de dar el estado por cerrado.

Informá `code`, `description`, el CDC y `operation_info.id`. No pegues la contraseña ni el token completo en el informe ni en un archivo del repositorio.

Si el login responde sin token, el fallo es de usuario o de ambiente. No lo conviertas en un reintento de emisión.
