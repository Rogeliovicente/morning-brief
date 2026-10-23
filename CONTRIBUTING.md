# Preparar y publicar una edición

La edición piloto del 22 de octubre de 2026 permanece en `index.html`. El flujo genera cada edición nueva en `/latest/`; no reescribe la portada ni crea una página de archivo. GitHub conserva el historial de cambios del contenido, pero todavía no hay un archivo público de ediciones anteriores.

## Preparar contenido

1. Crea una rama para la edición.
2. Copia `content/edition.example.json` como `content/edition.json`.
3. Completa el JSON. No agregues noticias por medio de esta automatización: cada pieza debe pasar por investigación y revisión editorial antes de incorporarse.
4. Ejecuta `python scripts/edition.py validate` localmente o abre un pull request.
5. Revisa el artefacto `edition-preview` del flujo de GitHub Actions. El validador comprueba la estructura, cinco secciones, campos requeridos, fechas, identificadores y enlaces HTTPS. No comprueba la veracidad de una afirmación ni sustituye el criterio editorial.

## Revisar y publicar

1. Abre un pull request hacia `main` con `content/edition.json`. El flujo valida y genera una vista previa como artefacto; no publica desde ramas ni pull requests.
2. Haz la revisión editorial del contenido y aprueba/integra el pull request solo cuando esté listo.
3. En **Actions → Publish The Morning Brief → Run workflow**, selecciona `publish` para publicar manualmente. El flujo está deliberadamente sin calendario.
4. La publicación requiere que GitHub Pages esté configurado para usar **GitHub Actions**. El entorno `github-pages` puede requerir aprobación adicional si se configuran revisores en **Settings → Environments**.

La salida publicada incluye el `index.html` existente sin modificar y la edición actual en `/latest/`. Una edición posterior reemplazará el contenido de `/latest/`; esta propuesta no implementa ni duplica el archivo histórico. Antes de mover la edición más reciente a la portada, deberá definirse ese archivo y una estrategia de migración segura.

## Ejecución local

```sh
python scripts/edition.py validate
python scripts/edition.py build --output-dir /tmp/morning-brief-preview
```

La plantilla es un ejemplo estructural, no una edición lista para publicar. No se debe copiar directamente como contenido aprobado.
