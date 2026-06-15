# Predictor de Precio del Cobre

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9.0-orange.svg)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Completed-success.svg)]()

> Sistema de Machine Learning para predecir el precio diario del cobre (USD/lb) usando 15+ años de datos de Yahoo Finance, 29 features de series temporales, y un modelo Ridge Regression. Walk-forward validation con 5 ventanas anuales (2020-2024) confirma robustez fuera de muestra: R² promedio **0.957**, MAPE **1.16%**.

![Serie historica del precio del cobre](reports/figures/01_price_history.png)

## Resultados principales

| Ventana (test) | MAE (USD/lb) | RMSE (USD/lb) | R²     | MAPE  |
|----------------|--------------|---------------|--------|-------|
| 2020           | $0.030       | $0.039        | 0.989  | 1.08% |
| 2021           | $0.054       | $0.071        | 0.938  | 1.25% |
| 2022           | $0.054       | $0.071        | 0.978  | 1.36% |
| 2023           | $0.038       | $0.049        | 0.927  | 0.99% |
| 2024           | $0.047       | $0.064        | 0.955  | 1.10% |
| **Promedio**   | **$0.045**   | **$0.059**    | **0.957** | **1.16%** |

El modelo se mantiene sobre **R²=0.92 en todas las ventanas**, incluyendo el periodo 2022 (shock de la guerra en Ucrania). Esto valida que el modelo no está sobreajustado al periodo 2010-2019.

## Por que importa este proyecto

Chile es el mayor productor de cobre del mundo (~28% de la producción global). El precio del cobre es un indicador macro que mueve presupuestos fiscales, decisiones CAPEX mineras, y estrategias de cobertura. Un modelo con error MAPE ~1% es útil para:
- Pronóstico de ingresos a corto plazo (1 día adelante)
- Backtesting de estrategias de cobertura
- Análisis de sensibilidad ante shocks de oferta

## El modelo en accion (app Streamlit)

La aplicación carga el modelo Ridge entrenado y permite explorar predicciones sobre la serie completa. Para correrla localmente:

```bash
git clone https://github.com/berriosb/predictor-precio-cobre.git
cd predictor-precio-cobre/predictor-precio-cobre
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Estructura del repositorio

```
predictor-precio-cobre/
├── app.py                        # App Streamlit
├── config.yaml                   # Configuracion centralizada
├── data/
│   ├── raw/precio_cobre_yahoo.csv       # 4,137 registros (2010-2026) desde Yahoo Finance
│   └── processed/precio_cobre_features.csv  # CSV con las 29 features
├── models/                       # Modelos entrenados (.pkl)
│   ├── ridge_model.pkl           # Modelo en produccion
│   ├── linear_regression.pkl     # Baseline de referencia
│   └── results_summary.json      # Metricas de reentrenamiento
├── notebooks/
│   ├── 01_descarga_datos.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_modelado.ipynb
│   ├── 05_modelado_avanzado.ipynb
│   └── 06_walk_forward_validation.py   # Validacion walk-forward (nuevo)
├── reports/
│   ├── figures/                  # Graficos generados
│   └── walk_forward_results.csv  # Tabla de las 5 ventanas
└── src/
    ├── data_loader.py
    ├── download_raw.py           # Re-descarga datos crudos
    ├── features.py
    ├── models.py
    ├── retrain.py                # Pipeline de reentrenamiento
    └── regenerate_figures.py     # Regenera plots
