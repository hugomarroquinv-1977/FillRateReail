# VALIDACIÓN — FillRateRetail

Resultado de la ejecución de pruebas contra las cifras de control y los casos límite definidos en `AGENTS.md`.

Generado por el subagente @tester (entrega 14 del PLAN.md).
No se modificó el código de la app ni se "ajustaron" los números para que coincidan.

---

## 1. RESUMEN DE PRUEBAS

| Métrica | Valor |
|---------|-------|
| Total de pruebas | 32 |
| Pruebas aprobadas | 32 |
| Pruebas fallidas | 0 |
| Archivo de pruebas de cifras de control | `tests/test_fill_rate.py` |
| Archivo de pruebas de casos límite | `tests/test_casos_limite.py` |
| Comando de ejecución | `.venv\Scripts\python.exe -m pytest tests/ -v` |

---

## 2. CIFRAS DE CONTROL — ESPERADO vs OBTENIDO

### 2.1 Primer día: 1 de noviembre de 2026 (AGENTS.md, sección 9.1)

| Indicador | Esperado | Obtenido | Estado |
|-----------|----------|----------|--------|
| Kilos solicitados | 250 | 250 | ✅ |
| Kilos entregados | 193 | 193 | ✅ |
| Kilos faltantes | 57 | 57 | ✅ |
| Fill Rate general | 77,20 % | 77,20 % | ✅ |

**Por categoría**

| Categoría | Pedido kg (E) | Pedido kg (O) | Entrega kg (E) | Entrega kg (O) | Faltante kg (E) | Faltante kg (O) | Fill Rate (E) | Fill Rate (O) | Estado |
|-----------|---------------|---------------|----------------|----------------|-----------------|-----------------|---------------|---------------|--------|
| Res | 140 | 140 | 95 | 95 | 45 | 45 | 67,86 % | 67,86 % | ✅ |
| Cerdo | 110 | 110 | 98 | 98 | 12 | 12 | 89,09 % | 89,09 % | ✅ |
| Total | 250 | 250 | 193 | 193 | 57 | 57 | 77,20 % | 77,20 % | ✅ |

### 2.2 Segundo día: 2 de noviembre de 2026 (AGENTS.md, sección 9.2)

| Indicador | Esperado | Obtenido | Estado |
|-----------|----------|----------|--------|
| Kilos solicitados | 300 | 300 | ✅ |
| Kilos entregados | 256 | 256 | ✅ |
| Kilos faltantes | 44 | 44 | ✅ |
| Fill Rate general | 85,33 % | 85,33 % | ✅ |

### 2.3 Consolidado de ambos días (AGENTS.md, sección 9.3, R14)

| Indicador | Esperado | Obtenido | Estado |
|-----------|----------|----------|--------|
| Kilos solicitados | 550 | 550 | ✅ |
| Kilos entregados | 449 | 449 | ✅ |
| Kilos faltantes | 101 | 101 | ✅ |
| Fill Rate consolidado | 81,64 % | 81,64 % | ✅ |

**Verificación R14:** El Fill Rate consolidado se calculó con totales (449/550 = 81,64 %), NO como promedio simple de porcentajes diarios ((77,20 + 85,33)/2 = 81,265 % ≠ 81,64 %).

### 2.4 Consolidado por categoría (AGENTS.md, sección 9.4)

| Categoría | Pedido kg (E) | Pedido kg (O) | Entrega kg (E) | Entrega kg (O) | Faltante kg (E) | Faltante kg (O) | Fill Rate (E) | Fill Rate (O) | Estado |
|-----------|---------------|---------------|----------------|----------------|-----------------|-----------------|---------------|---------------|--------|
| Res | 290 | 290 | 215 | 215 | 75 | 75 | 74,14 % | 74,14 % | ✅ |
| Cerdo | 260 | 260 | 234 | 234 | 26 | 26 | 90,00 % | 90,00 % | ✅ |
| Total | 550 | 550 | 449 | 449 | 101 | 101 | 81,64 % | 81,64 % | ✅ |

### 2.5 Consolidado por Centro de Carne (AGENTS.md, sección 9.5)

| Centro | Pedido kg (E) | Pedido kg (O) | Entrega kg (E) | Entrega kg (O) | Faltante kg (E) | Faltante kg (O) | Fill Rate (E) | Fill Rate (O) | Estado |
|--------|---------------|---------------|----------------|----------------|-----------------|-----------------|---------------|---------------|--------|
| CC A | 350 | 350 | 295 | 295 | 55 | 55 | 84,29 % | 84,29 % | ✅ |
| CC B | 200 | 200 | 154 | 154 | 46 | 46 | 77,00 % | 77,00 % | ✅ |
| Total | 550 | 550 | 449 | 449 | 101 | 101 | 81,64 % | 81,64 % | ✅ |

