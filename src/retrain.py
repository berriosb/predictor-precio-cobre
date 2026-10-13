"""
Reentrena el modelo Ridge con los datos crudos + features regeneradas,
y persiste el .pkl compatible con la sklearn instalada.

Uso:
    python src/retrain.py

Salida:
    - models/ridge_model.pkl     (sobreescrito)
    - models/linear_regression.pkl
    - models/feature_names.pkl
    - data/processed/precio_cobre_features.csv (sobreescrito)
    - models/results_summary.json
"""
import json
import pickle
import sys
import warnings
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

warnings.filterwarnings("ignore")

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.features import create_all_features  # noqa: E402


# --- Config -----------------------------------------------------------------
RAW_CSV = BASE / "data" / "raw" / "precio_cobre_yahoo.csv"
PROC_CSV = BASE / "data" / "processed" / "precio_cobre_features.csv"
MODELS_DIR = BASE / "models"

RIDGE_PATH = MODELS_DIR / "ridge_model.pkl"
LR_PATH = MODELS_DIR / "linear_regression.pkl"
FEATS_PATH = MODELS_DIR / "feature_names.pkl"
SUMMARY_PATH = MODELS_DIR / "results_summary.json"


def load_raw() -> pd.DataFrame:
    if not RAW_CSV.exists():
        raise FileNotFoundError(
            f"No existe {RAW_CSV}. Ejecuta primero: python src/download_raw.py"
        )
    df = pd.read_csv(RAW_CSV)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def build_features(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Reusamos el modulo existente para mantener consistencia con los notebooks
    return create_all_features(df_raw, config_path=str(BASE / "config.yaml"))


def temporal_split(df: pd.DataFrame, train=0.8, val=0.1, test=0.1):
    assert abs(train + val + test - 1.0) < 1e-6
    n = len(df)
    a = int(n * train)
    b = a + int(n * val)
    return df.iloc[:a].copy(), df.iloc[a:b].copy(), df.iloc[b:].copy()


def xy(df: pd.DataFrame, target: str = "precio_cobre_usd_lb"):
    cols_excluir = {target, "fecha"}
    feature_cols = [c for c in df.columns if c not in cols_excluir]
    return df[feature_cols], df[target], feature_cols


def metrics(y_true, y_pred) -> dict:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
        "mape_pct": float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100),
    }


def main() -> None:
    print("=" * 60)
    print("Reentrenamiento Predictor Precio del Cobre")
    print("=" * 60)
    print(f"sklearn version: {__import__('sklearn').__version__}")
    print(f"Fecha: {datetime.now().isoformat(timespec='seconds')}")

    # 1) Cargar y construir features
    print("\n[1/4] Cargando datos crudos...")
    df_raw = load_raw()
    print(f"  Crudos: {len(df_raw)} filas | {df_raw['fecha'].min().date()} -> {df_raw['fecha'].max().date()}")

    print("\n[2/4] Construyendo features...")
    df = build_features(df_raw)
    df = df.dropna().reset_index(drop=True)
    print(f"  Con features: {len(df)} filas | {df.shape[1]} columnas")

    # Persistir CSV procesado
    PROC_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROC_CSV, index=False)
    print(f"  Guardado {PROC_CSV.name}")

    # 2) Split temporal
    train_df, val_df, test_df = temporal_split(df)
    X_train, y_train, feature_cols = xy(train_df)
    X_val, y_val, _ = xy(val_df)
    X_test, y_test, _ = xy(test_df)
    print(f"\n  Train: {len(X_train)} | Val: {len(X_val)} | Test: {len(X_test)}")
    print(f"  Features: {len(feature_cols)}")

    # 3) Ridge con grid search
    print("\n[3/4] Entrenando Ridge Regression...")
    alphas = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
    tscv = TimeSeriesSplit(n_splits=5)
    grid = GridSearchCV(
        Ridge(),
        {"alpha": alphas},
        cv=tscv,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
    )
    grid.fit(X_train, y_train)
    ridge = grid.best_estimator_
    print(f"  Mejor alpha: {grid.best_params_['alpha']}")
    print(f"  Mejor CV MAE: ${-grid.best_score_:.4f}")

    # Evaluar en test
    y_test_pred = ridge.predict(X_test)
    ridge_test = metrics(y_test, y_test_pred)
    print(f"  Test MAE:  ${ridge_test['mae']:.4f}")
    print(f"  Test RMSE: ${ridge_test['rmse']:.4f}")
    print(f"  Test R2:   {ridge_test['r2']:.4f}")
    print(f"  Test MAPE: {ridge_test['mape_pct']:.2f}%")

    # 4) Linear Regression (referencia)
    print("\n[4/4] Entrenando Linear Regression (referencia)...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    lr_test = metrics(y_test, lr.predict(X_test))
    print(f"  Test R2:   {lr_test['r2']:.4f}")
    print(f"  Test MAE:  ${lr_test['mae']:.4f}")

    # Persistir
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    # pickle.dump (no joblib) para mantener compatibilidad con app.py que usa pickle.load
    with open(RIDGE_PATH, "wb") as f:
        pickle.dump(ridge, f)
    with open(LR_PATH, "wb") as f:
        pickle.dump(lr, f)
    with open(FEATS_PATH, "wb") as f:
        pickle.dump(feature_cols, f)

    # Resumen
    summary = {
        "sklearn_version": __import__("sklearn").__version__,
        "fecha_reentrenamiento": datetime.now().isoformat(timespec="seconds"),
        "datos_crudos": {
            "filas": int(len(df_raw)),
            "desde": str(df_raw["fecha"].min().date()),
            "hasta": str(df_raw["fecha"].max().date()),
        },
        "features": {
            "total": int(len(feature_cols)),
            "lista": feature_cols,
        },
        "split": {
            "train": int(len(X_train)),
            "val": int(len(X_val)),
            "test": int(len(X_test)),
        },
        "ridge": {
            "alpha": float(ridge.alpha),
            "test_metrics": ridge_test,
        },
        "linear_regression": {
            "test_metrics": lr_test,
        },
    }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n" + "=" * 60)
    print("OK - modelos reentrenados con sklearn actual")
    print(f"  {RIDGE_PATH}")
    print(f"  {LR_PATH}")
    print(f"  {SUMMARY_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