```

## Metodologia

### Datos
- **Fuente:** Yahoo Finance (ticker `HG=F`, Copper Futures)
- **Periodo:** 2010-01-04 a 2026-06-15 (4,137 registros)
- **Sin valores nulos, ordenamiento cronologico**

### Feature engineering (29 features en 5 grupos)
1. **Temporales (7):** year, month, day, dayofweek, quarter, is_month_start, is_month_end
2. **Lags (6):** precio de hace 1, 2, 3, 7, 14, 30 dias
3. **Rolling statistics (12):** mean, std, min, max en ventanas de 7, 30, 90 dias
4. **Tendencia (2):** price_diff, price_pct_change
5. **Volatilidad (2):** volatilidad 7d y 30d

**Importante:** todas las features se calculan con `shift(1)` para evitar data leakage — el modelo nunca ve el precio del dia T al predecir T.

### Por que Ridge Regression (y no XGBoost o Random Forest)

| Modelo              | R² test | MAE test | Tiempo entrenamiento |
|---------------------|---------|----------|----------------------|
| **Ridge alpha=0.1** | 0.9704  | $0.0732  | < 1s                 |
| Linear Regression   | 0.9702  | $0.0737  | < 1s                 |
| XGBoost             | 0.66    | $0.092   | ~30s                 |
| Random Forest       | 0.68    | $0.088   | ~10s                 |

XGBoost y Random Forest fueron probados (notebook 05) y quedaron muy por debajo: la relacion entre el precio del cobre y sus lags es **casi perfectamente lineal** (correlacion lag_1 = 0.998), por lo que un modelo simple con regularizacion captura mejor la dinamica. Ridge maneja la multicolinealidad entre lags (0.99+ entre si) sin perder explicacion.

![Comparacion de modelos](reports/figures/03_model_comparison.png)

### El factor lag_1: por que el mercado es tan predecible a corto plazo

![Scatter lag_1 vs target](reports/figures/02_lag1_scatter.png)

El precio de ayer (lag_1) tiene correlacion **0.998** con el precio de hoy. Esto es lo que en series temporales se llama "memoria extrema del mercado": el cobre no da saltos grandes de un dia para otro (salvo crisis), por lo que el valor de ayer es casi una prediccion perfecta de hoy. Ridge aprende a ponderar lag_1 fuertemente y a usar el resto de las features para corregir la pequena fraccion de varianza residual.

### Predicciones vs realidad (ultimos 120 dias del test set)

![Predicciones vs realidad](reports/figures/04_predictions_vs_actual.png)

Las predicciones (rojo y azul punteado) se superponen a la realidad (negro solido) en escala diaria. La diferencia es invisible a simple vista en regimenes normales — solo se nota en los picos.

## Walk-forward validation (5 ventanas anuales)

Para validar que el modelo no esta sobreajustado al periodo 2010-2019, lo reentreno en 5 ventanas anuales consecutivas y mido error en cada una:

![Walk-forward metrics](reports/figures/05_walk_forward_metrics.png)

**Lectura:** R² se mantiene entre 0.93 y 0.99 incluso en 2022 (guerra Ucrania), confirmando que el modelo es robusto fuera de muestra. La ventana con peor performance (2023, R²=0.927) coincide con un periodo de transicion en el mercado chino que el modelo no anticipa. Ver `notebooks/06_walk_forward_validation.py` para los detalles.

## Reproducibilidad

```bash
# 1. Descargar datos crudos
python src/download_raw.py

# 2. Reentrenar modelo (regenera features + .pkl)
python src/retrain.py

# 3. Regenerar figuras
python src/regenerate_figures.py

# 4. Correr walk-forward validation
python notebooks/06_walk_forward_validation.py

# 5. Lanzar la app
streamlit run app.py
```

Todo el pipeline es ejecutable con `pip install -r requirements.txt`. Version de sklearn usada: **1.9.0**.

## Limitaciones conocidas

- **Horizonte de prediccion:** optimizado para 1 dia adelante. Predicciones a 5-30 dias degradan rapidamente.
- **Eventos extremos:** crisis geopoliticas o financieras no vistas pueden degradar el R² a <0.80. El walk-forward muestra la ventana 2022 como la peor, pero se mantiene sobre 0.92.
- **Datos univariados:** solo usa la serie historica del precio. Incorporar variables exogenas (precio del oro, USD index, inventarios LME) es la siguiente iteracion.
- **Mercado cerrado:** no genera predicciones validas en dias sin cotizacion (fines de semana, feriados).

## Tecnologias

- **Python 3.11**, **scikit-learn 1.9.0**, **pandas 2.x**, **numpy**
- **Streamlit 1.58** para la app web
- **yfinance** como fuente de datos
- **matplotlib** + **seaborn** para visualizacion

## Autor

**Bastian Berrios** — Ingeniero Civil Industrial, en transicion hacia Data/ML.
GitHub: [@berriosb](https://github.com/berriosb)
