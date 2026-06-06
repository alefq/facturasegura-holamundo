# Factura Segura ESI – Hola Mundo

Ejemplos de integración con el **ESI (External System Integration)** de [Factura Segura](https://facturasegura.com.py), el proveedor que facilita la conexión con **SIFEN** (Sistema Integrado de Facturación Electrónica Nacional) de Paraguay, administrado por la DNIT.

Este repositorio nace con un objetivo claro: **reducir la curva de aprendizaje** de cualquiera que quiera integrar sistemas externos con Factura Segura de forma correcta, segura y siguiendo las mejores prácticas reales.

Cada implementación (por lenguaje o plataforma) cubre **exactamente el mismo flujo**, para que sea fácil comparar, portar código y mantener consistencia cuando se agreguen nuevos ejemplos.

## Filosofía del proyecto

- **Un solo flujo canónico** → todas las implementaciones hacen lo mismo.
- **Canary tests primero** → nunca generes un documento real sin antes validar que tu token y permisos funcionan.
- **Reingreso vs nuevo documento** → explicamos claramente cuándo usar el mismo `dNumDoc` y cuándo avanzar al siguiente.
- **Datos que realmente importan** → énfasis en que `gActEco`, fechas de timbrado y datos del emisor deben coincidir **exactamente** con lo registrado en el portal.
- **Listo para producción** → los ejemplos incluyen manejo de errores, logging claro y estructura que se puede copiar a proyectos reales.
- **Semilla para la comunidad** → la idea es que este repo se convierta en el punto de partida para integraciones en muchos lenguajes y ERPs.

## Cómo obtener la documentación oficial del ESI

Para acceder al **Manual Técnico del ESI** y a la documentación detallada del protocolo, escribí a:

**soporte@facturasegura.com.py**

Es el canal oficial para solicitar el acceso a la documentación completa y resolver dudas técnicas sobre la integración.

## Implementaciones disponibles

| Lenguaje / Plataforma | Carpeta          | Estado     |
|-----------------------|------------------|------------|
| Python                | [python/](python/) | Disponible |

> **Consejo**: Dentro de la carpeta `python/` encontrarás el archivo **[Ejemplos de Llamadas a la API](python/Ejemplos-API.md)** con los payloads reales de `calcular_de`, `generar_de`, `get_estado_sifen` y reingreso. Es muy útil como referencia cuando estés implementando en otro lenguaje.

## Implementaciones planeadas / deseadas

¡Contribuciones bienvenidas!

**Lenguajes / Runtimes**
- Node.js / TypeScript (con y sin framework)
- PHP (Laravel / Symfony / vanilla)
- Java / Kotlin (Spring Boot)
- Go
- .NET / C#
- Ruby

**Integraciones con ERPs open source**
- Odoo
- ERPNext / Frappe Framework
- Dolibarr
- Tryton
- Akaunting

**Otras integraciones útiles**
- Facturación masiva / batch
- Integración con tiendas (WooCommerce, Shopify vía apps)
- Microservicios / serverless (AWS Lambda, Cloud Functions, etc.)

## El flujo ESI que debe implementar todo ejemplo

Todos los subproyectos deben seguir este flujo base (con nombres de métodos adaptados al lenguaje):

1. **Login**  
   Obtener el `Authentication-Token` usando `/login?include_auth_token`.

2. **Canary pre-flight** (health-check)  
   Antes de generar cualquier documento real, consultar el estado de un CDC conocido (`get_estado_sifen`).  
   Si `code != 0` → abortar. Este paso evita generar documentos cuando hay problemas de token, permisos o conectividad.

3. **`calcular_de`**  
   Enviar un DE resumido.  
   La API devuelve el DE completo con todos los cálculos de IVA, bases gravadas, totales, etc. hechos según las reglas de SIFEN.

4. **`generar_de`**  
   Enviar el DE completo.  
   Factura Segura genera el XML, lo firma, genera el KuDE y lo envía a SIFEN.

5. **Canary post**  
   Consultar inmediatamente el estado del CDC recién generado para verificar que llegó a SIFEN (`SOL.APROBACION`, `ENVIADO_A_SIFEN`, etc.).

6. **Reintento / Reingreso** (cuando corresponde)  
   - Si el documento queda en estado `Rechazado` y el número **no fue inutilizado**, se puede hacer **reingreso** usando el **mismo `dNumDoc`**.
   - Si se prefiere descartar ese número, se avanza al siguiente (nuevo ingreso).
   - El script de Python soporta ambas modalidades con las flags `--retry` y `--reingreso`.

## Patrones recomendados (mejores prácticas que surgieron de las pruebas)

Estos patrones aparecen en todas las implementaciones saludables:

- **Canary pre-flight obligatorio**: Siempre consultar un CDC conocido antes de generar. Es el mejor "smoke test" de token + permisos + conectividad.
- **Canary post-generación**: Después de `generar_de`, consultar inmediatamente el estado del CDC. Permite detectar rápido si el documento quedó en `SOL.APROBACION`, `Rechazado`, etc.
- **Logging del `operation_info.id`**: Cada respuesta trae un `id` único. Guardarlo ayuda muchísimo para debugging con el equipo de soporte.
- **Manejo explícito de reingreso**: Diferenciar claramente entre "intentar con el mismo número" (`--reingreso`) vs "avanzar al siguiente número".
- **Validación estricta de datos del emisor**: Especialmente `gActEco` (las descripciones deben ser idénticas a las registradas) y `dFeIniT` del timbrado.
- **Manejo de estados intermedios**: `SOL.APROBACION` y `ENVIADO_A_SIFEN` son normales. No asumir que un `generar_de` exitoso significa que ya está aprobado.

## Estructura recomendada para nuevas implementaciones

Cada nuevo lenguaje o plataforma debe vivir en su propio subdirectorio y seguir una estructura similar:

```
<plataforma>/
├── README.md
├── .env.example
├── requirements.txt / package.json / composer.json / go.mod ...
├── examples/
│   ├── full_flow.py / index.js / ...
│   └── poll_status.py / ...
└── src/ (si aplica)
```

El `README.md` de cada subcarpeta debe ser **didáctico** (como el de Python), explicando:
- Cómo obtener un usuario ESI y autorizarlo
- El flujo paso a paso con los mismos nombres de operaciones
- Las trampas más comunes (descripciones de `gActEco`, fechas de timbrado, etc.)
- Cómo hacer reingreso
- Ejemplos de uso del canary pattern

## Errores comunes (FAQ rápida)

Durante las pruebas reales aparecieron estos rechazos frecuentes en ambiente de **TEST**:

| Código     | Mensaje típico                                      | Causa más común                                      | Solución |
|------------|-----------------------------------------------------|-------------------------------------------------------|----------|
| 1101       | TEST - Número de timbrado inválido                  | Timbrado no registrado o fecha incorrecta en el portal | Verificar que el timbrado y `dFeIniT` coincidan exactamente con lo cargado en Factura Segura |
| 1107       | TEST - Fecha de inicio de vigencia del timbrado incorrecta | `dFeIniT` no coincide con el timbrado registrado     | Usar exactamente la fecha que figura en el portal |
| 1262       | TEST - Descripción de la actividad económica no corresponde al código | `dDesActEco` no coincide con la descripción oficial del `cActEco` | Copiar **textualmente** las descripciones que aparecen en tu cuenta de Factura Segura (ej: "Actividades de programación informática") |

Otros tips:
- El `gActEco` debe listar las actividades **tal cual** están autorizadas para el emisor.
- El receptor siempre debe tener `dEmailRec` (lo exige Factura Segura aunque SIFEN no siempre lo haga obligatorio).
- En TEST es normal ver rechazos. El objetivo es validar que el flujo técnico funciona correctamente.

## Contribuir

1. Forkeá el repo.
2. Copiá la carpeta `python/` como base (es la implementación de referencia).
3. Adaptá el código a tu lenguaje/plataforma manteniendo la misma estructura de flujo.
4. Escribí un `README.md` claro y con ejemplos (idealmente siguiendo el mismo nivel de detalle que el de Python).
5. Abrí un Pull Request.

No es necesario que la implementación sea perfecta desde el primer día. El objetivo es tener un punto de partida funcional y bien documentado.

### Plantilla mínima recomendada para un nuevo `README.md`

Si estás empezando una implementación en otro lenguaje, te recomendamos incluir al menos:

- Cómo obtener un usuario ESI y pedir autorización (mencionar `soporte@facturasegura.com.py`)
- Instrucciones claras de instalación y ejecución (con venv o equivalente)
- Ejemplo de uso del flujo completo (login → canary pre → calcular_de → generar_de → canary post)
- Cómo hacer reingreso vs nuevo documento
- Tabla o lista de los errores comunes que detectaste en tu plataforma
- Ejemplo de `.env.example`

Esto ayuda a mantener la coherencia entre todas las implementaciones del repositorio.

## Licencia

Todo el contenido de este repositorio está bajo **Apache License 2.0**.

---
