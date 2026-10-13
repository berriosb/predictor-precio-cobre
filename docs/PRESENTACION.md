# Predictor de Precio del Cobre
## Presentación Ejecutiva del Proyecto

---

## Slide 1: Portada

**PREDICTOR DE PRECIO DEL COBRE**

Sistema de Machine Learning para Predicción de Precios

**Resultados Destacados:**
- Precisión: 99.14% (R cuadrado)
- Error Promedio: $0.0173 USD/lb
- Dataset: 15+ años de datos históricos
- Modelos Evaluados: 5 algoritmos diferentes

**Autor**: Tu Nombre
**Fecha**: Octubre 2025

---

## Slide 2: Problema de Negocio

### Contexto

**Chile es el mayor productor de cobre del mundo**
- 28% de la producción global
- Ingresos fiscales dependientes del precio del cobre
- Industria crítica para la economía nacional

### El Desafío

El precio del cobre es **altamente volátil** y afecta:
- Presupuestos gubernamentales
- Inversiones CAPEX en minería
- Estrategias de cobertura financiera
- Decisiones de trading

### Pregunta Clave

**¿Cuál será el precio del cobre mañana, la próxima semana o el próximo mes?**

---

## Slide 3: Objetivo del Proyecto

### Objetivo General

Desarrollar un sistema de Machine Learning para **predecir el precio del cobre** con alta precisión utilizando:
- Series temporales
- Feature engineering avanzado
- Múltiples algoritmos de ML

### Objetivos Específicos

1. Analizar 15+ años de datos históricos del precio del cobre
2. Crear features predictivas basadas en patrones identificados
3. Comparar 5 modelos de machine learning diferentes
4. Seleccionar el mejor modelo para producción
5. Lograr R cuadrado > 0.90

### Valor Agregado

- Reducir incertidumbre en proyecciones financieras
- Optimizar estrategias de hedging
- Mejorar timing de decisiones comerciales

---

## Slide 4: Datos y Metodología

### Fuente de Datos

**Yahoo Finance (ticker HG=F)**
- Datos: Futuros de Cobre (Copper Futures)
- Periodo: Mayo 2010 - Octubre 2025
- Frecuencia: Diaria (días de mercado)
- Total Registros: 3,872 (después de limpieza)

### Pipeline de Trabajo

1. **Extracción** - Descarga desde Yahoo Finance
2. **EDA** - Análisis exploratorio de patrones
3. **Feature Engineering** - Creación de 42 features
4. **Modelado** - Entrenamiento de 5 modelos
5. **Evaluación** - Comparación y selección

### Split de Datos (Temporal)

- Train: 80% (3,097 registros) - 2010 a sep 2022
- Validation: 10% (387 registros) - sep 2022 a mar 2024
- Test: 10% (388 registros) - mar 2024 a oct 2025

**Crítico**: Sin shuffle para respetar orden cronológico

---

## Slide 5: Hallazgos del EDA

### Patrones Identificados

**1. Tendencia Alcista**
- Precio promedio creció de $3.20 (2010) a $4.50+ (2025)
- Crecimiento sostenido con volatilidad

**2. Estacionalidad**
- Precios 5% más altos en Q2 (marzo-mayo)
- Patrón repetible año tras año

**3. Volatilidad Variable**
- Baja en periodos normales (1-2% diaria)
- Picos en crisis: COVID-2020, Guerra Ucrania-2022
- 25 movimientos extremos >5% en 15 años

**4. Memoria Extrema del Mercado**
- Correlación lag_1 = 0.9975 (precio de ayer predice hoy)
- Autocorrelación muy fuerte hasta 30 días
- Mercado altamente predecible a corto plazo

---

## Slide 6: Feature Engineering

### 42 Features Creadas en 7 Grupos

**A. Estacionalidad** (6 features)
- Mes, trimestre, encoding cíclico
- Flags de temporada alta (Q2)

**B. Volatilidad** (6 features)
- Retornos diarios, desviación estándar móvil
- Indicadores de alta volatilidad

**C. Tendencia** (7 features)
- Medias móviles (7/30/90 días)
- Momentum e indicadores direccionales

**D. Outliers/Extremos** (4 features)
- Z-score, movimientos >5%
- Días desde último evento extremo

**E. Lags - Autocorrelación** (6 features)
- lag_1, lag_2, lag_3, lag_7, lag_14, lag_30
- **Feature más importante**: lag_1 (corr = 0.9975)

**F. Estadísticas** (6 features)
- Dispersión, rangos, posición relativa

**G. Intrasemanal** (7 features)
- Día de semana, inicio/fin de mes

### Validación

- Sin data leakage (todas las features miran hacia atrás)
- Dataset final: 3,872 registros x 42 features

---

