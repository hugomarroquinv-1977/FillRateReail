# AGENTS.md — FillRateRetail

Proyecto: análisis de Fill Rate y abastecimiento comercial (División Retail, Montecillos).
Estado: especificación basada en `Contexto/FillRateRetail_Documento_Contexto_Actualizado.docx` (extraído a `Contexto/Contexto_Mi_App.md`) y en el archivo real de `Insumos/`.
Generado por OpenCode bajo instrucción del usuario. No inventar columnas, archivos, fórmulas ni valores que no estén en el contexto o en los insumos.

---

## Qué es esta app

FillRateRetail es una aplicación web de uso local que automatiza el análisis diario de cumplimiento de pedidos (Fill Rate) de los Centros de Carne de Montecillos.

Propósito: identificar los faltantes de productos, detectar problemas recurrentes de abastecimiento y determinar cuáles artículos requieren atención prioritaria para proteger las ventas.

La aplicación integrará un agente de inteligencia artificial que interpretará los resultados de los análisis y generará conclusiones y recomendaciones comerciales.

Problema que resuelve: actualmente se genera un reporte diario de Fill Rate, pero su presentación no facilita un análisis profundo de productos con faltantes recurrentes, cantidades no entregadas en kilogramos, cumplimiento por categoría y Centro de Carne, tendencias históricas de abastecimiento, productos de mayor importancia comercial, riesgos de futuros faltantes y prioridades de abastecimiento según ventas históricas en kilos y colones.

Objetivo principal: proteger las ventas mediante la identificación temprana de faltantes y la priorización del abastecimiento de productos comercialmente relevantes.

Alcance de la primera versión: aplicación de consulta, análisis y recomendaciones. No realizará pedidos automáticamente, no modificará los pedidos originales y no ejecutará decisiones de abastecimiento sin intervención humana.

---

## Datos de entrada

### Archivo real entregado en `Insumos/`

**`Fill Rate Noviembre - Diciembre 2025.xlsx`** (único archivo de insumos; contiene texto, no es un PDF escaneado). Tiene 7 hojas:

| Hoja | Filas totales | Columnas | Filas de datos | Encabezados / contenido observado |
|------|---------------|----------|----------------|-----------------------------------|
| FR NOV 2025 | 88 | 8 | 86 | Fila 1 vacía. Fila 2: Descri Clase, Descri Articulo, Pedido, Recibido, Diferencia, % de servicio (columnas A y H vacías). Datos de la fila 3 a la 88. |
| FR DIC 2025 | 59 | 12 | 57 | Fila 1 vacía. Fila 2: Descri Clase, Descri Articulo, Pedido, Recibido, Diferencia, % de servicio, más columnas adicionales con valores de ejemplo (RES, CERDO, etc.). Datos de la fila 3 a la 59. |
| Kilos Vendidos Nov - Dic | 18093 | 11 | 18092 | Fila 1: Año, MES, Centro de Carnes, Categoría, Subcategoría, Artículo, Descripción, Descripcion, Medida, Cantidad, Total. Datos de la fila 2 a la 18093. Según el usuario, estas ventas son del año 2025 (noviembre/diciembre). |
| 1-11-26 | 3 | 2 | 0 | Solo contiene el aviso "LOS DOMINGOS NO TENEMOS ENTREGAS" (celda B3). Sin datos de Fill Rate. |
| 2-11-26 | 1 | 1 | 0 | Vacía. |
| 3-11-26 | 1 | 1 | 0 | Vacía. |
| 4-11-26 | 1 | 1 | 0 | Vacía. |

### Archivos mencionados en el contexto pero NO entregados en `Insumos/`

El contexto (sección 3.1) requiere como archivos de entrada:

| Archivo esperado | Formato | Contenido según contexto | ¿Está en insumos? |
|------------------|---------|--------------------------|-------------------|
| 1-11-26.xlsx | Excel .xlsx | Reporte real de Fill Rate (formato visual) | No (solo existe una hoja vacía llamada "1-11-26" dentro del único Excel) |
| 2-11-26.xlsx | Excel .xlsx | Nuevo reporte del día | No (solo existe una hoja vacía llamada "2-11-26") |
| Ventas_Octubre_2026.xlsx | Excel .xlsx | Kilos vendidos y ventas en colones | No |
| Ventas_Noviembre_2025.xlsx | Excel .xlsx | Histórico comparable para estacionalidad | No |

