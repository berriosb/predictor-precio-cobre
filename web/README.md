# Cobre / Forecast Lab — Web

Dashboard editorial estático construido con Next.js 15 y datos exportados desde los artefactos versionados del modelo.

## Desarrollo

```bash
cd web
pnpm install
pnpm data:export
pnpm dev
```

## Verificación

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

`pnpm build` regenera `src/data/dashboard.json` mediante `../scripts/export_web_data.py` y produce una exportación estática en `out/`.

## Fuente de datos

- `../predictor-precio-cobre/data/processed/precio_cobre_features.csv`
- `../predictor-precio-cobre/reports/walk_forward_results.csv`
- `../predictor-precio-cobre/models/results_summary.json`

La interfaz no ejecuta el modelo en runtime ni ofrece forecasts multi-step. Comunica el benchmark de un día y la comparación Ridge vs persistencia naïve.
