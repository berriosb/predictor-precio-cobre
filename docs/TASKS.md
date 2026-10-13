# TASKS - Predictor Precio Cobre Chile

Checklist de tareas para implementar el proyecto de predicción de precios del cobre.

**Referencia detallada:** Ver `intrucciones_preciocobre.md` y `claude.md`

---

## Progreso General
- [X] Fase 1: Setup completado ✓
- [ ] Fase 2: Datos obtenidos y explorados ← **AQUÍ ESTÁS**
- [ ] Fase 3: Features creados
- [ ] Fase 4: Modelos entrenados
- [ ] Fase 5: Evaluación completada
- [ ] Fase 6: Documentación lista
- [ ] Proyecto publicado

---

## FASE 1: Setup Inicial del Proyecto

### Configuración del Entorno
- [X] ~~Navegar a `predictor-precio-cobre/`~~
- [X] ~~Crear `requirements.txt` con dependencias~~
- [X] ~~Instalar dependencias: `pip install -r requirements.txt`~~
- [X] ~~Verificar instalación correcta~~

### Archivos de Configuración
- [X] ~~Crear `config.yaml` con parámetros del proyecto~~
- [X] ~~Crear `.gitignore` (ignorar data/, models/, __pycache__)~~
- [ ] Git: commit inicial

**Checkpoint:** ¿Navegas por todas las carpetas sin problemas? **✓ SÍ**

---

## FASE 2: Obtención y Exploración de Datos

### Módulo: `src/data_loader.py`
- [X] ~~Función `download_copper_yahoo()` - Descargar HG=F desde 2010~~
- [X] ~~Función `load_copper_data()` - Cargar y limpiar CSV~~
- [X] ~~Función `get_data_summary()` - Estadísticas básicas~~
- [X] ~~Probar el módulo~~

### Notebook 1: `01_descarga_datos.ipynb`
- [ ] **Ejecutar descarga de datos** ← SIGUIENTE PASO
- [ ] Mostrar df.head(), df.info(), df.describe()
- [ ] Verificar missing values
- [ ] Validar: 3000+ registros, rango 2010-2024

**Checkpoint:** ¿Tienes CSV con precio del cobre 2010-2024? **✗ NO (data/raw está vacío)**

### Notebook 2: `02_eda.ipynb`
- [ ] Gráfico: Serie temporal completa
- [ ] Gráfico: Distribución de precios
- [ ] Gráfico: Boxplot por año
- [ ] Gráfico: Estacionalidad mensual
- [ ] Gráfico: ACF/PACF (para ARIMA)
- [ ] Gráfico: Rolling statistics
- [ ] Identificar outliers y eventos extremos
- [ ] Escribir 5 insights clave en conclusiones
- [ ] Guardar gráficos en `reports/figures/`

**Checkpoint:** ¿Entiendes el comportamiento del precio en últimos 15 años? **✗ PENDIENTE**

---

## FASE 3: Feature Engineering

### Módulo: `src/features.py`
- [X] ~~`create_lag_features()` - Lags: [1, 2, 3, 7, 14, 30]~~
- [X] ~~`create_rolling_features()` - Ventanas: [7, 30, 90], stats: [mean, std, min, max]~~
- [X] ~~`create_temporal_features()` - year, month, day, dayofweek, quarter, flags~~
- [X] ~~`create_trend_features()` - price_diff, price_pct_change, volatility~~
- [X] ~~`create_all_features()` - Integrar todo + dropna~~
- [X] ~~`get_feature_correlation()` - Top N correlaciones~~
- [X] ~~Probar el módulo~~

### Notebook 3: `03_feature_engineering.ipynb`
- [ ] Cargar datos limpios
- [ ] Aplicar `create_all_features()`
- [ ] Heatmap de correlación (top 20)
- [ ] (Opcional) Calcular VIF para multicolinealidad
- [ ] Guardar `data/processed/precio_cobre_processed.csv`
- [ ] Documentar features más importantes

**Checkpoint:** ¿Tienes CSV con 20+ columnas de features? **✗ NO (data/processed vacío)**

---

## FASE 4: Modelado y Entrenamiento

### Módulo: `src/models.py`
- [X] ~~`split_data()` - Split temporal 80/10/10 (NO shuffle)~~
- [X] ~~`prepare_features_target()` - Separar X e y~~
- [X] ~~`train_linear_regression()` - Entrenar LR + métricas~~
- [X] ~~`train_arima()` - Entrenar ARIMA(5,1,2)~~
- [X] ~~`evaluate_model()` - Calcular MAE, RMSE, R², MAPE~~
- [X] ~~`save_model()` y `load_model()` - Persistencia~~
- [X] ~~Probar el módulo~~