**Pendiente:** los 4 archivos esperados por el contexto no se entregaron por separado; el único insumo real es el Excel agrupado anterior. El AGENTS.md asume que se usan las hojas `FR NOV 2025` / `FR DIC 2025` como reporte de Fill Rate y `Kilos Vendidos Nov - Dic` como histórico de ventas, según indicación del usuario.

### Campos de Fill Rate (contexto, imagen de referencia)

El contexto indica que se deben usar las columnas que muestra la imagen de referencia del reporte de Fill Rate:

| Col. | Nombre exacto (imagen) | Interpretación según contexto |
|------|------------------------|-------------------------------|
| A | Mes | Mes del reporte; año y fecha exacta pendientes de confirmar. |
| B | Categoría | Nombre o código de categoría; los ejemplos muestran errores #¡REF!. |
| C | Artículo | Identificador o descripción del artículo; captura con errores #¡REF!. |
| D | Pedido | Cantidad solicitada; unidad exacta y origen pendientes de confirmar. |
| E | Asignado | Cantidad asignada; confirmar equivalencia con entregado físicamente. |
| F | Sin Asignar | Cantidad sin asignación; comprobar si corresponde a faltantes en kg. |
| G | Fill Rate | Porcentaje observado como encabezado; debe recalcularse con datos válidos. |
| H | % Faltante | Columna existente en origen, pero NO se presentará como indicador en los reportes. |
| I | Origen | Referencia o procedencia del registro; ejemplo visible: Faltantes noviembre 2025. |

### Campos reales del insumo entregado (FR NOV 2025 / FR DIC 2025)

| Columna real | Observación |
|--------------|-------------|
| Descri Clase | Agrupación (ej. RES, CERDO, FORMADOS, PRODUCTOS PREPARADOS). |
| Descri Articulo | Código + descripción (ej. "10184 - RIB EYE STEAK"). |
| Pedido | Cantidad solicitada. |
| Recibido | Cantidad recibida. |
| Diferencia | Pedido − Recibido. |
| % de servicio | Porcentaje de servicio. |

**Contradicción anotada:** el Excel real tiene columnas `Pedido` / `Recibido` / `Diferencia`, mientras el contexto (imagen) menciona `Pedido` / `Asignado` / `Sin Asignar` / `Fill Rate` / `% Faltante`. Según indicación del usuario, se usa el mapeo de la imagen (Pedido, Asignado, Sin Asignar). Falta validar contra el Excel definitivo qué columna real corresponde a cada campo lógico.

### Campos lógicos que necesita el sistema (contexto, sección 3.3)

Estos son los datos que necesita el sistema; NO se confirma que existan columnas de igual nombre en el Excel real:

| Campo lógico | Tipo | Uso |
|--------------|------|-----|
| Fecha | Fecha | Identificar el día |
| Centro de Carne | Texto o código | Identificar establecimiento | **Omitido por ahora** (usuario indicó: "olvida por ahora lo relacionado a centro de carne") |
| Categoría | Texto o código | Agrupar productos |
| Subcategoría | Texto o código | Análisis detallado, si existe |
| Código de artículo | Texto | Identificar inequívocamente el producto |
| Descripción | Texto | Mostrar el nombre comercial |
| Unidad de medida | Texto | Diferenciar kilos de otras unidades |
| Kilos solicitados | Decimal | Cantidad pedida |
| Kilos entregados | Decimal | Cantidad recibida |
| Kilos faltantes | Decimal calculado | Diferencia entre pedido y entrega |
| Ventas históricas en kilos | Decimal | Importancia comercial en volumen |
| Ventas históricas en colones | Decimal | Importancia comercial monetaria |
| Período histórico | Mes/año | Identificar la referencia de ventas |

Observación crítica del contexto: la captura no incluye una columna visible de Centro de Carne ni una fecha diaria completa. Es obligatorio localizar esos datos en el Excel definitivo antes del cruce por punto de venta. Por ahora, Centro de Carne queda fuera del alcance inmediato.

### Tratamiento del período histórico (contexto, sección 3.4)

Para analizar noviembre de 2026:
- Fill Rate: archivos diarios de noviembre de 2026.
- Ventas recientes: octubre de 2026.
- Ventas estacionales: noviembre de 2025.
- Ambos históricos deben conservarse identificados por período y no sumarse sin una regla expresamente aprobada.

### Organización de archivos (contexto, sección 3.2)

