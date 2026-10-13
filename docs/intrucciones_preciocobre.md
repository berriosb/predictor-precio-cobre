##  CONTEXTO Y OBJETIVO

Necesito que me ayudes a crear **desde cero** un proyecto completo de Machine Learning para predecir el precio del cobre chileno. Este es el **Proyecto #1** de mi portfolio de 30 proyectos ML/DL, y es el más simple para empezar a construir experiencia.

### ¿Por qué este proyecto?
- **Relevancia empresarial:** Chile es el mayor productor de cobre del mundo. Las empresas mineras necesitan predecir precios para planificar presupuestos, hacer cobertura de riesgo financiero y tomar decisiones de inversión.
- **Complejidad:**  Fácil - Ideal para comenzar con series temporales
- **Datos públicos:** Disponibles en COCHILCO (Comisión Chilena del Cobre) y Yahoo Finance

---

##  CONCEPTO DEL MODELO

### Problema de Negocio
**Pregunta clave:** ¿Cuál será el precio del cobre mañana/la próxima semana/el próximo mes?

**Variables de entrada:**
1. **Precio histórico del cobre** (principal variable)
2. **Tendencia temporal:** ¿El precio está subiendo o bajando?
3. **Estacionalidad:** ¿Hay patrones que se repiten en ciertos meses/trimestres?
4. **Promedios móviles:** Media de los últimos 7, 30, 90 días
5. **Volatilidad:** ¿Qué tan variable ha sido el precio recientemente?

### Enfoque Técnico
Vamos a usar **dos modelos complementarios:**

1. **Linear Regression (Baseline):**
   - Modelo simple para tener una referencia
   - Usa features engineered (lags, rolling stats)
   - Fácil de interpretar

2. **ARIMA (AutoRegressive Integrated Moving Average):**
   - Modelo especializado en series temporales
   - Captura tendencia y estacionalidad automáticamente
   - Es el estándar en la industria para este tipo de datos

### Pipeline del Proyecto
```
Datos brutos → Feature Engineering → Split Train/Val/Test → 
→ Entrenar modelos → Evaluar → Comparar → Seleccionar mejor → Deploy
```

---

##  ESTRUCTURA DEL PROYECTO QUE DEBES CREAR

Genera la siguiente estructura de carpetas y archivos:

```
predictor-precio-cobre/
├── data/
│   ├── raw/                    # CSV/Excel descargados de fuentes
│   └── processed/              # Datos con features creados
│
├── notebooks/                  # Jupyter Notebooks para exploración
│   ├── 01_descarga_datos.ipynb        # Obtener datos de Yahoo Finance
│   ├── 02_eda.ipynb                   # Análisis exploratorio visual
│   ├── 03_feature_engineering.ipynb   # Crear variables predictoras
│   └── 04_modelado.ipynb              # Entrenar y evaluar modelos
│
├── src/                        # Código Python reutilizable
│   ├── __init__.py
│   ├── data_loader.py          # Funciones para descargar/cargar datos
│   ├── features.py             # Lógica de feature engineering
│   ├── models.py               # Entrenamiento de modelos
│   └── visualization.py        # Gráficos estandarizados
│
├── models/                     # Modelos .pkl entrenados
│   └── .gitkeep
│
├── reports/
│   └── figures/                # Gráficos PNG para documentación
│       └── .gitkeep
│
├── .gitignore                  # Ignorar data/, models/, __pycache__
├── requirements.txt            # Dependencias Python
├── config.yaml                 # Parámetros configurables del proyecto
└── README.md                   # Documentación completa del proyecto
```

---

##  ARCHIVOS CLAVE A GENERAR

###  `requirements.txt`
Lista todas las librerías necesarias con versiones específicas:
- **pandas, numpy:** Manipulación de datos
- **scikit-learn:** Regresión lineal y métricas
- **statsmodels:** Modelo ARIMA
- **matplotlib, seaborn, plotly:** Visualizaciones
- **yfinance:** Descargar datos de Yahoo Finance (alternativa a COCHILCO)
- **pyyaml:** Leer configuración
- **jupyter:** Para notebooks interactivos

###  `config.yaml`
Archivo de configuración centralizado con:
- URLs de fuentes de datos
- Rutas de carpetas
- Parámetros de features (lags: [1,2,3,7,14,30], ventanas rolling: [7,30,90])
- Configuración de modelos (orden ARIMA: p=5, d=1, q=2)
- Splits de datos (80% train, 10% val, 10% test)

###  `src/data_loader.py`
Módulo para obtener datos. Debe incluir:

