MONTECILLOS  /  DIVISIÓN RETAIL
DOCUMENTO
DE CONTEXTO
FillRateRetail
Sistema inteligente de análisis de Fill Rate y abastecimiento comercial
Versión  1.1 · Corrección de la referencia visual de Fill Rate
Fecha  4 de noviembre de 2026
Destino  Equipo de desarrollo mediante OpenCode
Estado  Formato visual de Fill Rate recibido; archivo Excel completo y datos reales pendientes de validación
DOCUMENTO INTERNO Y CONFIDENCIAL · Contiene especificaciones para el manejo local de información comercial.
Contenido
01   Qué es esta app
02   El proceso hoy
03   Datos de entrada
04   Reglas de negocio para el código
05   Lo que hace el agente de IA
06   Qué produce la app
07   Quién decide
08   Datos de prueba que hay que generar
09   Cifras de control
10   Casos límite
11   Reglas del sistema
12   Supuestos por confirmar
Actualización v1.1: se corrigió la referencia de la captura de la pregunta 2. La nueva imagen es el formato de Fill Rate; la anterior corresponde a ventas. El diseño de importación sigue sujeto a la entrega del Excel real.
Criterios de lectura
Las reglas identificadas como R01–R33 son verificables y deben quedar implementadas mediante código.
Los elementos marcados como SUPUESTO requieren validación antes de convertirse en decisiones definitivas.
El cálculo de Fill Rate y faltantes debe ser determinístico; la IA solo interpreta y recomienda.
1. Qué es esta app
1.1 Descripción general
FillRateRetail es una aplicación web de uso local que automatiza el análisis diario de cumplimiento de pedidos (Fill Rate) de los Centros de Carne de Montecillos.
Su propósito es identificar los faltantes de productos, detectar problemas recurrentes de abastecimiento y determinar cuáles artículos requieren atención prioritaria para proteger las ventas.
La aplicación integrará un agente de inteligencia artificial que interpretará los resultados de los análisis y generará conclusiones y recomendaciones comerciales.
1.2 Problema que resuelve
Actualmente se genera un reporte diario de Fill Rate, pero su presentación no facilita un análisis profundo de:
Productos con faltantes recurrentes.
Cantidades no entregadas en kilogramos.
Cumplimiento por categoría y Centro de Carne.
Tendencias históricas de abastecimiento.
Productos de mayor importancia comercial.
Riesgos de futuros faltantes.
Prioridades de abastecimiento según ventas históricas en kilos y colones.
1.3 Objetivo principal
Proteger las ventas mediante la identificación temprana de faltantes y la priorización del abastecimiento de productos comercialmente relevantes.
1.4 Alcance
La primera versión será una aplicación de consulta, análisis y recomendaciones. No realizará pedidos automáticamente, no modificará los pedidos originales y no ejecutará decisiones de abastecimiento sin intervención humana.
2. El proceso hoy
2.1 Proceso operativo actual

| Tabla |
|---|
| Paso | Actividad | Responsable |
| 1 | Preparar los pedidos diarios de los Centros de Carne | Asistente de pedidos |
| 2 | Descargar el archivo diario de Fill Rate | Asistente de pedidos |
| 3 | Revisar la información de cumplimiento | Asistente de pedidos |
| 4 | Preparar una captura del informe diario | Asistente de pedidos |
| 5 | Compartir el informe con los supervisores | Asistente de pedidos |
| 6 | Revisar los faltantes y problemas de abastecimiento | Supervisores |
| 7 | Evaluar el desempeño comercial y operativo | Gerencia de División Retail |