SUPUESTO: estructura de carpetas locales configurable desde la aplicación.
```
FillRateRetail/
├── datos/
│   ├── fill_rate/
│   │   ├── 1-11-26.xlsx
│   │   ├── 2-11-26.xlsx
│   │   └── 3-11-26.xlsx
│   └── ventas_historicas/
│       ├── Ventas_Octubre_2026.xlsx
│       └── Ventas_Noviembre_2025.xlsx
├── reportes/
├── base_datos/
├── logs/
├── .env
└── iniciar_app.bat
```
Las rutas serán configurables. No deben depender de nombres fijos de usuarios ni de rutas específicas de Windows.

### Interpretación de nombres de archivo (regla R02)

Interpretar nombres como `1-11-26.xlsx` con formato día-mes-año; el ejemplo representa 1 de noviembre de 2026.

---

## Reglas de negocio (código, sin IA)

Las reglas siguientes se implementan mediante código Python. No dependen de interpretaciones del agente de IA.

### 4.1 Lectura y validación

| Regla | Descripción verificable |
|-------|-------------------------|
| R01 | Leer los archivos Excel desde una carpeta local configurada. |
| R02 | Interpretar nombres como 1-11-26.xlsx con formato día-mes-año; el ejemplo representa 1 de noviembre de 2026. |
| R03 | Identificar nuevos archivos al actualizar el análisis y evitar procesar nuevamente el mismo contenido como si fuera un día nuevo. |
| R04 | No modificar los Excel originales. |
| R05 | Registrar los errores de lectura e informar el archivo y los registros afectados. |
| R06 | No inventar valores cuando existan campos incompletos. |
| R07 | Excluir de un cálculo únicamente los registros que no puedan validarse para ese cálculo. |
| R08 | Mostrar la cantidad de registros válidos, excluidos y pendientes de revisión. |
| R09 | Procesar cantidades en kilos; no sumar unidades de medida diferentes sin una conversión expresamente definida. |
| R10 | Identificar los productos mediante Centro de Carne y código de artículo, usando los campos adicionales necesarios para evitar cruces incorrectos. |

### 4.2 Cálculo del Fill Rate

**R11. Cálculo del cumplimiento**
```
Fill Rate (%) = (Kilos entregados / Kilos solicitados) × 100
```
La fórmula se aplica únicamente cuando los kilos solicitados son mayores que cero y los datos son válidos.

**R12. Cálculo de faltantes**
```
Kilos faltantes = Kilos solicitados − Kilos entregados
```
El faltante se mostrará exclusivamente en kilos.

**R13. Formato de indicadores**
- Fill Rate: porcentaje.
- Faltantes: kilogramos.
- Ventas históricas: colones y kilogramos, por separado.
- Está prohibido presentar porcentajes de faltantes como indicador de negocio.

**R14. Fill Rate consolidado**
El cumplimiento general debe calcularse usando los totales de kilos solicitados y entregados. No se permitirá promediar directamente los porcentajes individuales de los productos o establecimientos.

**R15. Niveles de agregación**
Calcular Fill Rate y kilos faltantes para:
- Producto.
- Categoría.
- Centro de Carne.
- Categoría dentro de cada Centro de Carne.
- Total de la División Retail.

**R16. Casos matemáticos inválidos**
Los pedidos con cantidad cero no generarán un porcentaje de cumplimiento calculado por división entre cero. Si los kilos entregados exceden los solicitados, el registro deberá marcarse para revisión y no ajustarse silenciosamente.

### 4.3 Análisis histórico

| Regla | Descripción verificable |
|-------|-------------------------|
| R17 | Consolidar el histórico diario de faltantes por Centro de Carne, categoría y artículo. |
| R18 | Contar la cantidad de fechas diferentes en las que un mismo producto registra kilos faltantes mayores que cero. |
| R19 | Identificar faltantes recurrentes cuando un producto tenga faltantes en dos o más fechas distintas. |
| R20 | Identificar faltantes en días consecutivos. Si falta el archivo de una fecha intermedia, no se debe asumir que existió o no un faltante ese día. |
| R21 | Permitir la consulta de resultados por día, rango de fechas, Centro de Carne, categoría y artículo. |

### 4.4 Importancia comercial

| Regla | Descripción verificable |
|-------|-------------------------|
| R22 | Cruzar los productos con el archivo de ventas del mes anterior. |
| R23 | Cruzar los productos con las ventas del mismo mes del año anterior. |
| R24 | Generar rankings independientes por kilos vendidos y por ventas en colones. |
| R25 | Generar los rankings por Centro de Carne, por categoría y a nivel consolidado. |
| R26 | Mantener separados los indicadores históricos de ambos períodos, sin asignar ponderaciones no aprobadas. |
| R27 | Si un producto no aparece en el histórico de ventas, mostrarlo como dato no disponible. No interpretarlo automáticamente como cero ventas. |
| R28 | No convertir las ventas históricas en una supuesta pérdida económica real sin una metodología de cálculo previamente aprobada. |

