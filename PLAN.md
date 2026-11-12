# PLAN.md — FillRateRetail

Plan de entregas para construir la aplicación web de análisis de Fill Rate y abastecimiento comercial (División Retail, Montecillos).
Generado por el subagente @arquitecto con base en `AGENTS.md`, `Contexto/Contexto_Mi_App.md` y el archivo real de `Insumos/`.

---

## 1. RESUMEN

Vamos a construir una aplicación web local en Python con Flask y patrón MVC que analice el cumplimiento de pedidos (Fill Rate) de los Centros de Carne. Entra un archivo Excel de insumos con reportes de Fill Rate y un histórico de ventas; la app calcula kilos solicitados, entregados, faltantes y rankings de importancia comercial. El agente de IA interpreta los indicadores calculados y devuelve recomendaciones en un contrato JSON. Sale un tablero gerencial con contadores, tablas filtradas, reportes descargables en Excel/PDF y alertas del agente, todo en español y ejecutado localmente.

---

## 2. LO QUE ENCONTRÉ

### Contexto (`Contexto/`)
- `Contexto_Mi_App.md` (669 líneas): especificación completa de FillRateRetail (qué es la app, datos de entrada, reglas R01–R33, contrato JSON del agente, qué produce, quién decide, cifras de control, casos límite, reglas del sistema, supuestos S01–S12).
- `FillRateRetail_Documento_Contexto_Actualizado.docx`: documento de origen del contexto.

### Insumos (`Insumos/`)
- Único archivo: `Fill Rate Noviembre - Diciembre 2025.xlsx` (contiene texto, no es escaneado). Tiene 7 hojas:
  - `FR NOV 2025`: 88 filas totales, 8 columnas, 86 filas de datos. Encabezados: Descri Clase, Descri Articulo, Pedido, Recibido, Diferencia, % de servicio.
  - `FR DIC 2025`: 59 filas totales, 12 columnas, 57 filas de datos. Mismos encabezados base + columnas extra.
  - `Kilos Vendidos Nov - Dic`: 18 093 filas totales, 11 columnas, 18 092 filas de datos. Encabezados: Año, MES, Centro de Carnes, Categoría, Subcategoría, Artículo, Descripción, Descripcion, Medida, Cantidad, Total. Según el usuario, estas ventas son de 2025.
  - `1-11-26`, `2-11-26`, `3-11-26`, `4-11-26`: hojas vacías o con solo texto de aviso ("LOS DOMINGOS NO TENEMOS ENTREGAS").

### ¿Coincide con AGENTS.md?
- Parcialmente. AGENTS.md ya documenta el archivo real entregado y anota las contradicciones:
  - El contexto espera 4 archivos Excel separados (`1-11-26.xlsx`, `2-11-26.xlsx`, `Ventas_Octubre_2026.xlsx`, `Ventas_Noviembre_2025.xlsx`), pero solo se entregó uno agrupado.
  - Las columnas reales del insumo son `Pedido` / `Recibido` / `Diferencia`, no `Asignado` / `Sin Asignar` / `Fill Rate` como dice la imagen del contexto.
  - Las hojas de Fill Rate no tienen columna Centro de Carne ni fecha diaria completa (usuario indicó omitir Centro de Carne por ahora).
  - Las cifras de control de AGENTS.md usan datos de prueba ficticios que no están en el insumo real.

### ¿Qué falta o no cuadra?
- No se entregaron los 4 archivos separados esperados por el contexto.
- Falta validar el mapeo definitivo de columnas reales del Excel contra los campos lógicos del contexto.
- Falta confirmar el período real cubierto por `Kilos Vendidos Nov - Dic` (muestra mostraba Año 2024; usuario dijo 2025).
- Centro de Carne y fecha de cada reporte diario no están en las hojas de Fill Rate.

---

## 3. ENTREGAS POR SUBAGENTE

Orden de ejecución. Cada entrega es pequeña y verificable en pocos minutos.

