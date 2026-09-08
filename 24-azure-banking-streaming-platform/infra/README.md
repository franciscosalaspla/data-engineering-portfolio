# Infraestructura `dev`

Este directorio representa la infraestructura objetivo del Proyecto 24. La compilación es local y
no autentica contra Azure.

## Estructura

- `main.bicep`: punto de entrada a nivel de resource group;
- `environments/dev.bicepparam`: valores no sensibles y marcadores de compilación;
- `modules/`: siete módulos de recursos independientes;
- `bicepconfig.json`: reglas de lint elevadas a error.

## Validación offline

Con Bicep CLI 0.46.1 instalado:

```bash
scripts/validate_bicep.sh
```

También puede indicarse una ruta explícita:

```bash
BICEP_BIN=/ruta/al/bicep scripts/validate_bicep.sh
```

El script usa `--no-restore`, compila hacia la salida estándar y no conserva ARM JSON generado.
No ejecuta `login`, `validate`, `what-if`, `deploy` ni ninguna operación sobre una suscripción.

## Bloqueo previo al despliegue

`dev.bicepparam` contiene IDs de Microsoft Entra deliberadamente inválidos. En el Hito 3 deberán
reemplazarse por valores verificados, después de revisar costo, permisos y teardown. Este archivo no
debe contener secretos.