### 4.5 Generación de resultados

| Regla | Descripción verificable |
|-------|-------------------------|
| R29 | Ordenar los rankings de mayor a menor según la métrica seleccionada. |
| R30 | Permitir exportar los datos y resultados en Excel y PDF. |
| R31 | Mantener identificable la fuente de cada cálculo. |
| R32 | Ningún resultado generado por IA podrá modificar los cálculos matemáticos originales. |
| R33 | No emitir pedidos, modificar inventarios ni ejecutar abastecimiento automáticamente. |

---

## Lo que hace el agente de IA

### 5.1 Rol del agente

Analista inteligente de abastecimiento y protección de ventas Retail. Su responsabilidad será convertir los indicadores calculados por el sistema en información útil para la toma de decisiones comerciales y operativas.

### 5.2 Información que recibe

Recibirá datos previamente validados y calculados:
- Cumplimiento de Fill Rate.
- Faltantes diarios y acumulados en kilos.
- Frecuencia de faltantes por producto.
- Comportamiento histórico por Centro de Carne.
- Rankings de ventas en kilos.
- Rankings de ventas en colones.
- Ventas del mes anterior.
- Ventas del mismo mes del año anterior.
- Incidencias de calidad de datos.

El agente no deberá procesar directamente archivos desconocidos sin pasar primero por el módulo de validación.

### 5.3 Funciones de inteligencia artificial

- **A. Identificación de faltantes críticos:** Señalar productos con faltantes recurrentes que, además, tienen importancia comercial según sus históricos de venta.
- **B. Identificación de riesgos:** Detectar patrones de faltantes diarios y señalar productos que podrían presentar nuevos problemas de abastecimiento. El riesgo debe presentarse como una estimación, no como un hecho confirmado.
- **C. Protección de ventas:** Recomendar los productos que deben recibir atención prioritaria para evitar afectaciones comerciales.
- **D. Recomendaciones por Centro de Carne:** Generar conclusiones específicas para cada establecimiento, considerando su propio comportamiento de venta.
- **E. Resumen gerencial:** Redactar un resumen de los principales hallazgos, riesgos, oportunidades y prioridades.

### 5.4 Contrato JSON de salida

El agente deberá devolver un JSON válido con la siguiente estructura:

| Llave JSON | Tipo | Descripción |
|------------|------|-------------|
| fecha_corte | string | Fecha del análisis, formato AAAA-MM-DD |
| resumen_ejecutivo | string | Síntesis gerencial |
| alertas | array | Productos o situaciones que requieren atención |
| alertas[].centro_carne | string | Establecimiento afectado |
| alertas[].categoria | string | Categoría del producto |
| alertas[].codigo_articulo | string | Código identificador |
| alertas[].producto | string | Descripción comercial |
| alertas[].tipo | string | Faltante confirmado o riesgo estimado |
| alertas[].prioridad | string | Evaluación cualitativa fundamentada |
| alertas[].evidencia | object | Indicadores que fundamentan la alerta |
| alertas[].recomendacion | string | Acción sugerida |
| productos_indispensables | array | Productos destacados por su importancia comercial |
| riesgos_detectados | array | Posibles problemas de abastecimiento |
| limitaciones | array | Información insuficiente o no disponible |
| fuentes | array | Identificadores de archivos y períodos utilizados |

#### Estructura obligatoria de la evidencia

Cada alerta deberá incluir los siguientes datos dentro de `evidencia`:

| Llave | Tipo | Contenido |
|-------|------|-----------|
| kilos_faltantes | number o string | Kilos no entregados |
| dias_con_faltante | integer o string | Número de fechas con faltantes |
| fill_rate_pct | number o string | Porcentaje de cumplimiento |
| ventas_historicas_kg | number o string | Volumen vendido de referencia |
| ventas_historicas_crc | number o string | Valor vendido de referencia |
| periodo_referencia | string | Período de las ventas históricas |

#### Reglas obligatorias del agente