Tiempo actual del proceso: No indicado. Debe medirse posteriormente, sin asumir una cantidad de minutos.
Origen del archivo: Sistema desde el que se descarga el Fill Rate; nombre no indicado.
2.2 Proceso futuro automatizado
La asistente guarda los archivos diarios de Fill Rate en una carpeta local.
La aplicación identifica los nuevos archivos por fecha.
Lee, valida y consolida los datos.
Calcula los porcentajes de cumplimiento y los kilos faltantes.
Cruza los resultados con los históricos de ventas.
Genera rankings de productos por Centro de Carne y categoría.
Identifica productos con faltantes recurrentes.
El agente de IA interpreta los indicadores y genera recomendaciones.
Los usuarios consultan el tablero gerencial o descargan los reportes.
Resultado esperado: reducir el trabajo manual de análisis, mejorar la visibilidad de los faltantes y facilitar decisiones oportunas.
3. Datos de entrada
3.1 Archivos requeridos

| Tabla |
|---|
| Archivo o dato | Formato | Contenido | Ejemplo |
| Fill Rate diario | Excel .xlsx | Reporte real de Fill Rate (formato visual corregido). Campos concretos pendientes de validar con el Excel completo. | 1-11-26.xlsx |
| Fill Rate diario siguiente | Excel .xlsx | Nuevo reporte del día, siguiendo el formato visual de Fill Rate presentado. | 2-11-26.xlsx |
| Ventas del mes anterior | Excel .xlsx | Kilos vendidos y ventas en colones | Ventas_Octubre_2026.xlsx |
| Ventas del mismo mes del año anterior | Excel .xlsx | Histórico comparable para estacionalidad | Ventas_Noviembre_2025.xlsx |

3.2 Organización de archivos
SUPUESTO: estructura de carpetas locales configurable desde la aplicación.
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
Las rutas serán configurables. No deben depender de nombres fijos de usuarios ni de rutas específicas de Windows.
3.3 Estructura de campos
Campos visibles en la captura correcta de Fill Rate
Estos nueve encabezados están observados en la captura de formato; no equivalen a validación de los datos ni de las fórmulas del archivo definitivo.

| Tabla |
|---|
| Col. | Nombre exacto | Interpretación y validación pendiente |
| A | Mes | Mes del reporte; año y fecha exacta pendientes de confirmar. |
| B | Categoría | Nombre o código de categoría; los ejemplos muestran errores #¡REF!. |
| C | Artículo | Identificador o descripción del artículo; captura con errores #¡REF!. |
| D | Pedido | Cantidad solicitada; unidad exacta y origen pendientes de confirmar. |
| E | Asignado | Cantidad asignada; confirmar equivalencia con entregado físicamente. |
| F | Sin Asignar | Cantidad sin asignación; comprobar si corresponde a faltantes en kg. |
| G | Fill Rate | Porcentaje observado como encabezado; debe recalcularse con datos válidos. |
| H | % Faltante | Columna existente en origen, pero NO se presentará como indicador en los reportes. |
| I | Origen | Referencia o procedencia del registro; ejemplo visible: Faltantes noviembre 2025. |

Observaciones críticas: el ejemplo presenta #¡REF! en varias columnas y 0,0 % en Fill Rate; dichos valores NO deben utilizarse como evidencia de incumplimiento real. La captura no incluye una columna visible de Centro de Carne ni una fecha diaria completa. Es obligatorio localizar esos datos en el Excel definitivo (pestaña, archivo o campo validado) antes del cruce por punto de venta.
CORRECCIÓN DE REFERENCIA (versión 1.1). La última captura proporcionada por el usuario corresponde al formato visual del reporte de Fill Rate y sustituye a la captura anterior como referencia para ese reporte. La captura anterior mostraba un ejemplo de ventas y no debe utilizarse para definir las columnas del Fill Rate. La captura nueva permite orientar la estructura, pero aún no sustituye la revisión técnica del Excel original con su contenido completo, que será facilitado posteriormente.

| Tabla |
|---|
| Campo lógico | Tipo | Uso |
| Fecha | Fecha | Identificar el día |
| Centro de Carne | Texto o código | Identificar establecimiento |
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

