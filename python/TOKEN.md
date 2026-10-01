# Token del ESI para emitir

Cuando el dueño de un Registro Único de Contribuyentes (RUC) ya asoció tu usuario en el portal de Factura Segura, el token y la emisión los manejás vos. Esta guía es esa parte.

La asociación a un RUC la hace el dueño de ese RUC en el portal. Hasta que tu correo figure asociado, el token no emite por ese emisor.

El flujo de una factura está implementado en [examples/test_esi.py](examples/test_esi.py). Los cuerpos de cada llamada están en [Ejemplos-API.md](Ejemplos-API.md). El manual de operaciones está en el [Manual técnico del ESI](https://docs.google.com/document/d/1DKiUHB9Vftn6gcBYDAKgayId_IEagBHELx68NQk-Pbc/edit?tab=t.0).

ESI es la interoperación de sistemas externos (*External System Integration*) de Factura Segura hacia el Sistema Integrado de Facturación Electrónica Nacional (SIFEN).

## Ambientes

El token de pruebas no sirve en producción. Pedilo en el mismo ambiente en el que te asociaron.

| Ambiente | Portal | API |
|---|---|---|
| Pruebas | https://test.facturasegura.com.py | https://apitest.facturasegura.com.py |
| Producción | https://portal.facturasegura.com.py | https://api.facturasegura.com.py |

## Paso 0. Test de login

Antes del canary, comprobá que el usuario ESI entra. Usá el correo y la contraseña con los que te registraste en el portal. La contraseña va en claro. Si esta llamada no devuelve `authentication_token`, no sigas.

```bash
python examples/test_esi.py --login-only
```

El token sigue vigente hasta que cambies esa contraseña. Guardalo en el sistema que va a facturar.

```bash
curl -sS -X POST 'https://apitest.facturasegura.com.py/login?include_auth_token' \
  -H 'Content-Type: application/json' \
  -d '{"email":"usuario-esi@ejemplo.com","password":"la-contraseña"}'
```

En producción, la misma llamada va a `https://api.facturasegura.com.py/login?include_auth_token`.

El token está en `response.user.authentication_token`. En cada operación se envía así:

```http
Authentication-Token: EL_TOKEN
```

El ejemplo de Python lo pide solo. En `python/.env`:

```env
BASE_URL=https://apitest.facturasegura.com.py
ESI_EMAIL=usuario-esi@ejemplo.com
ESI_PASSWORD=la-contraseña
```

```bash
python examples/test_esi.py --num-doc 1000091 --retry
```

Ese comando hace el paso 0 (login), el canary sobre un código de control (CDC) conocido, calcula la factura, la genera y vuelve a consultar el CDC nuevo. Si el login falla, no llega al canary.

## Paso 1. Canary: permiso sobre el RUC

Con el token del paso 0, consultá un CDC de ese emisor. `dRucEm` es el RUC sin dígito verificador y tiene que ser el que está dentro del CDC (posiciones 3 a 10, sin ceros a la izquierda).

```bash
curl -sS -X POST 'https://apitest.facturasegura.com.py/misife00/v1/esi' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authentication-Token: EL_TOKEN' \
  -d '{"operation":"get_estado_sifen","params":{"CDC":"CDC_DE_44_DIGITOS","dRucEm":"RUC_SIN_DV"}}'
```

`"code": 0` indica que el token y la asociación a ese RUC están en orden. Si el código es negativo, no generes: falta la asociación o el RUC no coincide.

## Emitir

1. `calcular_de` con el documento electrónico (DE) resumido. No crea la factura. Devuelve el DE completo en `results[0].DE`.
2. `generar_de` con ese DE completo. [examples/test_esi.py](examples/test_esi.py) completa `CDC`, `dCodSeg`, `dDVId`, `dSisFact` y `dInfAdic` si faltan.
3. Guardá `results[0].CDC`.
4. Esperá cerca de un minuto y consultá `get_estado_sifen` con ese CDC y el mismo `dRucEm`.

`dNumDoc` son 7 dígitos. Usá un número nuevo. Si ya existe, repetí con otro. Un documento rechazado que no quedó aprobado se reingresa con el mismo número:

```bash
python examples/test_esi.py --num-doc 1000091 --retry --reingreso
```

`Aprobado` cierra la prueba. `SOL.APROBACION` y `ENVIADO_A_SIFEN` siguen en proceso. Si está rechazado, mirá `desc_sifen` y `error_sifen`.

Los datos del emisor en el DE tienen que coincidir con lo cargado en el portal: timbrado, `dFeIniT` y las descripciones de `gActEco`.

## Varios RUC y varios correos

El mismo token factura para todos los RUC asociados a tu usuario. En cada llamada indicás el emisor con `dRucEm`.

Cada factura lleva un correo del emisor (`dEmailE`) y un correo del receptor (`dEmailRec`). `dEmailRec` es obligatorio y es un solo correo válido. Otra factura puede ir a otro correo. Cuando SIFEN aprueba el documento, Factura Segura envía el XML firmado y el KuDE (Kuatia de Documento Electrónico, la representación gráfica) al correo del receptor, y en copia oculta al emisor y al contador de ese RUC.