1. Nunca inventar datos, productos, fechas, cifras ni causas de faltantes.
2. Si un campo no aparece o no puede determinarse, utilizar exactamente `"no indicado"`.
3. Los datos numéricos válidos deben devolverse como números, sin símbolos monetarios ni unidades en el valor.
4. No modificar cifras previamente calculadas por Python.
5. Distinguir explícitamente los hechos confirmados de las estimaciones.
6. No afirmar que existe un problema de producción, inventario o logística si los datos únicamente demuestran un faltante de abastecimiento.
7. Justificar las recomendaciones mediante datos concretos.
8. No recomendar cantidades específicas de reposición sin contar con una regla aprobada para calcularlas.
9. Devolver listas vacías cuando no existan alertas sustentadas.
10. Si el modelo local no está disponible, el sistema debe seguir mostrando los cálculos y señalar que las recomendaciones de IA no están disponibles.

### 5.5 Criterios de interpretación

| Criterio | Definición |
|----------|------------|
| Alta importancia en kilos | Producto situado en los primeros lugares del ranking de volumen histórico. |
| Alta importancia en colones | Producto situado en los primeros lugares del ranking de ventas monetarias. |
| Recurrencia | Faltantes registrados en diferentes fechas. |
| Riesgo | Patrón detectado que justifica seguimiento, sin garantizar que se producirá un nuevo faltante. |

Pendiente de confirmar: umbrales cuantitativos de semáforos y cantidad de posiciones prioritarias. Hasta aprobar estos parámetros, los rankings numéricos deben permanecer separados y transparentes.

---

## Qué produce la app

### 6.1 Pantalla principal: tablero gerencial

| Indicador | Presentación |
|-----------|--------------|
| Fill Rate general | Porcentaje destacado |
| Fill Rate por categoría | Tabla y gráfico |
| Fill Rate por Centro de Carne | Tabla comparativa |
| Kilos faltantes totales | Valor numérico |
| Productos con faltantes recurrentes | Ranking |
| Centros de Carne afectados | Ranking |
| Productos prioritarios en kilos | Ranking independiente |
| Productos prioritarios en colones | Ranking independiente |
| Evolución diaria | Gráficos de tendencia |
| Alertas del agente de IA | Panel de recomendaciones |

### 6.2 Pantalla de análisis por Centro de Carne

El usuario seleccionará un establecimiento y visualizará:
- Fill Rate general del Centro de Carne.
- Fill Rate por categoría.
- Productos con faltantes.
- Kilos faltantes acumulados.
- Frecuencia de incumplimientos.
- Rankings de importancia comercial.
- Productos que necesitan prioridad de abastecimiento.
- Recomendaciones específicas de IA.

### 6.3 Pantalla de análisis por categoría

Permitirá visualizar categorías y productos con sus respectivos indicadores de cumplimiento, faltantes e importancia comercial.

### 6.4 Pantalla histórica

Mostrará tendencias por día y período, faltantes recurrentes y evolución del cumplimiento.

### 6.5 Pantalla de administración de archivos

- Configurar las carpetas locales.
- Consultar los archivos encontrados.
- Revisar las fechas procesadas.
- Identificar archivos con errores.
- Actualizar el análisis manualmente.
- Consultar el registro de importaciones.

### 6.6 Semáforos

Se reservará un componente visual para indicar niveles de atención del Fill Rate y del abastecimiento.

**SUPUESTO PENDIENTE:** No existen porcentajes límite aprobados para asignar colores rojo, amarillo y verde. No deben inventarse ni activarse como clasificación automática hasta definirlos.

### 6.7 Botones principales

- Actualizar análisis.
- Seleccionar Centro de Carne.
- Filtrar categoría.
- Seleccionar período.
- Ver histórico.
- Ver recomendaciones de IA.
- Descargar Excel.
- Descargar PDF.
- Revisar errores de carga.

### 6.8 Reportes descargables

- Reporte Excel: incluirá datos consolidados, cálculos de Fill Rate, faltantes en kilos, rankings e indicadores históricos.
- Reporte PDF: presentará un resumen gerencial, principales indicadores, productos críticos y recomendaciones.
- Ambos se generarán localmente.

---

## Quién decide

### 7.1 Roles operativos

| Usuario | Responsabilidad |
|---------|-----------------|
| Asistente de pedidos | Mantener disponibles los archivos diarios y revisar los resultados |
| Supervisores | Consultar resultados por Centro de Carne e identificar incidencias |
| Gerente de División Retail | Evaluar los indicadores consolidados y las prioridades comerciales |
| Agente de IA | Generar análisis y recomendaciones sin tomar decisiones autónomas |