**Función principal:** `download_copper_yahoo(start_date, end_date)`
- Usa librería `yfinance` para descargar precio del cobre (ticker: HG=F)
- Descarga desde 2010-01-01 hasta hoy
- Retorna DataFrame con columnas: ['fecha', 'precio_cobre_usd_lb']
- Guarda en `data/raw/precio_cobre_yahoo.csv`

**Función auxiliar:** `load_copper_data(source='yahoo')`
- Carga datos ya descargados
- Parsea fechas correctamente
- Elimina valores nulos
- Ordena cronológicamente

**Alternativa:** Instrucciones para descarga manual desde COCHILCO si Yahoo Finance falla.

###  `src/features.py`
Módulo de Feature Engineering. Implementa:

**a) Lags (valores pasados):**
```python
create_lag_features(df, lags=[1, 2, 3, 7, 14, 30])
```
- Crea columnas: `lag_1`, `lag_2`, ..., `lag_30`
- Ejemplo: `lag_1` es el precio de ayer, `lag_7` de hace una semana

**b) Promedios móviles (Rolling Statistics):**
```python
create_rolling_features(df, windows=[7, 30, 90])
```
- Crea: `rolling_mean_7`, `rolling_std_7`, `rolling_min_7`, `rolling_max_7`
- Lo mismo para ventanas de 30 y 90 días
- Captura tendencias de corto, mediano y largo plazo

**c) Features temporales:**
```python
create_temporal_features(df)
```
- Extrae: `year`, `month`, `day`, `dayofweek`, `quarter`
- `is_month_start`, `is_month_end` (binarios)
- Captura estacionalidad

**d) Features de tendencia:**
```python
create_trend_features(df)
```
- `price_diff`: Cambio día a día (precio_hoy - precio_ayer)
- `price_pct_change`: Retorno porcentual (%)
- `volatility_7d`, `volatility_30d`: Desviación estándar de retornos

**Función integradora:** `create_all_features(df, config)`
- Aplica todas las transformaciones en secuencia
- Elimina filas con NaN (resultado de lags y rolling)
- Retorna DataFrame listo para modelado

###  `src/models.py`
Módulo de modelado. Incluye:

**a) Split temporal de datos:**
```python
split_data(df, train_size=0.8, val_size=0.1)
```
- **Importante:** En series temporales NO se hace shuffle
- Split cronológico: primeros 80% train, siguientes 10% val, últimos 10% test
- Retorna 3 DataFrames separados

**b) Modelo 1 - Linear Regression:**
```python
train_linear_regression(X_train, y_train, X_val, y_val)
```
- X = todas las features creadas
- y = precio del cobre (target)
- Retorna modelo entrenado + métricas (MAE, RMSE, R²)

**c) Modelo 2 - ARIMA:**
```python
train_arima(train_series, order=(5,1,2))
```
- Solo usa la serie temporal del precio (sin features adicionales)
- order=(p,d,q): 
  - p=5: Usa últimos 5 valores (autorregresivo)
  - d=1: Diferenciación de primer orden (para estacionariedad)
  - q=2: Media móvil de últimos 2 errores
- Retorna modelo ARIMA ajustado

**d) Evaluación:**
```python
evaluate_model(y_true, y_pred, model_name)
```
- Calcula métricas:
  - **MAE** (Mean Absolute Error): Error promedio en dólares
  - **RMSE** (Root Mean Squared Error): Penaliza errores grandes
  - **R²** (R-squared): % de varianza explicada (0-1)
  - **MAPE** (Mean Absolute Percentage Error): Error porcentual

**e) Persistencia:**
- `save_model(model, filename)`: Guarda con joblib
- `load_model(filename)`: Carga modelo entrenado

###  `src/visualization.py`
Funciones de visualización estandarizadas:

**a) Gráfico de serie temporal:**
```python
plot_time_series(df, title="Precio del Cobre 2010-2024")
```
- Línea de tiempo con precio
- Resalta tendencias y anomalías

**b) Gráfico de predicciones vs reales:**
```python
plot_predictions(y_true, y_pred, dates, model_name)
```
- Dos líneas: real (azul) vs predicción (naranja)
- Incluye banda de confianza

**c) Distribución de errores:**
```python
plot_residuals(y_true, y_pred)
```
- Histograma de errores
- Gráfico Q-Q para verificar normalidad

**d) Comparación de modelos:**
```python
compare_models(metrics_dict)
```
- Gráfico de barras con MAE, RMSE de cada modelo

###  `README.md`
Documentación completa con:
- **Descripción del proyecto:** Qué hace, por qué es útil
- **Fuentes de datos:** Links a COCHILCO y Yahoo Finance
- **Instalación:** Cómo clonar y setup
- **Uso:** Cómo ejecutar notebooks paso a paso
- **Resultados:** Tabla con métricas de cada modelo
- **Próximos pasos:** Mejoras futuras (agregar variables exógenas, probar más modelos)