Importante: la tabla de campos lógicos a continuación describe los datos que necesita el sistema, NO confirma la presencia de columnas de igual nombre en el Excel. En el formato visible se lee «Pedido», «Asignado» y «Sin Asignar»: no se puede asumir que «Asignado» signifique recibido hasta validar la lógica del reporte y sus unidades.
El desarrollador debe usar la nueva captura de Fill Rate como referencia visual inicial. El mapeo definitivo de columnas, tipos de datos y hojas se realizará al revisar el Excel real; está prohibido deducir esos campos a partir del ejemplo anterior de ventas.
3.4 Tratamiento del período histórico
Para analizar noviembre de 2026:
Fill Rate: archivos diarios de noviembre de 2026.
Ventas recientes: octubre de 2026.
Ventas estacionales: noviembre de 2025.
Ambos históricos deben conservarse identificados por período y no sumarse sin una regla expresamente aprobada.
4. Reglas de negocio para el código
Las reglas siguientes deberán implementarse mediante código Python. No deben depender de interpretaciones del agente de IA.
4.1 Lectura y validación

| Tabla |
|---|
| Regla | Descripción verificable |
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

4.2 Cálculo del Fill Rate
R11. Cálculo del cumplimiento
Fill Rate (%) = (Kilos entregados / Kilos solicitados) × 100
La fórmula se aplica únicamente cuando los kilos solicitados son mayores que cero y los datos son válidos.
R12. Cálculo de faltantes
Kilos faltantes = Kilos solicitados − Kilos entregados
El faltante se mostrará exclusivamente en kilos.
R13. Formato de indicadores
Fill Rate: porcentaje.
Faltantes: kilogramos.
Ventas históricas: colones y kilogramos, por separado.
Está prohibido presentar porcentajes de faltantes como indicador de negocio.
R14. Fill Rate consolidado
El cumplimiento general debe calcularse usando los totales de kilos solicitados y entregados. No se permitirá promediar directamente los porcentajes individuales de los productos o establecimientos.
R15. Niveles de agregación
Calcular Fill Rate y kilos faltantes para:
Producto.
Categoría.
Centro de Carne.
Categoría dentro de cada Centro de Carne.
Total de la División Retail.
R16. Casos matemáticos inválidos
Los pedidos con cantidad cero no generarán un porcentaje de cumplimiento calculado por división entre cero. Si los kilos entregados exceden los solicitados, el registro deberá marcarse para revisión y no ajustarse silenciosamente.
4.3 Análisis histórico

| Tabla |
|---|
| Regla | Descripción verificable |
| R17 | Consolidar el histórico diario de faltantes por Centro de Carne, categoría y artículo. |
| R18 | Contar la cantidad de fechas diferentes en las que un mismo producto registra kilos faltantes mayores que cero. |
| R19 | Identificar faltantes recurrentes cuando un producto tenga faltantes en dos o más fechas distintas. |
| R20 | Identificar faltantes en días consecutivos. Si falta el archivo de una fecha intermedia, no se debe asumir que existió o no un faltante ese día. |
| R21 | Permitir la consulta de resultados por día, rango de fechas, Centro de Carne, categoría y artículo. |

4.4 Importancia comercial

| Tabla |
|---|
| Regla | Descripción verificable |
| R22 | Cruzar los productos con el archivo de ventas del mes anterior. |
| R23 | Cruzar los productos con las ventas del mismo mes del año anterior. |
| R24 | Generar rankings independientes por kilos vendidos y por ventas en colones. |
| R25 | Generar los rankings por Centro de Carne, por categoría y a nivel consolidado. |
| R26 | Mantener separados los indicadores históricos de ambos períodos, sin asignar ponderaciones no aprobadas. |
| R27 | Si un producto no aparece en el histórico de ventas, mostrarlo como dato no disponible. No interpretarlo automáticamente como cero ventas. |
| R28 | No convertir las ventas históricas en una supuesta pérdida económica real sin una metodología de cálculo previamente aprobada. |

4.5 Generación de resultados

| Tabla |
|---|
| Regla | Descripción verificable |
| R29 | Ordenar los rankings de mayor a menor según la métrica seleccionada. |
| R30 | Permitir exportar los datos y resultados en Excel y PDF. |
| R31 | Mantener identificable la fuente de cada cálculo. |
| R32 | Ningún resultado generado por IA podrá modificar los cálculos matemáticos originales. |
| R33 | No emitir pedidos, modificar inventarios ni ejecutar abastecimiento automáticamente. |