### 7.2 Decisión final

La inteligencia artificial únicamente recomienda. Las decisiones relacionadas con cambios de abastecimiento, prioridades de pedidos, escalamiento de incidencias o intervenciones operativas deben permanecer bajo responsabilidad humana.

**SUPUESTO:** El Gerente de División Retail establecerá prioridades generales y los supervisores coordinarán el seguimiento correspondiente. La autoridad exacta para modificar pedidos está pendiente de confirmar.

### 7.3 Permisos de usuario

**SUPUESTO:** La primera versión utilizará roles de consulta y administración local. La necesidad de autenticación por usuario y contraseña debe confirmarse antes de implementar un sistema completo de permisos.

---

## Cifras de control

Las siguientes valores son resultados esperados obligatorios para las pruebas de aceptación del contexto (sección 9). Se basan en datos de prueba ficticios (`1-11-26.xlsx`, `2-11-26.xlsx`, `Ventas_Octubre_2026.xlsx`) que **no están entre los insumos reales entregados**, por lo que no pueden validarse contra el archivo actual de insumos hasta que se disponga de esos archivos de prueba.

### 9.1 Primer día: 1 de noviembre de 2026

| Indicador | Resultado esperado |
|-----------|-------------------|
| Kilos solicitados | 250 |
| Kilos entregados | 193 |
| Kilos faltantes | 57 |
| Fill Rate general | 77,20 % |

**Cumplimiento por categoría**

| Categoría | Pedido kg | Entrega kg | Faltante kg | Fill Rate |
|-----------|-----------|------------|-------------|-----------|
| Res | 140 | 95 | 45 | 67,86 % |
| Cerdo | 110 | 98 | 12 | 89,09 % |
| Total | 250 | 193 | 57 | 77,20 % |

### 9.2 Segundo día: 2 de noviembre de 2026

| Indicador | Resultado esperado |
|-----------|-------------------|
| Kilos solicitados | 300 |
| Kilos entregados | 256 |
| Kilos faltantes | 44 |
| Fill Rate general | 85,33 % |

### 9.3 Consolidado de ambos días

| Indicador | Resultado esperado |
|-----------|-------------------|
| Kilos solicitados | 550 |
| Kilos entregados | 449 |
| Kilos faltantes | 101 |
| Fill Rate consolidado | 81,64 % |

(449 / 550) × 100 = 81,63636… % → 81,64 %. Está prohibido sustituir este cálculo por un promedio simple de los porcentajes diarios.

### 9.4 Consolidado por categoría

| Categoría | Pedido kg | Entrega kg | Faltante kg | Fill Rate |
|-----------|-----------|------------|-------------|-----------|
| Res | 290 | 215 | 75 | 74,14 % |
| Cerdo | 260 | 234 | 26 | 90,00 % |
| Total | 550 | 449 | 101 | 81,64 % |

### 9.5 Consolidado por Centro de Carne

| Centro | Pedido kg | Entrega kg | Faltante kg | Fill Rate |
|--------|-----------|------------|-------------|-----------|
| CC A | 350 | 295 | 55 | 84,29 % |
| CC B | 200 | 154 | 46 | 77,00 % |
| Total | 550 | 449 | 101 | 81,64 % |

### 9.6 Control de recurrencia

| Centro | Artículo | Faltante total kg | Días con faltante |
|--------|----------|-------------------|-------------------|
| CC A | R001 | 55 | 2 |
| CC B | R001 | 20 | 1 |
| CC B | C001 | 26 | 2 |

El sistema deberá identificar a R001 del CC A y C001 del CC B como productos con faltantes recurrentes. R001 del CC B tiene un faltante comprobado, pero no recurrente en este conjunto de prueba.

### 9.7 Control de rankings comerciales

Utilizando octubre de 2026:
- CC A — Mayor volumen vendido: R001, con 900 kg.
- CC A — Mayor venta en colones: R001, con ₡4.500.000.
- CC B — Mayor volumen vendido: C001, con 700 kg.
- CC B — Mayor venta en colones: C001, con ₡2.100.000.

En ambos Centros de Carne, estos artículos deben aparecer en primer lugar en sus respectivos rankings.

### 9.8 Validación de calidad

El desarrollo será aceptable cuando:
- Todos los cálculos coincidan con las cifras de control.
- La carga repetida de un archivo no duplique los resultados.
- Los registros inválidos sean identificados.
- Los rankings respeten la métrica y el período seleccionados.
- Las recomendaciones del agente estén fundamentadas en la evidencia disponible.
- El sistema funcione localmente sin transmitir datos comerciales.
- Los reportes descargados coincidan con los datos del tablero.