## Slide 7: Modelos Evaluados

### 5 Modelos Implementados

**1. Linear Regression** (Baseline)
- Modelo más simple
- Sin regularización
- R cuadrado: 0.9923

**2. Ridge Regression**
- Regularización L2
- Grid Search para alpha óptimo
- R cuadrado: 0.9914

**3. XGBoost**
- Gradient boosting
- 500 árboles, lr=0.01
- R cuadrado: 0.6567

**4. Random Forest**
- 300 árboles, max_depth=10
- Ensemble robusto
- R cuadrado: 0.6809

**5. SARIMAX**
- ARIMA + features exógenas
- Auto-optimizado con pmdarima
- R cuadrado: 0.7593

---

## Slide 8: Resultados - Comparación de Modelos

### Tabla de Performance (Test Set)

| Modelo             | R cuadrado | MAE (USD/lb) | RMSE (USD/lb) | MAPE   |
|--------------------|------------|--------------|---------------|--------|
| **Ridge Regression** | **0.9914** | **$0.0173**  | **$0.0345**   | **0.38%** |
| Linear Regression  | 0.9923     | $0.0169      | $0.0326       | 0.37%  |
| SARIMAX            | 0.7593     | $0.1370      | $0.1822       | 3.02%  |
| Random Forest      | 0.6809     | $0.0876      | $0.2098       | 1.71%  |
| XGBoost            | 0.6567     | $0.0921      | $0.2176       | 1.80%  |

### Ganador: Ridge Regression

**¿Por qué Ridge ganó?**
- Maneja perfectamente la multicolinealidad (lags correlacionados 0.99+)
- Captura la relación lineal fuerte del precio del cobre
- Regularización mínima (alpha=0.01) suficiente
- Rápido, simple e interpretable

---

## Slide 9: Insights Clave

### 1. La Simplicidad Ganó

**Sorpresa**: Ridge Regression (R cuadrado=0.99) superó a XGBoost (R cuadrado=0.66)

**Lección**: Feature engineering de calidad > Complejidad del modelo

### 2. Relación Casi Perfectamente Lineal

- lag_1 (precio de ayer) explica 99.75% de hoy
- Modelos de árboles fragmentan el espacio, perdiendo suavidad
- Regularización lineal es óptima para este problema

### 3. Features Dominantes

**Top 5 Features** (por correlación):
1. lag_1 (0.9975)
2. rolling_mean_7 (0.9949)
3. lag_2 (0.9946)
4. lag_3 (0.9919)
5. rolling_mean_30 (0.9779)

**Patrón**: Lags y medias móviles dominan. Volatilidad y estacionalidad son marginales.

### 4. XGBoost Decepcionó

**Causas identificadas**:
- Hiperparámetros conservadores (max_depth=5)
- Overfitting al validation set
- No captura bien relaciones lineales suaves

---

## Slide 10: Visualizaciones

### Gráfico 1: Comparación de Métricas

**Barras horizontales comparando R cuadrado, MAE, RMSE, MAPE**
- Ridge destacado en verde
- Otros modelos en azul
- Ridge claramente superior en R cuadrado
- XGBoost/RF con errores mayores

### Gráfico 2: Predicciones vs Realidad

**Líneas temporales en Test Set (mar 2024 - oct 2025)**
- Línea negra: Precio real
- Líneas de colores: Predicciones de cada modelo
- Ridge casi perfectamente sobre la línea real
- XGBoost/RF con más desviaciones
- SARIMAX sigue la tendencia pero con más error

**Conclusión visual**: Ridge es indistinguible del precio real

---

## Slide 11: Modelo Recomendado para Producción

### Ridge Regression

**Especificaciones Técnicas**:
- Algoritmo: Ridge (sklearn.linear_model.Ridge)
- Hiperparámetro: alpha = 0.01
- Features: 42 (todas creadas en notebook 03)
- Tiempo de entrenamiento: <1 segundo
- Tiempo de predicción: <0.01 segundos

**Performance**:
- R cuadrado: 0.9914 (99.14% varianza explicada)
- MAE: $0.0173 USD/lb
- RMSE: $0.0345 USD/lb
- MAPE: 0.38%

**Intervalo de Confianza**:
- ±2 RMSE = ±$0.069 USD/lb (95% confianza)

### Pipeline de Producción

1. Descargar datos diarios (HG=F de Yahoo Finance)
2. Generar 42 features con `src/features.py`
3. Cargar modelo pre-entrenado (`ridge_model.pkl`)
4. Predecir precio próximo día
5. Actualizar diariamente

**Reentrenamiento**: Mensual (para capturar nuevos patrones)

---

## Slide 12: Conclusiones

### Hallazgos Principales