### 2.6 Control de recurrencia (AGENTS.md, sección 9.6)

| Centro | Artículo | Faltante total kg (E) | Faltante total kg (O) | Días con faltante (E) | Días con faltante (O) | Estado |
|--------|----------|----------------------|----------------------|----------------------|----------------------|--------|
| CC A | R001 | 55 | 55 | 2 | 2 | ✅ |
| CC B | R001 | 20 | 20 | 1 | 1 | ✅ |
| CC B | C001 | 26 | 26 | 2 | 2 | ✅ |

**Productos identificados como recurrentes (2+ fechas):** R001 (CC A), C001 (CC B) ✅
**Producto con faltante pero NO recurrente:** R001 (CC B, 1 fecha) ✅

### 2.7 Control de rankings comerciales — octubre 2026 (AGENTS.md, sección 9.7)

| Centro | Métrica | Artículo (E) | Artículo (O) | Valor (E) | Valor (O) | Estado |
|--------|---------|-------------|-------------|-----------|-----------|--------|
| CC A | Mayor volumen (kg) | R001 | R001 | 900 kg | 900 kg | ✅ |
| CC A | Mayor venta (colones) | R001 | R001 | ₡4.500.000 | ₡4.500.000 | ✅ |
| CC B | Mayor volumen (kg) | C001 | C001 | 700 kg | 700 kg | ✅ |
| CC B | Mayor venta (colones) | C001 | C001 | ₡2.100.000 | ₡2.100.000 | ✅ |

---

## 3. CASOS LÍMITE — ESPERADO vs OBTENIDO (AGENTS.md, sección 10)

| Caso | Comportamiento obligatorio | Resultado obtenido | Estado |
|------|---------------------------|--------------------|--------|
| Pedido de cero kilos | No calcular Fill Rate por división entre cero | `fill_rate_pct = None`, `es_valido = False` | ✅ |
| Entrega superior al pedido | Marcar inconsistencia para revisión | `motivo_exclusion` contiene "Entrega superior" | ✅ |
| Campos incompletos (nulos) | Excluir del cálculo válido | Registros con nulos contados como excluidos | ✅ |
| Producto sin histórico de ventas | Mostrar "no disponible", no como cero | `ventas_kg = "no disponible"`, `ventas_crc = "no disponible"` | ✅ |
| Duplicado exacto | No contabilizar dos veces (a nivel de archivo) | Hash SHA-256 detecta contenido idéntico | ✅ |
| Modelo de IA no disponible | Mantener cálculos, señalar que IA no está disponible | JSON con `limitaciones` reportando "Modelo de IA no disponible" | ✅ |
| JSON sin alertas | Devolver listas vacías | `alertas = []`, `productos_indispensables = []`, `riesgos_detectados = []` | ✅ |
| Fecha inválida en nombre de archivo | No asignar fecha inventada | `fecha = None`, mensaje de error | ✅ |
| Nombre sin formato día-mes-año | Retornar error | `fecha = None`, mensaje de error | ✅ |
| Archivo vacío | Informar que no contiene registros procesables | 0 válidos, 0 excluidos, 0 pendientes | ✅ |
| Dos archivos mismos fecha, distinto contenido | Detectar conflicto (hashes distintos) | Hashes SHA-256 diferentes | ✅ |
| Unidades en lugar de kilos | No mezclar con indicadores en kg | Valores procesados sin conversión automática de unidades | ✅ |

---

## 4. ADVERTENCIAS

- **Pandas4Warning:** En `app/services/rankings.py` línea 124, `fillna("no disponible")` se aplica a una columna de tipo float64. Esto genera una advertencia de pandas pero no afecta la funcionalidad. Se recomienda convertir la columna a string antes de aplicar `fillna` en una futura entrega.
- Los casos límite que requieren archivos físicos (archivo corrupto, escaneado, con columnas faltantes, protegido con contraseña, en otro idioma, con pestañas múltiples) no se probaron con archivos reales porque los insumos entregados no incluyen esos casos. Se probaron los comportamientos lógicos equivalentes en los servicios existentes.

---

## 5. CONCLUSIÓN

Todas las 32 pruebas pasan. Las cifras de control de AGENTS.md coinciden exactamente con los resultados obtenidos de los cálculos de la app. No hay diferencias reportadas.

**Comando para reproducir:**
```
.venv\Scripts\python.exe -m pytest tests/ -v
```