### Notebook 4: `04_modelado.ipynb`
- [ ] Cargar datos procesados
- [ ] Split temporal (train/val/test)
- [ ] **Linear Regression:**
  - [ ] Entrenar modelo
  - [ ] Predicciones en test
  - [ ] Evaluar métricas
  - [ ] Guardar modelo
- [ ] **ARIMA:**
  - [ ] Entrenar modelo
  - [ ] Predicciones en test
  - [ ] Evaluar métricas
  - [ ] Guardar modelo
- [ ] Comparar modelos (tabla comparativa)
- [ ] Guardar mejor modelo como `best_model.pkl`
- [ ] Documentar cuál modelo ganó y por qué

**Checkpoint:** ¿Tienes métricas de ambos modelos en test set? **✗ NO (models/ vacío)**

---

## FASE 5: Evaluación y Visualización

### Módulo: `src/visualization.py`
- [X] ~~`plot_time_series()` - Gráfico de serie temporal~~
- [X] ~~`plot_predictions()` - Real vs predicción~~
- [X] ~~`plot_residuals()` - 3 subplots: scatter, histogram, Q-Q~~
- [X] ~~`compare_models()` - Barplot comparativo de métricas~~
- [X] ~~`plot_correlation_heatmap()` - Heatmap~~
- [X] ~~`plot_feature_importance()` - Barplot horizontal~~
- [X] ~~Probar el módulo~~

### Visualizaciones en Notebook 4
- [ ] Predicciones vs Real (LR y ARIMA)
- [ ] Análisis de residuales (LR y ARIMA)
- [ ] Comparación de modelos
- [ ] Feature importance
- [ ] Guardar todas en `reports/figures/`

### Conclusiones Finales
- [ ] ¿Qué modelo es mejor?
- [ ] ¿Se cumplen métricas objetivo (R² > 0.85, MAE < 0.15)?
- [ ] ¿Residuales son aleatorios?
- [ ] Limitaciones del modelo
- [ ] Horizonte temporal óptimo

**Checkpoint:** ¿Puedes explicar resultados a alguien no-técnico? **✗ PENDIENTE**

---

## FASE 6: Documentación y Limpieza

### README.md del Proyecto
- [X] ~~Descripción y contexto del proyecto~~
- [X] ~~Fuentes de datos (Yahoo Finance HG=F, COCHILCO)~~
- [X] ~~Estructura del proyecto (árbol de directorios)~~
- [X] ~~Instalación (clonar, instalar dependencias)~~
- [X] ~~Uso (cómo ejecutar notebooks 01-04)~~
- [ ] **Resultados (tabla de métricas + imágenes)** ← PENDIENTE
- [X] ~~Features utilizados~~
- [X] ~~Modelos implementados~~
- [X] ~~Próximos pasos~~
- [X] ~~Autor y contacto~~

### Limpieza de Código
- [ ] Verificar docstrings en todos los módulos
- [ ] Verificar type hints
- [ ] Eliminar código comentado
- [ ] Verificar NO hay emojis
- [ ] Verificar prints informativos

### Limpieza de Notebooks
- [ ] Celdas markdown explicativas
- [ ] Notebooks corren sin errores (Restart & Run All)
- [ ] Verificar NO hay emojis

### Git
- [ ] Verificar `.gitignore` funciona
- [ ] Commit final
- [ ] Push a GitHub
- [ ] (Opcional) Testing con pytest

**Checkpoint:** ¿Proyecto se ve profesional en GitHub? **✗ PENDIENTE**

---

## FASE 7: Mejoras Opcionales (Avanzado)

### Features Avanzados
- [ ] Indicadores técnicos: RSI, MACD, Bollinger Bands
- [ ] Features cíclicos: sin/cos de month, dayofweek
- [ ] Variables exógenas: USD Index, WTI, S&P 500, GDP China

### Modelos Adicionales
- [ ] XGBoost / LightGBM
- [ ] Prophet (Facebook)
- [ ] SARIMAX
- [ ] (Muy avanzado) LSTM / GRU

### Validación Mejorada
- [ ] TimeSeriesSplit (cross-validation temporal)
- [ ] Walk-forward validation
- [ ] Hyperparameter tuning (GridSearchCV, Optuna)
- [ ] Feature selection (RFE, VIF)

### Visualizaciones Impactantes
- [ ] Gráficos interactivos con Plotly
- [ ] Timeline de eventos (COVID, crisis 2008)
- [ ] Decomposición de serie temporal
- [ ] SHAP values (interpretabilidad)

### Deploy y Productionización
- [ ] API REST con FastAPI
- [ ] Dashboard con Streamlit
- [ ] Docker + deploy en Heroku/Cloud Run