5. Lo que hace el agente de IA
5.1 Rol del agente
Analista inteligente de abastecimiento y protección de ventas Retail
Su responsabilidad será convertir los indicadores calculados por el sistema en información útil para la toma de decisiones comerciales y operativas.
5.2 Información que recibe
Recibirá datos previamente validados y calculados:
Cumplimiento de Fill Rate.
Faltantes diarios y acumulados en kilos.
Frecuencia de faltantes por producto.
Comportamiento histórico por Centro de Carne.
Rankings de ventas en kilos.
Rankings de ventas en colones.
Ventas del mes anterior.
Ventas del mismo mes del año anterior.
Incidencias de calidad de datos.
El agente no deberá procesar directamente archivos desconocidos sin pasar primero por el módulo de validación.
5.3 Funciones de inteligencia artificial
A. Identificación de faltantes críticos
Señalar productos con faltantes recurrentes que, además, tienen importancia comercial según sus históricos de venta.
B. Identificación de riesgos
Detectar patrones de faltantes diarios y señalar productos que podrían presentar nuevos problemas de abastecimiento. El riesgo debe presentarse como una estimación, no como un hecho confirmado.
C. Protección de ventas
Recomendar los productos que deben recibir atención prioritaria para evitar afectaciones comerciales.
D. Recomendaciones por Centro de Carne
Generar conclusiones específicas para cada establecimiento, considerando su propio comportamiento de venta.
E. Resumen gerencial
Redactar un resumen de los principales hallazgos, riesgos, oportunidades y prioridades.
5.4 Contrato JSON de salida
El agente deberá devolver un JSON válido con la siguiente estructura:

| Tabla |
|---|
| Llave JSON | Tipo | Descripción |
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

Estructura obligatoria de la evidencia
Cada alerta deberá incluir los siguientes datos dentro de evidencia:

| Tabla |
|---|
| Llave | Tipo | Contenido |
| kilos_faltantes | number o string | Kilos no entregados |
| dias_con_faltante | integer o string | Número de fechas con faltantes |
| fill_rate_pct | number o string | Porcentaje de cumplimiento |
| ventas_historicas_kg | number o string | Volumen vendido de referencia |
| ventas_historicas_crc | number o string | Valor vendido de referencia |
| periodo_referencia | string | Período de las ventas históricas |

Reglas obligatorias del agente
Nunca inventar datos, productos, fechas, cifras ni causas de faltantes.
Si un campo no aparece o no puede determinarse, utilizar exactamente "no indicado".
Los datos numéricos válidos deben devolverse como números, sin símbolos monetarios ni unidades en el valor.
No modificar cifras previamente calculadas por Python.
Distinguir explícitamente los hechos confirmados de las estimaciones.
No afirmar que existe un problema de producción, inventario o logística si los datos únicamente demuestran un faltante de abastecimiento.
Justificar las recomendaciones mediante datos concretos.
No recomendar cantidades específicas de reposición sin contar con una regla aprobada para calcularlas.
Devolver listas vacías cuando no existan alertas sustentadas.
Si el modelo local no está disponible, el sistema debe seguir mostrando los cálculos y señalar que las recomendaciones de IA no están disponibles.
5.5 Criterios de interpretación

| Tabla |
|---|
| Criterio | Definición |
| Alta importancia en kilos | Producto situado en los primeros lugares del ranking de volumen histórico. |
| Alta importancia en colones | Producto situado en los primeros lugares del ranking de ventas monetarias. |
| Recurrencia | Faltantes registrados en diferentes fechas. |
| Riesgo | Patrón detectado que justifica seguimiento, sin garantizar que se producirá un nuevo faltante. |

Pendiente de confirmar: umbrales cuantitativos de semáforos y cantidad de posiciones prioritarias. Hasta aprobar estos parámetros, los rankings numéricos deben permanecer separados y transparentes.
6. Qué produce la app
6.1 Pantalla principal: tablero gerencial