---

## Casos límite

| Caso | Comportamiento obligatorio |
|------|----------------------------|
| Archivo vacío | Informar que no contiene registros procesables |
| Archivo corrupto | Mostrar error y conservar los datos previamente válidos |
| Archivo escaneado o basado en imágenes | Señalar que requiere revisión; no inventar datos |
| Archivo con columnas faltantes | Identificar las columnas y registros afectados |
| Fecha ausente o inválida | No asignar una fecha inventada |
| Duplicado exacto | No contabilizar dos veces |
| Dos archivos distintos para la misma fecha | Detectar conflicto y solicitar validación |
| Producto sin histórico de ventas | Mantener su faltante y señalar que no existe referencia comercial |
| Pedido de cero kilos | No calcular Fill Rate por división entre cero |
| Entrega superior al pedido | Marcar inconsistencia para revisión |
| Cantidad en unidades en lugar de kilos | No mezclar con los indicadores en kilogramos |
| Descripción distinta con mismo código | Señalar la discrepancia para revisión |
| Día sin archivo | Mostrar ausencia de información, sin asumir cumplimiento |
| Pestañas múltiples | Procesar según un mapeo de hojas previamente validado |
| Archivo en otro idioma | Requerir correspondencia validada de encabezados |
| Archivo protegido con contraseña | Informar que no puede procesarse sin acceso autorizado |
| Modelo de IA no disponible | Mantener disponibles los cálculos y reportes determinísticos |
| Histórico de ventas incompleto | No inventar ventas ni estimar importes faltantes |

**Regla general:** no transformar la ausencia de información en un cero que distorsione los indicadores. Los registros excluidos deberán ser visibles en un reporte de incidencias.

---

## Reglas del sistema

### 11.1 Tecnologías obligatorias

| Componente | Tecnología |
|------------|------------|
| Lenguaje principal | Python |
| Framework web | Flask |
| Arquitectura | MVC |
| Gestión de dependencias | uv |
| Interfaz | HTML, CSS y JavaScript |
| Plantillas web | Jinja2 |
| Procesamiento de Excel | pandas y openpyxl |
| Base de datos local | SQLite (SUPUESTO técnico) |
| Generación de Excel | openpyxl |
| Generación de PDF | Librería Python de ejecución local |
| Inteligencia artificial | Modelo ejecutado localmente |
| Configuración sensible | Archivo .env |
| Inicio de la aplicación | iniciar_app.bat |

Las tecnologías adicionales deberán justificarse por necesidades presentes en este documento.

### 11.2 Arquitectura MVC

**Modelo:** responsable de almacenar y consultar registros de pedidos, entregas, faltantes, históricos de ventas, archivos procesados y resultados calculados.

**Vista:** responsable de presentar el tablero, tablas, filtros, gráficos, alertas y recomendaciones en español.

**Controlador:** responsable de recibir las solicitudes del usuario, coordinar importaciones, ejecutar cálculos, consultar el agente y preparar las respuestas.

Servicios especializados separados:
- Importación y validación de Excel.
- Cálculo de Fill Rate.
- Análisis de recurrencia.
- Cruce con históricos de ventas.
- Construcción de rankings.
- Integración con el agente local.
- Exportación de informes.

La lógica de cálculo no deberá quedar mezclada con las plantillas visuales ni con las instrucciones de IA.

### 11.3 Arquitectura de inteligencia artificial

El sistema deberá utilizar un modelo local compatible con el computador donde se instalará la aplicación.

**SUPUESTO técnico:** evaluar Ollama o llama.cpp como motor local, sujeto a las características del equipo disponible.

El agente no deberá utilizar servicios externos de inferencia. Los datos comerciales no podrán enviarse a:
- APIs de inteligencia artificial en la nube.
- Servicios externos de análisis.
- Plataformas de telemetría.
- Servidores de terceros.

El modelo y sus dependencias deberán estar disponibles localmente para que el sistema opere sin conexión a Internet. No se permitirán descargas automáticas de modelos o actualizaciones durante el funcionamiento normal.

### 11.4 Seguridad