###  `.gitignore`
Ignorar:
```
data/
models/*.pkl
__pycache__/
.ipynb_checkpoints/
*.pyc
.DS_Store
```

---

##  NOTEBOOKS - FLUJO DE TRABAJO

### Notebook 1: `01_descarga_datos.ipynb`
**Objetivo:** Obtener datos y guardarlos

```markdown
# Celdas del notebook:

1. Importar librerías
2. Ejecutar: download_copper_yahoo(start_date='2010-01-01')
3. Cargar datos: df = load_copper_data()
4. Mostrar primeras filas: df.head()
5. Info básica: df.info(), df.describe()
6. Verificar missing values: df.isnull().sum()
```

### Notebook 2: `02_eda.ipynb`
**Objetivo:** Explorar datos visualmente

```markdown
# Análisis exploratorio:

1. Gráfico de serie temporal completa (2010-2024)
2. Distribución de precios (histograma)
3. Boxplot por año para ver tendencia
4. Análisis de estacionalidad (precio promedio por mes)
5. Autocorrelación (ACF/PACF plots) - ayuda a determinar orden ARIMA
6. Rolling statistics (media y std móviles)
7. Identificar outliers y eventos extremos
```

### Notebook 3: `03_feature_engineering.ipynb`
**Objetivo:** Crear variables predictoras

```markdown
# Transformaciones:

1. Cargar datos limpios
2. Aplicar create_all_features(df, config)
3. Visualizar correlación entre features (heatmap)
4. Análisis de importancia de features (preliminar)
5. Verificar multicolinealidad (VIF)
6. Guardar dataset con features: precio_cobre_processed.csv
```

### Notebook 4: `04_modelado.ipynb`
**Objetivo:** Entrenar, evaluar y comparar modelos

```markdown
# Pipeline de modelado:

1. Cargar datos procesados
2. Split temporal (train/val/test)
3. Entrenar Linear Regression
   - Mostrar coeficientes de features más importantes
4. Entrenar ARIMA
   - Mostrar diagnóstico de residuales
5. Predicciones en test set para ambos modelos
6. Calcular métricas (MAE, RMSE, R², MAPE)
7. Gráfico de comparación: real vs predicciones
8. Análisis de errores (residuals)
9. Conclusión: ¿Qué modelo es mejor? ¿Por qué?
10. Guardar mejor modelo en models/
```

---

##  MÉTRICAS DE ÉXITO ESPERADAS

Para este proyecto simple, se espera:

- **Linear Regression:**
  - R² entre 0.85-0.92 (explica 85-92% de varianza)
  - MAE < $0.15 USD/lb
  - RMSE < $0.20 USD/lb

- **ARIMA:**
  - Similar o ligeramente mejor que Linear Regression
  - Mejor captura de tendencias a corto plazo

**Conclusión esperada:** Ambos modelos funcionan razonablemente bien para predicciones de corto plazo (1-7 días). Para horizontes más largos, se necesitarían variables exógenas (demanda China, inventarios, GDP mundial, etc.).

---

##  INSTRUCCIONES ESPECÍFICAS PARA CLAUDE CODE

**Por favor, genera:**

1.  Toda la estructura de carpetas descrita arriba
2.  Todos los archivos `.py` en `src/` con código completo y documentado
3.  Los 4 notebooks `.ipynb` con celdas de markdown explicativas y código
4.  `requirements.txt` con todas las dependencias
5.  `config.yaml` con parámetros configurables
6.  `README.md` profesional y completo
7.  `.gitignore` apropiado

**Estilo de código:**
- Docstrings en todas las funciones (Google style)
- Type hints donde sea apropiado
- Nombres de variables en español para contexto chileno
- Comentarios explicativos en secciones complejas
- Prints informativos para tracking de progreso

**Importante:**
- El código debe ser **ejecutable inmediatamente** después de `pip install -r requirements.txt`
- Usa `yfinance` como fuente principal de datos (más confiable que scraping COCHILCO)
- Incluye manejo de errores básico (try/except)
- Los notebooks deben ser auto-explicativos para alguien que aprende ML

---

##  CONTEXTO ADICIONAL

Este es mi primer proyecto serio de ML. Quiero que sea:
-  **Profesional:** Como para mostrar en entrevistas
-  **Educativo:** Con explicaciones claras de cada paso
-  **Reproducible:** Cualquiera debe poder clonar y ejecutar
-  **Extensible:** Fácil agregar más features o modelos después

Una vez terminado, seguiré con proyectos más complejos del roadmap (clasificación de riesgo crediticio, detección de anomalías, etc.).

---