| Tabla |
|---|
| Indicador | Presentación |
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

6.2 Pantalla de análisis por Centro de Carne
El usuario seleccionará un establecimiento y visualizará:
Fill Rate general del Centro de Carne.
Fill Rate por categoría.
Productos con faltantes.
Kilos faltantes acumulados.
Frecuencia de incumplimientos.
Rankings de importancia comercial.
Productos que necesitan prioridad de abastecimiento.
Recomendaciones específicas de IA.
6.3 Pantalla de análisis por categoría
Permitirá visualizar categorías y productos con sus respectivos indicadores de cumplimiento, faltantes e importancia comercial.
6.4 Pantalla histórica
Mostrará tendencias por día y período, faltantes recurrentes y evolución del cumplimiento.
6.5 Pantalla de administración de archivos
Configurar las carpetas locales.
Consultar los archivos encontrados.
Revisar las fechas procesadas.
Identificar archivos con errores.
Actualizar el análisis manualmente.
Consultar el registro de importaciones.
6.6 Semáforos
Se reservará un componente visual para indicar niveles de atención del Fill Rate y del abastecimiento.
SUPUESTO PENDIENTE: No existen porcentajes límite aprobados para asignar colores rojo, amarillo y verde. No deben inventarse ni activarse como clasificación automática hasta definirlos.
6.7 Botones principales
Actualizar análisis.
Seleccionar Centro de Carne.
Filtrar categoría.
Seleccionar período.
Ver histórico.
Ver recomendaciones de IA.
Descargar Excel.
Descargar PDF.
Revisar errores de carga.
6.8 Reportes descargables
Reporte Excel: incluirá datos consolidados, cálculos de Fill Rate, faltantes en kilos, rankings e indicadores históricos.
Reporte PDF: presentará un resumen gerencial, principales indicadores, productos críticos y recomendaciones.
Ambos se generarán localmente.
7. Quién decide
7.1 Roles operativos

| Tabla |
|---|
| Usuario | Responsabilidad |
| Asistente de pedidos | Mantener disponibles los archivos diarios y revisar los resultados |
| Supervisores | Consultar resultados por Centro de Carne e identificar incidencias |
| Gerente de División Retail | Evaluar los indicadores consolidados y las prioridades comerciales |
| Agente de IA | Generar análisis y recomendaciones sin tomar decisiones autónomas |

7.2 Decisión final
La inteligencia artificial únicamente recomienda. Las decisiones relacionadas con cambios de abastecimiento, prioridades de pedidos, escalamiento de incidencias o intervenciones operativas deben permanecer bajo responsabilidad humana.
SUPUESTO: El Gerente de División Retail establecerá prioridades generales y los supervisores coordinarán el seguimiento correspondiente. La autoridad exacta para modificar pedidos está pendiente de confirmar.
7.3 Permisos de usuario
SUPUESTO: La primera versión utilizará roles de consulta y administración local. La necesidad de autenticación por usuario y contraseña debe confirmarse antes de implementar un sistema completo de permisos.
8. Datos de prueba que hay que generar
Los desarrolladores deberán crear archivos Excel ficticios sin utilizar información comercial real.
8.1 Archivo 1-11-26.xlsx

| Tabla |
|---|
| Centro | Categoría | Artículo | Pedido kg | Entrega kg |
| CC A | Res | R001 | 100 | 75 |
| CC A | Cerdo | C001 | 50 | 50 |
| CC B | Res | R001 | 40 | 20 |
| CC B | Cerdo | C001 | 60 | 48 |

8.2 Archivo 2-11-26.xlsx

| Tabla |
|---|
| Centro | Categoría | Artículo | Pedido kg | Entrega kg |
| CC A | Res | R001 | 120 | 90 |
| CC A | Cerdo | C001 | 80 | 80 |
| CC B | Res | R001 | 30 | 30 |
| CC B | Cerdo | C001 | 70 | 56 |