- El acceso web se limitará al equipo local, utilizando la dirección 127.0.0.1, salvo una autorización expresa posterior.
- Los archivos originales, las bases de datos, los resultados, los registros técnicos y los informes deberán mantenerse en el computador autorizado.
- La aplicación deberá:
  - Evitar conexiones externas innecesarias.
  - Restringir accesos a carpetas fuera de la configuración.
  - No incluir datos comerciales completos en registros técnicos.
  - No exponer secretos en pantallas o mensajes de error.
  - Validar nombres y tipos de archivos antes de procesarlos.
  - Manejar los errores sin revelar credenciales.

### 11.5 Archivo .env

Toda llave o credencial de acceso del agente deberá configurarse en `.env` y nunca dentro del código fuente. En una instalación local sin autenticación del motor de IA, la variable de llave podrá permanecer vacía. El archivo `.env` no debe subirse al repositorio ni incluirse en entregables públicos.

### 11.6 Inicio de la aplicación

Crear obligatoriamente `iniciar_app.bat`. Al ejecutarlo, deberá iniciar la aplicación local, utilizando el entorno gestionado por `uv`.

**SUPUESTO:** el archivo también abrirá automáticamente el navegador predeterminado en la dirección local del tablero. El usuario no deberá necesitar conocimientos de programación para iniciar el sistema.

### 11.7 Requisitos visuales

- Completamente en español.
- Sencillas e intuitivas.
- Legibles en una computadora de oficina.
- Orientadas a interpretación gerencial.
- Consistentes en formatos de kilos, colones y porcentajes.
- Las cifras monetarias usarán el símbolo ₡ y los indicadores de volumen mostrarán kg.

### 11.8 Separación obligatoria entre código e IA

El código calcula; la IA interpreta.
- Python calcula el Fill Rate.
- Python calcula los kilos faltantes.
- Python realiza agregaciones y cruces.
- Python genera los rankings numéricos.
- El agente analiza los patrones.
- El agente redacta recomendaciones.
- El usuario toma las decisiones.

### 11.9 Restricciones para OpenCode

- Prohibido inventar reglas comerciales que no estén especificadas en este documento.
- Prohibido inventar columnas o valores del Excel real.
- Prohibido incorporar servicios de IA en la nube.
- Prohibido cambiar las fórmulas aprobadas.
- Prohibido calcular porcentajes de faltantes como indicadores.
- Prohibido combinar kilos y colones en una puntuación ponderada sin aprobación.
- Prohibido ejecutar acciones operativas autónomas no autorizadas.
- Prohibido modificar los archivos de origen.
- Todos los cálculos deben contar con pruebas automatizadas.
- Los supuestos pendientes deben mantenerse identificados, sin convertirlos silenciosamente en requisitos definitivos.

---

## Pendientes y contradicciones conocidas

1. **Archivos esperados vs entregados:** el contexto requiere 4 archivos Excel separados (`1-11-26.xlsx`, `2-11-26.xlsx`, `Ventas_Octubre_2026.xlsx`, `Ventas_Noviembre_2025.xlsx`), pero el único insumo real es `Fill Rate Noviembre - Diciembre 2025.xlsx` con hojas agrupadas. Se asume usar `FR NOV 2025` / `FR DIC 2025` como Fill Rate y `Kilos Vendidos Nov - Dic` como histórico, según indicación del usuario.
2. **Columnas del Fill Rate:** el Excel real tiene `Descri Clase`, `Descri Articulo`, `Pedido`, `Recibido`, `Diferencia`, `% de servicio`; el contexto (imagen) menciona `Mes`, `Categoría`, `Artículo`, `Pedido`, `Asignado`, `Sin Asignar`, `Fill Rate`, `% Faltante`, `Origen`. Falta validar el mapeo definitivo contra el Excel completo.
3. **Centro de Carne y fecha:** las hojas de Fill Rate no tienen columna Centro de Carne ni fecha diaria completa. Por indicación del usuario, Centro de Carne se omite por ahora.
4. **Cifras de control:** las cifras de aceptación del contexto usan datos de prueba ficticios que no están en los insumos entregados; no son validables aún contra el archivo real.
5. **Período del histórico de ventas:** la muestra de `Kilos Vendidos Nov - Dic` mostraba `Año = 2024`, pero el usuario indicó que las ventas son de 2025. Pendiente confirmar el período real cubierto por esas 18092 filas.
6. **Supuestos del contexto:** S01–S12 de la sección 12 del contexto permanecen pendientes de confirmar (columnas exactas, umbrales de semáforos, productos prioritarios, permisos, memoria para IA local, autenticación, reglas de priorización, días sin pedidos, tiempo de proceso actual).

---

Fin del AGENTS.md