### Portfolio-Ready
- [ ] README con badges
- [ ] Screenshots de resultados
- [ ] Sección "Desafíos Encontrados"
- [ ] Sección "Lecciones Aprendidas"
- [ ] Comparar vs baseline simple (naive forecast)

---

## CHECKLIST FINAL

### Criterios de "Proyecto Completado"
- [ ] Notebooks corren sin errores de principio a fin
- [ ] README completo con imágenes
- [ ] Código documentado (docstrings + type hints)
- [ ] Al menos 2 modelos con métricas
- [ ] Visualizaciones guardadas en `reports/figures/`
- [ ] Proyecto en GitHub
- [ ] Puedes explicar proyecto en 5 minutos
- [ ] Alguien más puede clonar y ejecutar

---

## Tips Rápidos

**Buenas Prácticas:**
- Commits frecuentes
- Restart & Run All antes de commitear notebooks
- Si copias código 2+ veces, crear función
- Magic numbers en config.yaml

**Errores Comunes a Evitar:**
- Data leakage
- Shuffle en series temporales
- No validar fuera de muestra
- Overfitting

**Cuando Estés Atascado:**
1. Volver al EDA
2. Simplificar
3. Documentación oficial
4. Google el error

---

**Próximo Proyecto:** Clasificador Riesgo Crediticio (Complejidad Media)

**Recuerda:** Mejor proyecto terminado al 80% que perfecto al 30%

---

## RESUMEN EJECUTIVO - ESTADO ACTUAL

###  LO QUE TIENES (Completado)

**Estructura del Proyecto:**
-  Carpetas creadas: `data/`, `src/`, `notebooks/`, `models/`, `reports/`
-  [config.yaml](predictor-precio-cobre/config.yaml) con parámetros configurados
-  [README.md](predictor-precio-cobre/README.md) completo y profesional

**Código Python (src/):**
-  [src/data_loader.py](predictor-precio-cobre/src/data_loader.py) - Funciones de descarga/carga
-  [src/features.py](predictor-precio-cobre/src/features.py) - Feature engineering completo
-  [src/models.py](predictor-precio-cobre/src/models.py) - LR y ARIMA listos
-  [src/visualization.py](predictor-precio-cobre/src/visualization.py) - 6 funciones de gráficos

**Notebooks Creados:**
-  [01_descarga_datos.ipynb](predictor-precio-cobre/notebooks/01_descarga_datos.ipynb)
-  [02_eda.ipynb](predictor-precio-cobre/notebooks/02_eda.ipynb)
-  [03_feature_engineering.ipynb](predictor-precio-cobre/notebooks/03_feature_engineering.ipynb)
-  [04_modelado.ipynb](predictor-precio-cobre/notebooks/04_modelado.ipynb)

###  LO QUE FALTA (Crítico)

1. **Datos:** `data/raw/` y `data/processed/` están vacíos
2. **Modelos:** `models/` está vacío
3. **Gráficos:** `reports/figures/` está vacío
4. **Notebooks SIN EJECUTAR:** Creados pero sin output

###  SIGUIENTE PASO INMEDIATO

**Ejecutar notebooks en orden:**
1. **[01_descarga_datos.ipynb](predictor-precio-cobre/notebooks/01_descarga_datos.ipynb)** ← **EMPIEZA AQUÍ**
   - Descarga datos de Yahoo Finance
   - Verifica que se cree `data/raw/precio_cobre_yahoo.csv`
2. **[02_eda.ipynb](predictor-precio-cobre/notebooks/02_eda.ipynb)**
   - Análisis exploratorio + gráficos
3. **[03_feature_engineering.ipynb](predictor-precio-cobre/notebooks/03_feature_engineering.ipynb)**
   - Crear features + guardar en `data/processed/`
4. **[04_modelado.ipynb](predictor-precio-cobre/notebooks/04_modelado.ipynb)**
   - Entrenar modelos + evaluar + guardar en `models/`

###  Progreso Visual

```
FASE 1: Setup               [██████████] 100% ✓
FASE 2: Datos/EDA           [██░░░░░░░░]  20% (módulos listos, notebooks sin ejecutar)
FASE 3: Features            [████░░░░░░]  40% (módulos listos, notebooks sin ejecutar)
FASE 4: Modelado            [████░░░░░░]  40% (módulos listos, notebooks sin ejecutar)
FASE 5: Evaluación          [███░░░░░░░]  30% (módulos listos, notebooks sin ejecutar)
FASE 6: Documentación       [███████░░░]  70% (README listo, falta ejecutar notebooks)

PROGRESO TOTAL:             [█████░░░░░]  50%
```

### ⚠️ BLOQUEADORES ACTUALES

- **Sin datos:** No puedes entrenar ni evaluar hasta ejecutar notebook 01
- **Notebooks sin ejecutar:** No hay evidencia de que funciona