Estos archivos permitirán verificar los cálculos diarios, el consolidado y la identificación de faltantes recurrentes.
8.3 Archivo Ventas_Octubre_2026.xlsx

| Tabla |
|---|
| Centro | Artículo | Ventas kg | Ventas ₡ |
| CC A | R001 | 900 | 4.500.000 |
| CC A | C001 | 500 | 1.500.000 |
| CC B | R001 | 350 | 1.750.000 |
| CC B | C001 | 700 | 2.100.000 |

8.4 Archivo Ventas_Noviembre_2025.xlsx

| Tabla |
|---|
| Centro | Artículo | Ventas kg | Ventas ₡ |
| CC A | R001 | 800 | 4.000.000 |
| CC A | C001 | 450 | 1.350.000 |
| CC B | R001 | 400 | 2.000.000 |
| CC B | C001 | 650 | 1.950.000 |

8.5 Archivos de prueba adicionales
Archivo vacío.
Archivo dañado.
Nombre de archivo inválido.
Fecha duplicada.
Archivo con columnas faltantes.
Producto no existente en los históricos.
Pedido con cero kilos.
Entrega superior a lo solicitado.
Datos de kilos mezclados con unidades.
Ausencia de un día intermedio.
Archivo con varias pestañas.
Los archivos deberán diseñarse con los campos lógicos de este documento, sin atribuirlos al formato real todavía no recibido.
9. Cifras de control
Los siguientes valores son resultados esperados obligatorios para las pruebas de aceptación.
9.1 Primer día: 1 de noviembre de 2026

| Tabla |
|---|
| Indicador | Resultado esperado |
| Kilos solicitados | 250 |
| Kilos entregados | 193 |
| Kilos faltantes | 57 |
| Fill Rate general | 77,20 % |

Cumplimiento por categoría

| Tabla |
|---|
| Categoría | Pedido kg | Entrega kg | Faltante kg | Fill Rate |
| Res | 140 | 95 | 45 | 67,86 % |
| Cerdo | 110 | 98 | 12 | 89,09 % |
| Total | 250 | 193 | 57 | 77,20 % |

9.2 Segundo día: 2 de noviembre de 2026

| Tabla |
|---|
| Indicador | Resultado esperado |
| Kilos solicitados | 300 |
| Kilos entregados | 256 |
| Kilos faltantes | 44 |
| Fill Rate general | 85,33 % |

9.3 Consolidado de ambos días

| Tabla |
|---|
| Indicador | Resultado esperado |
| Kilos solicitados | 550 |
| Kilos entregados | 449 |
| Kilos faltantes | 101 |
| Fill Rate consolidado | 81,64 % |

(449 / 550) × 100 = 81,63636… %  →  81,64 %
Está prohibido sustituir este cálculo por un promedio simple de los porcentajes diarios.
9.4 Consolidado por categoría

| Tabla |
|---|
| Categoría | Pedido kg | Entrega kg | Faltante kg | Fill Rate |
| Res | 290 | 215 | 75 | 74,14 % |
| Cerdo | 260 | 234 | 26 | 90,00 % |
| Total | 550 | 449 | 101 | 81,64 % |

9.5 Consolidado por Centro de Carne

| Tabla |
|---|
| Centro | Pedido kg | Entrega kg | Faltante kg | Fill Rate |
| CC A | 350 | 295 | 55 | 84,29 % |
| CC B | 200 | 154 | 46 | 77,00 % |
| Total | 550 | 449 | 101 | 81,64 % |

9.6 Control de recurrencia

| Tabla |
|---|
| Centro | Artículo | Faltante total kg | Días con faltante |
| CC A | R001 | 55 | 2 |
| CC B | R001 | 20 | 1 |
| CC B | C001 | 26 | 2 |