| N° | Responsable | Qué debe entregar | Archivos que crea o modifica | Qué recibe de la entrega anterior | Cómo se verifica en pantalla |
|----|-------------|-------------------|------------------------------|-----------------------------------|------------------------------|
| 1 | @arquitecto | `PLAN.md` con este plan de entregas | `PLAN.md` (raíz) | `AGENTS.md`, carpeta `contexto/`, carpeta `insumos/` | `PLAN.md` existe en la raíz del proyecto |
| 2 | @backend | Estructura MVC base con `uv`: `create_app()`, `wsgi.py`, `iniciar_app.bat`, `.env.example`, dependencias instaladas (`flask`, `python-dotenv`, `openpyxl`, `pandas`) | `app/__init__.py`, `wsgi.py`, `iniciar_app.bat`, `.env.example`, `pyproject.toml`/`uv.lock` | `PLAN.md` | Ejecutar `iniciar_app.bat`: enciende en `127.0.0.1` y abre el navegador en el tablero local |
| 3 | @backend | Lectura y validación de insumos Excel: leer hojas `FR NOV 2025` y `FR DIC 2025`, detectar columnas y contar filas de datos | `app/services/lectura_insumos.py` | Estructura MVC base (entrega 2) | En consola/pantalla se imprime: hoja, columnas, cantidad de filas de datos de `FR NOV 2025` y `FR DIC 2025` |
| 4 | @backend | Reglas R01–R04 (leer archivos, interpretar fecha día-mes-año, evitar reprocesar duplicados, no modificar originales) + R08 (contar válidos/excluidos/pendientes) | `app/services/validacion.py` | Lectura de insumos (entrega 3) | Pantalla muestra: registros válidos, excluidos y pendientes de revisión del insumo leído |
| 5 | @backend | Reglas R11–R12 (cálculo Fill Rate y kilos faltantes; prohibido dividir entre cero; faltante solo en kg) | `app/services/calculo_fill_rate.py` | Validación (entrega 4) | Pantalla muestra: Fill Rate general (%) y kilos faltantes totales del insumo cargado |
| 6 | @backend | Reglas R14, R15 (consolidado con totales, no promedio de porcentajes; agregación por producto, categoría, Centro de Carne, total División Retail) | `app/services/agregaciones.py` | Cálculo Fill Rate (entrega 5) | Tabla en pantalla: consolidado por categoría y por Centro de Carne con pedido, entrega, faltante y Fill Rate |
| 7 | @backend | Reglas R17–R19 (histórico diario de faltantes, contar fechas con faltante > 0, identificar faltantes recurrentes en 2+ fechas) | `app/services/recurrencia.py` | Agregaciones (entrega 6) | Lista en pantalla: productos con faltantes recurrentes y días con faltante |
| 8 | @backend | Reglas R22–R25 (cruce con ventas del mes anterior y mismo mes año anterior; rankings independientes por kilos y por colones; por Centro de Carne, categoría y consolidado) | `app/services/rankings.py` | Recurrencia (entrega 7) | Pantalla muestra: ranking de productos por kilos vendidos y ranking por colones, independientes |
| 9 | @backend | Integración agente de IA: leer llave de `.env`, recibir indicadores calculados, devolver JSON válido con contrato (`fecha_corte`, `resumen_ejecutivo`, `alertas`, `evidencia`, etc.), reglas obligatorias del agente | `app/services/agente_ia.py`, `app/controllers/ia_controller.py` | Rankings (entrega 8) | Endpoint o pantalla muestra un JSON válido con las llaves obligatorias del contrato |
| 10 | @backend | Descarga de resultados: generar reporte Excel y PDF localmente con datos consolidados, cálculos, faltantes, rankings e indicadores históricos | `app/services/exportacion.py` | Agente IA (entrega 9) | Botón "Descargar Excel" y "Descargar PDF" genera archivo local sin error |
| 11 | @frontend | Pantalla de inicio / tablero gerencial: contadores grandes y tablas con filtro, completamente en español | `app/templates/inicio.html`, `app/static/styles.css` (en `base.html`) | Estructura MVC base (entrega 2) | Se carga la URL local y se ve el tablero con contadores destacados en español |
| 12 | @frontend | Pantalla de resultados con contadores, tabla con filtro y detalle por registro | `app/templates/resultados.html` | Pantalla de inicio (entrega 11) | Al seleccionar un registro se ve su detalle y la tabla permite filtrar |
| 13 | @frontend | Estilo de la app: CSS dentro de `base.html`, pantallas profesionales, sin librerías JS externas, formato ₡ y kg, consistente | `app/templates/base.html`, `app/static/styles.css` | Pantalla de resultados (entrega 12) | App completa con estilo consistente, legible en pantalla de oficina, sin librerías JS externas |
| 14 | @tester | Pruebas en `tests/` con `pytest` contra las cifras de control y casos límite de `AGENTS.md`; `pythonpath` configurado | `tests/test_fill_rate.py`, `tests/test_casos_limite.py`, `pytest.ini`/`conftest.py` | Backend completo (entregas 2–10) | Ejecutar `pytest`: todas las pruebas pasan y comparan con cifras control (77,20 %; 85,33 %; 81,64 %) |
| 15 | @tester | `VALIDACION.md` con esperado vs obtenido para cada cifra de control y cada caso límite | `VALIDACION.md` (raíz) | Pruebas (entrega 14) | Documento muestra tabla esperado vs obtenido sin diferencias reportadas |
| 16 | @revisor | Revisión de seguridad (llaves en código, datos sensibles, `.gitignore`) y de que todo esté especificado en `AGENTS.md`; entrega lista de hallazgos con prioridad y corrección propuesta | Ningún archivo (solo lectura y reporte) | Todo el proyecto (entregas 1–15) | Pantalla/consola muestra lista de hallazgos con prioridad (alta/media/baja) y corrección propuesta |

---

## 4. PUNTOS DE CONTROL

Después de cada entrega indicada, interviene @tester y usted debe verificar en pantalla el resultado exacto:

| Después de entrega | @tester valida | Qué debe ver usted en pantalla |
|--------------------|----------------|--------------------------------|
| 2 (estructura MVC) | Que la app encienda sin errores | Navegador abierto en `http://127.0.0.1:5000` (o puerto local) mostrando el tablero vacío o de bienvenida |
| 3 (lectura insumos) | Que se lean las columnas y filas del Excel | Consola imprime: `FR NOV 2025: 86 filas de datos, columnas: Descri Clase, Descri Articulo, Pedido, Recibido, Diferencia, % de servicio` |
| 5 (cálculo Fill Rate) | R11, R12 | Pantalla muestra: `Fill Rate general: 77,20 %` (si usa datos de prueba del contexto) o el porcentaje real del insumo cargado; `Kilos faltantes totales: 57 kg` (datos de prueba) o valor real |
| 6 (consolidado) | R14, R15 | Tabla muestra: Total pedido 550 kg, Total entregado 449 kg, Total faltante 101 kg, Fill Rate consolidado 81,64 % (datos de prueba del contexto) |
| 7 (recurrencia) | R17–R19 | Lista muestra productos con faltantes recurrentes (ej. R001 del CC A con 2 días con faltante) |
| 8 (rankings) | R22–R25 | Pantalla muestra dos rankings independientes: uno por kilos vendidos y otro por colones, con el producto #1 de cada Centro de Carne |
| 9 (agente IA) | Contrato JSON | Pantalla/endpoint devuelve JSON válido con `fecha_corte`, `resumen_ejecutivo`, `alertas`, `evidencia` (con `kilos_faltantes`, `fill_rate_pct`, etc.) |
| 14 (pruebas pytest) | Cifras de control y casos límite | `pytest` finaliza con `X passed` y ninguna prueba falla; salida compara obtenido vs esperado |
| 15 (VALIDACION.md) | Esperado vs obtenido | `VALIDACION.md` muestra tabla donde obtenido = esperado para cada cifra de control |

---

## 5. RIESGOS

| Riesgo | Qué hará @backend | Qué hará @frontend | Qué hará @tester | Qué hará @revisor |
|--------|-------------------|--------------------|------------------|-------------------|
| Datos incompletos o columnas faltantes en el Excel | Registrar error (R05), excluir solo registros inválidos (R07), mostrar afectados (R08) | Mostrar mensaje claro en pantalla sin inventar valores | Verificar que los registros excluidos aparezcan en reporte de incidencias | Confirmar que no se inventaron columnas ni valores fuera de AGENTS.md |
| Archivo escaneado o basado en imágenes | Señalar que requiere revisión; no inventar datos (caso límite) | Mostrar aviso en pantalla de archivo no procesable | Incluir prueba de caso límite para archivo basado en imágenes | Verificar que no haya OCR ni invento de datos |
| Respuesta del agente IA que no es JSON válido | Capturar excepción, devolver error controlado, mantener cálculos disponibles | Mostrar mensaje: "Recomendaciones de IA no disponibles" | Probar con respuesta malformada del agente y verificar que la app no se rompa | Verificar que no se expongan claves ni secretos en el manejo de errores |
| Llave gratis del modelo local limitada o no disponible | Leer llave de `.env`; si no hay, seguir mostrando cálculos y avisar que IA no está disponible | Mostrar aviso: "Recomendaciones de IA no disponibles" | Verificar que los cálculos determinísticos sigan funcionando sin IA | Verificar que la llave no esté escrita en el código fuente |
| Archivos esperados del contexto no entregados | Preguntar al usuario antes de asumir columnas o archivos | No inventar campos de entrada | Reportar diferencia entre cifras de control (datos ficticios) y datos reales del insumo | Listar como hallazgo prioridad alta: faltan archivos de entrada del contexto |

---

## 6. PREGUNTAS PARA MÍ

Antes de empezar la construcción, necesito que confirme:

1. **¿Uso el único Excel entregado (`Fill Rate Noviembre - Diciembre 2025.xlsx`) y sus hojas (`FR NOV 2025`, `FR DIC 2025`, `Kilos Vendidos Nov - Dic`) como fuentes de entrada, o espera primero los 4 archivos separados del contexto?**
2. **¿Qué columnas reales del insumo mapeo a "Kilos solicitados" y "Kilos entregados"?** (¿`Pedido`→solicitado y `Recibido`→entregado, o hay otra correspondencia?)
3. **¿Omitimos Centro de Carne por ahora como indicó, o desea que lo busque en alguna hoja del insumo?**
4. **¿Qué período cubre exactamente `Kilos Vendidos Nov - Dic`?** (¿2025 noviembre/diciembre, o incluye 2024 como mostraba la muestra?)
5. **¿Las pruebas de aceptación deben usar las cifras de control del contexto (datos ficticios: 250/193/57 kg, etc.) o datos reales del insumo entregado?**
6. **¿Quiero que el entregable 2 ya incluya `.gitignore` con `.env`, `uv.lock`, `__pycache__`, `instance/`, `*.db`, etc.?**

Quedo a la espera de su aprobación de este `PLAN.md` antes de que comience cualquier subagente.
