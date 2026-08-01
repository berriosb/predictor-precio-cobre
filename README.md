# Predictor de Precio del Cobre

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.9-orange.svg)](https://scikit-learn.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000?logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **Demo editorial en vivo:** [web-theta-teal-22.vercel.app](https://web-theta-teal-22.vercel.app) — *Predecir menos. Demostrar más.*

Sistema de Machine Learning para predecir el precio diario del cobre (USD/lb) mediante series temporales, feature engineering y validación walk-forward, con un dashboard Next.js que comunica los resultados con honestidad analítica.

---

## Lectura de 5 segundos

- **Dataset**: 4.137 cierres diarios del futuro `HG=F` (Yahoo Finance), mayo 2010 — junio 2026.
- **Modelo**: Ridge Regression α=0.1 sobre 29 features (lags, rolling stats, calendario, tendencia).
- **Resultado walk-forward** (2020—2024): R² promedio **0.957**, MAPE **1.16%**.
- **Hallazgo honesto**: Ridge gana en **2 de 5 ventanas**. La persistencia naïve gana **3 de 5**. Un R² alto refleja la persistencia extrema de la serie, no una ventaja predictiva del modelo.

El dashboard publica el benchmark completo con baseline naïve explícito en lugar de inflar el resultado con claims multi-step no validados.

---

## Tabla de Contenidos

- [Demo Interactiva](#demo-interactiva)
- [Resumen Ejecutivo](#resumen-ejecutivo)
- [Resultados Destacados](#resultados-destacados)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Uso](#uso)
- [Metodología](#metodología)
- [Limitaciones Conocidas](#limitaciones-conocidas)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Autor](#autor)
- [Licencia](#licencia)

---

## Demo Interactiva

**[Abrir el dashboard editorial](https://web-theta-teal-22.vercel.app)**

Incluye:

- Hero "Predecir menos. Demostrar más." con la narrativa del proyecto.
- 4 KPIs reales: último cierre, R² walk-forward, MAPE y comparativa Ridge vs naïve.
- Serie histórica interactiva del cobre desde 2010 con rangos `2A / 5A / 10A / Todo` y eventos COVID-19 / Guerra de Ucrania anotados.
- Comparación MAE por ventana con etiquetas `Ridge` / `Naïve`.
- Hallazgo principal: el baseline naïve gana más veces.
- Metodología en 5 pasos y sección de limitaciones explícitas.

La web consume datos versionados del pipeline ML exportados vía `scripts/export_web_data.py`.

---

## Resumen Ejecutivo

**Objetivo**: predecir el precio diario del cobre (USD/lb) y publicar el benchmark con honestidad analítica.

**Resultado principal**: modelo Ridge reproducible, validación walk-forward de 5 ventanas, R² promedio 0.957, MAPE 1.16%, sin forecast multi-step inventado.

**Dataset**: 4.137 cierres diarios, mayo 2010 — junio 2026, ticker `HG=F` (Yahoo Finance).

**Postura analítica**: el proyecto compara contra persistencia naïve y muestra cuándo el modelo aporta valor real y cuándo no.

---

## Resultados Destacados

### Walk-forward 2020—2024 (out-of-sample)

| Año  | Ridge MAE | Naïve MAE | R²    | MAPE  | ¿Gana Ridge? |
|------|-----------|-----------|-------|-------|---------------|
| 2020 | 0.0298    | 0.0291    | 0.989 | 1.08% | ❌            |
| 2021 | 0.0535    | 0.0544    | 0.938 | 1.25% | ✅            |
| 2022 | 0.0542    | 0.0541    | 0.978 | 1.36% | ❌            |
| 2023 | 0.0381    | 0.0386    | 0.927 | 0.99% | ✅            |
| 2024 | 0.0474    | 0.0462    | 0.955 | 1.10% | ❌            |
| **Promedio** | **0.0466** | **0.0465** | **0.957** | **1.16%** | **2 / 5** |

### Insights Clave

1. **La simplicidad gana por escaso margen**: Ridge apenas empata con un modelo que predice `precio(t+1) = precio(t)`. La diferencia está dentro del ruido.
2. **La persistencia del cobre es extrema**: `lag_1` explica ~99.6% de la varianza diaria. Eso vuelve casi cualquier modelo competitivo.
3. **Honestidad metodológica > métricas infladas**: el benchmark muestra cuándo Ridge pierde y cuándo gana. No se publican intervalos "95%" sin calibración ni horizontes multi-step no validados.
4. **Feature engineering importa**: lags + rolling stats con `shift(1)` para evitar leakage y TimeSeriesSplit para seleccionar α.

---

## Estructura del Proyecto

```
predictor-precio-cobre/
│
├── data/
│   ├── raw/                          # Datos descargados de Yahoo Finance (gitignored)
│   └── processed/                    # Features generadas (gitignored)
│       └── precio_cobre_features.csv
│
├── docs/                             # Documentación interna
│
├── models/                           # Artefactos del modelo (gitignored)
│   └── results_summary.json         # Métricas vigentes (incluidas)
│
├── notebooks/                        # Análisis exploratorio
│   └── 06_walk_forward_validation.py
│
├── reports/
│   ├── walk_forward_results.csv     # Métricas por ventana (incluido)
│   └── figures/                      # Gráficos PNG generados
│
├── scripts/
│   └── export_web_data.py            # Exporter read-only a JSON para la web
│
├── src/                              # Pipeline ML
│   ├── data_loader.py
│   ├── download_raw.py
│   ├── features.py
│   ├── models.py
│   ├── retrain.py
│   ├── visualization.py
│   └── regenerate_figures.py
│
├── web/                              # Dashboard Next.js 15 (editorial, static export)
│   ├── src/
│   │   ├── app/                      # Layout, page, globals.css
│   │   ├── components/               # Dashboard.tsx, PriceChart.tsx
│   │   ├── data/dashboard.json       # Generado por scripts/export_web_data.py
│   │   └── lib/                      # Helpers + tests vitest
│   ├── package.json
│   └── README.md
│
├── predictor-precio-cobre/           # Workspace interno del pipeline
│   ├── app.py                        # App Streamlit heredada
│   ├── src/                          # Módulos espejo
│   ├── data/                         # Datos cacheados
│   ├── models/                       # Modelos entrenados
│   ├── notebooks/                    # Notebooks históricos
│   └── reports/figures/              # PNGs ya generados
│
├── config.yaml                       # Parámetros del pipeline
├── requirements.txt                  # Dependencias runtime Python
├── vercel.json                       # Config de deploy Vercel
├── LICENSE                           # MIT
└── README.md                         # Este archivo
```

---

## Instalación

```bash
# 1. Clonar e instalar dependencias Python
git clone https://github.com/berriosb/predictor-precio-cobre.git
cd predictor-precio-cobre
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Instalar dependencias del dashboard
cd web
pnpm install --frozen-lockfile
cd ..
```

## Uso

### Pipeline ML local

```bash
# Descargar datos crudos desde Yahoo Finance
python3 src/download_raw.py

# Regenerar features y modelos
python3 src/retrain.py

# Ejecutar validación walk-forward
python3 notebooks/06_walk_forward_validation.py

# Regenerar figuras PNG
python3 src/regenerate_figures.py
```

### Dashboard editorial local

```bash
cd web

# Exportar datos del pipeline a JSON consumido por la web
pnpm data:export

# Levantar servidor de desarrollo
pnpm dev          # http://localhost:3000

# Verificación completa
pnpm lint
pnpm typecheck
pnpm test
pnpm build        # genera web/out/ (sitio estático)
```

---

## Metodología

1. **Datos** — 4.137 cierres diarios de `HG=F` desde Yahoo Finance, ordenados cronológicamente.
2. **Features** — 29 variables:
   - 6 lags (1, 2, 3, 7, 14, 30 días)
   - 12 rolling stats (medias, std, min, max para ventanas 7, 30, 90)
   - 7 features de calendario (year, month, day, dayofweek, quarter, is_month_start, is_month_end)
   - 4 features de tendencia (price_diff, price_pct_change, volatility_7d, volatility_30d)
   - Todas con `shift(1)` para evitar leakage.
3. **Modelo** — Ridge Regression con `TimeSeriesSplit(5)` y grid search sobre α ∈ {0.001, 0.01, 0.1, 1, 10, 100}. Mejor α = 0.1.
4. **Validación** — Walk-forward expansivo de 5 ventanas anuales (2020 → 2024). Cada ventana reentrena con toda la historia hasta fin del año anterior y evalúa sobre ese año.
5. **Baseline** — Persistencia naïve: `precio(t+1) = precio(t)`. Es la referencia mínima y la métrica más honesta del proyecto.

---

## Limitaciones Conocidas

- **Solo horizonte 1 día.** El dashboard no publica forecasts multi-step porque las features recursivas degradan fuera de distribución y los horizontes 5/14/30 días no fueron validados con targets directos.
- **Sin variables exógenas.** No se incorporan DXY, inventarios LME, oro, tasas ni China PMI. La siguiente iteración exploraría un modelo con `GC=F` y `DX-Y.NYB`.
- **R² alto ≠ valor predictivo.** La persistencia del cobre explica la mayor parte de la varianza. El verdadero aporte del modelo es marginal sobre una persistencia naïve.
- **Intervalos no calibrados.** No se publican bandas de confianza tipo "95%" porque no hay cobertura empírica validada sobre residuos walk-forward.
- **Datos válidos hasta 15 jun 2026.** Para producción real, regenerar `data/processed/precio_cobre_features.csv` y volver a entrenar antes de confiar en cualquier predicción.

---

## Tecnologías Utilizadas

**Machine Learning**: Python 3.11, pandas, numpy, scikit-learn, statsmodels, matplotlib, seaborn, yfinance.

**Dashboard**: Next.js 15, React 19, TypeScript (strict), SVG propio (sin librerías de charts), DM Mono + Manrope + Newsreader, Vitest, ESLint flat config.

**Deployment**: Vercel (static export desde `web/out/`).

---

## Autor

**Bastian Nicolas Berrios Alarcon** — Analista de Datos en búsqueda activa, Chile.

- GitHub: [@berriosb](https://github.com/berriosb)
- LinkedIn: /in/bastian-berrios
- Email: berriosbastian@gmail.com

---

## Licencia

MIT — ver [LICENSE](LICENSE).