El sistema deberá identificar a R001 del CC A y C001 del CC B como productos con faltantes recurrentes. R001 del CC B tiene un faltante comprobado, pero no recurrente en este conjunto de prueba.
9.7 Control de rankings comerciales
Utilizando octubre de 2026:
CC A — Mayor volumen vendido: R001, con 900 kg.
CC A — Mayor venta en colones: R001, con ₡4.500.000.
CC B — Mayor volumen vendido: C001, con 700 kg.
CC B — Mayor venta en colones: C001, con ₡2.100.000.
En ambos Centros de Carne, estos artículos deben aparecer en primer lugar en sus respectivos rankings.
9.8 Validación de calidad
El desarrollo será aceptable cuando:
Todos los cálculos coincidan con las cifras de control.
La carga repetida de un archivo no duplique los resultados.
Los registros inválidos sean identificados.
Los rankings respeten la métrica y el período seleccionados.
Las recomendaciones del agente estén fundamentadas en la evidencia disponible.
El sistema funcione localmente sin transmitir datos comerciales.
Los reportes descargados coincidan con los datos del tablero.
10. Casos límite

| Tabla |
|---|
| Caso | Comportamiento obligatorio |
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

Regla general: no transformar la ausencia de información en un cero que distorsione los indicadores.
Los registros excluidos deberán ser visibles en un reporte de incidencias.
11. Reglas del sistema
11.1 Tecnologías obligatorias

| Tabla |
|---|
| Componente | Tecnología |
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
11.2 Arquitectura MVC
Modelo
Responsable de almacenar y consultar registros de pedidos, entregas, faltantes, históricos de ventas, archivos procesados y resultados calculados.
Vista
Responsable de presentar el tablero, tablas, filtros, gráficos, alertas y recomendaciones en español.
Controlador
Responsable de recibir las solicitudes del usuario, coordinar importaciones, ejecutar cálculos, consultar el agente y preparar las respuestas.
Adicionalmente, se deberán separar los servicios especializados:
Importación y validación de Excel.
Cálculo de Fill Rate.
Análisis de recurrencia.
Cruce con históricos de ventas.
Construcción de rankings.
Integración con el agente local.
Exportación de informes.
La lógica de cálculo no deberá quedar mezclada con las plantillas visuales ni con las instrucciones de IA.
11.3 Arquitectura de inteligencia artificial
El sistema deberá utilizar un modelo local compatible con el computador donde se instalará la aplicación.
SUPUESTO técnico: evaluar Ollama o llama.cpp como motor local, sujeto a las características del equipo disponible.
El agente no deberá utilizar servicios externos de inferencia. Los datos comerciales no podrán enviarse a:
APIs de inteligencia artificial en la nube.
Servicios externos de análisis.
Plataformas de telemetría.
Servidores de terceros.
El modelo y sus dependencias deberán estar disponibles localmente para que el sistema opere sin conexión a Internet. No se permitirán descargas automáticas de modelos o actualizaciones durante el funcionamiento normal.
11.4 Seguridad
El acceso web se limitará al equipo local, utilizando la dirección 127.0.0.1, salvo una autorización expresa posterior.
Los archivos originales, las bases de datos, los resultados, los registros técnicos y los informes deberán mantenerse en el computador autorizado.
La aplicación deberá:
Evitar conexiones externas innecesarias.
Restringir accesos a carpetas fuera de la configuración.
No incluir datos comerciales completos en registros técnicos.
No exponer secretos en pantallas o mensajes de error.
Validar nombres y tipos de archivos antes de procesarlos.
Manejar los errores sin revelar credenciales.
11.5 Archivo .env
Toda llave o credencial de acceso del agente deberá configurarse en .env y nunca dentro del código fuente. En una instalación local sin autenticación del motor de IA, la variable de llave podrá permanecer vacía.
El archivo .env no debe subirse al repositorio ni incluirse en entregables públicos.
11.6 Inicio de la aplicación
Crear obligatoriamente iniciar_app.bat. Al ejecutarlo, deberá iniciar la aplicación local, utilizando el entorno gestionado por uv.
SUPUESTO: el archivo también abrirá automáticamente el navegador predeterminado en la dirección local del tablero.
El usuario no deberá necesitar conocimientos de programación para iniciar el sistema.
11.7 Requisitos visuales
Completamente en español.
Sencillas e intuitivas.
Legibles en una computadora de oficina.
Orientadas a interpretación gerencial.
Consistentes en formatos de kilos, colones y porcentajes.
Las cifras monetarias usarán el símbolo ₡ y los indicadores de volumen mostrarán kg.
11.8 Separación obligatoria entre código e IA
El código calcula; la IA interpreta.
Python calcula el Fill Rate.
Python calcula los kilos faltantes.
Python realiza agregaciones y cruces.
Python genera los rankings numéricos.
El agente analiza los patrones.
El agente redacta recomendaciones.
El usuario toma las decisiones.
11.9 Restricciones para OpenCode
Prohibido inventar reglas comerciales que no estén especificadas en este documento.
Prohibido inventar columnas o valores del Excel real.
Prohibido incorporar servicios de IA en la nube.
Prohibido cambiar las fórmulas aprobadas.
Prohibido calcular porcentajes de faltantes como indicadores.
Prohibido combinar kilos y colones en una puntuación ponderada sin aprobación.
Prohibido ejecutar acciones operativas autónomas no autorizadas.
Prohibido modificar los archivos de origen.
Todos los cálculos deben contar con pruebas automatizadas.
Los supuestos pendientes deben mantenerse identificados, sin convertirlos silenciosamente en requisitos definitivos.
12. Supuestos por confirmar
Esta sección contiene las decisiones pendientes antes de considerar completamente cerrada la especificación técnica.