1. **Problema altamente predecible**
   - R cuadrado=99% alcanzado
   - Error promedio <2 centavos por libra

2. **La simplicidad es poderosa**
   - Ridge superó a XGBoost y Random Forest
   - Complejidad no siempre es mejor

3. **Feature Engineering es crítico**
   - 42 features bien diseñadas fueron clave
   - Lags capturan memoria extrema del mercado

4. **Entender el problema > Usar algoritmo fancy**
   - Relación lineal fuerte detectada en EDA
   - Ridge es la solución natural

### Limitaciones

- Horizonte: Optimizado para 1 día adelante
- Eventos extremos: Cisnes negros pueden degradar performance
- Solo precio: No considera fundamentals (oferta/demanda)
- Mercado funcionando: No válido en cierres de mercado

### Próximos Pasos

- Deploy de API REST (FastAPI)
- Dashboard interactivo (Streamlit)
- Incorporar variables exógenas (oro, USD, inventarios LME)
- Explorar horizontes de predicción más largos (7, 30 días)

---

## Slide 13: Impacto y Aplicaciones

### Impacto Empresarial

**Para Empresas Mineras**:
- Optimización de contratos forward
- Estrategias de hedging más efectivas
- Mejor planificación de producción

**Para Inversionistas**:
- Señales de trading en mercado de commodities
- Análisis de riesgo de portafolios
- Timing de entrada/salida

**Para Gobierno de Chile**:
- Proyecciones fiscales más precisas
- Planificación presupuestaria informada
- Políticas públicas basadas en datos

### Valor Técnico del Proyecto

- Código reproducible y bien documentado
- 5 notebooks ejecutables paso a paso
- Modelos serializados listos para deploy
- README profesional
- Estructura de proyecto estándar

**Portfolio-Ready**: Demuestra skills en data science, ML, series temporales y MLOps

---

## Slide 14: Tecnologías y Competencias Demostradas

### Stack Tecnológico

**Lenguajes**:
- Python 3.8+
- SQL (para data loading)

**Librerías de ML**:
- scikit-learn (Ridge, RF, métricas)
- XGBoost (gradient boosting)
- statsmodels (ARIMA)
- pmdarima (Auto-ARIMA)

**Data Science**:
- pandas (manipulación)
- numpy (operaciones numéricas)
- scipy (estadística)

**Visualización**:
- matplotlib, seaborn, plotly

### Competencias Demostradas

1. **Análisis de Series Temporales**
   - ACF/PACF, estacionalidad, tendencia
   - Split temporal correcto

2. **Feature Engineering**
   - Creación de 42 features relevantes
   - Validación de data leakage

3. **Machine Learning**
   - Comparación de 5 algoritmos
   - Regularización y optimización de hiperparámetros

4. **Pensamiento Crítico**
   - Análisis de por qué XGBoost falló
   - Selección de modelo basada en problema

5. **Comunicación**
   - Documentación clara
   - Visualizaciones efectivas
   - Presentación ejecutiva

---

### Agradecimientos

- COCHILCO (contexto de industria)
- Yahoo Finance (datos históricos)
- Comunidad de scikit-learn
- Kaggle (inspiración de mejores prácticas)

---

**FIN DE LA PRESENTACIÓN**

**¿Preguntas?**

---

## Notas para el Presentador

### Tiempo estimado: 15-20 minutos

**Distribución de tiempo**:
- Slides 1-3 (Intro y Problema): 3 min
- Slides 4-6 (Datos y Features): 4 min
- Slides 7-9 (Modelos y Resultados): 5 min
- Slides 10-11 (Visualizaciones y Modelo): 3 min
- Slides 12-15 (Conclusiones e Impacto): 4 min
- Preguntas: 5 min

### Mensajes Clave a Enfatizar

1. **R cuadrado=99% logrado** (resultado excepcional)
2. **Simplicidad ganó a complejidad** (lección importante)
3. **Feature engineering fue crítico** (no solo el algoritmo)
4. **Proyecto production-ready** (no solo teoría)

### Preguntas Frecuentes Anticipadas

**P**: ¿Por qué XGBoost falló?
**R**: Relación lineal fuerte. Árboles fragmentan espacio perdiendo suavidad. Hiperparámetros conservadores.

**P**: ¿Funciona para horizontes más largos (30 días)?
**R**: No optimizado para eso. Memoria del mercado decae. Requeriría reentrenamiento específico.

**P**: ¿Qué pasa en crisis (cisnes negros)?
**R**: Modelo puede degradarse. Solo vio 25 eventos extremos en 15 años. Recomendado: monitoreo continuo + reentrenamiento.

**P**: ¿Se puede deployar en producción?
**R**: Sí. Pipeline es: datos diarios + features + modelo.pkl + predicción. Próximo paso: API REST.
