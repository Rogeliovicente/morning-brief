---
name: morning-brief-editor
description: Investiga, verifica, redacta y publica The Morning Brief, revista de inteligencia y gestión tecnológica y educativa, con GitHub Pages.
---
# The Morning Brief
## Reglas editoriales
- Entrega de 10-12 minutos de lectura, español, formato responsivo rojo (#ed4746), carbón (#121215), amarillo (#f5c84c).
- Esenciales: gestión tecnológica e innovación (preferentemente 1-2 casos); XR y tecnologías emergentes; innovación educativa; benchmark universitario. Importantes: IA/agentes y riesgos/ciberseguridad/gobernanza. Ocasionales: investigación y mercado EdTech.
- Seleccionar 12-18 candidatos, preseleccionar 5-7, publicar 4-6 solo si pasan revisión. Diversificar industrias y proveedores; no permitir predominio automático de IA.
- Noticias prioritarias de 24-48 horas, normalmente máximo 14 días. Los casos de gestión pueden ser anteriores si siguen vigentes y se identifican como tales.
- Leer cada fuente específica antes de incluirla; cotejar titular, fecha, hallazgos, limitaciones y URL directa. Nunca vincular títulos concretos a homepages o catálogos. Dar preferencia a acceso libre.
- Separar resultados medidos, anuncios, estudios de proveedores, opiniones e interpretaciones estratégicas. No fabricar datos, fechas, enlaces ni noticias.
- Evitar duplicaciones; consultar ediciones anteriores y actualizar eventos solo ante cambios sustanciales. Microaprendizaje independiente, no cursos de semanas.
## Protocolo
1. Buscar fuentes variadas y casos de operación de tecnología reales.
2. Verificar exhaustivamente los finalistas; eliminar cualquier candidato no sustentado.
3. Escribir JSON de edición con `date`, `headline`, `dek`, `stories` y `learning`. Cada noticia: `category`, `title`, `summary`, `analysis`, `source_title`, `source_url`, `source_date`, `evidence_type`, `limitations`.
4. Ejecutar `python scripts/build.py --edition editions/YYYY-MM-DD.json --check` y el renderizado. El script verifica estructura, NO veracidad semántica.
5. Publicar solo tras verificación editorial humana o autorización editorial expresa y QA: salvar edición previa en `archive/YYYY-MM-DD/index.html`, preservar JSON y actualizar index.html. Ante error conservar portada anterior.
6. Confirmar URL publicada tras commit. No activar automatizaciones ni asumir permisos sin probarlos.