| Tabla |
|---|
| ID | Supuesto o dato pendiente | Importancia |
| S01 | El formato visual correcto del Fill Rate fue aportado en una nueva captura. Falta validar el Excel completo y los encabezados exactos, tipos y correspondencias de columnas. | Crítica |
| S02 | Confirmar en el Excel real los campos y las unidades que representan kilos solicitados y entregados, antes de activar los cálculos con datos reales. | Crítica |
| S03 | Confirmar las hojas, fechas y estructura de cada Excel diario; los archivos se recibirán individualmente con fecha en el nombre. | Alta |
| S04 | Validar el Excel real de históricos de ventas; la primera captura de la entrevista no es el formato de Fill Rate. | Crítica |
| S05 | Definir los umbrales de semáforos de cumplimiento | Media |
| S06 | Definir cuántos productos deben destacarse como prioritarios en cada ranking | Media |
| S07 | Confirmar los permisos y responsables de cada decisión de abastecimiento | Alta |
| S08 | Verificar memoria RAM, procesador y capacidad del computador para ejecutar IA local | Crítica |
| S09 | Confirmar si será necesario autenticar a varios usuarios en la misma computadora | Media |
| S10 | Definir si se requiere alguna regla adicional para priorizar simultáneamente kilos, colones y recurrencia | Alta |
| S11 | Confirmar si existen días sin pedidos o sin descarga de archivos que deban tratarse especialmente | Media |
| S12 | Medir el tiempo que actualmente consume preparar y analizar el reporte | Media |

Criterio de cierre de los supuestos
Los supuestos relacionados con columnas, formatos y fórmulas no podrán sustituirse por decisiones arbitrarias del equipo de desarrollo. La aplicación puede diseñarse y probarse con datos ficticios, pero la integración definitiva dependerá de validar los archivos reales.
Resultado esperado del proyecto
Al finalizar el desarrollo, FillRateRetail permitirá que el equipo Retail de Montecillos pase de recibir un informe diario estático a utilizar una herramienta de inteligencia comercial que:
Conozca el cumplimiento real del abastecimiento.
Identifique faltantes en kilos y sus recurrencias.
Diferencie los productos más importantes por volumen y facturación.
Detecte patrones que merecen atención preventiva.
Recomiende prioridades por Centro de Carne.
Facilite el seguimiento gerencial y de supervisión.
Mantenga la información comercial protegida localmente.
Principio rector
Transformar el Fill Rate de un indicador de cumplimiento operativo en una herramienta de decisión para proteger las ventas y fortalecer la gestión de abastecimiento de la División Retail.
FIN DEL DOCUMENTO DE CONTEXTO · FillRateRetail