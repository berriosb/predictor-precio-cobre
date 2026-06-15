"""
Genera los graficos principales del proyecto para el README.

Uso:
    python src/regenerate_figures.py

Salida (en reports/figures/):
    - 01_price_history.png       Serie historica con crisis anotadas
    - 02_lag1_scatter.png         Scatter lag_1 vs target (muestra el leakage-fix)
    - 03_model_comparison.png     Comparacion de metricas Ridge vs LR
    - 04_predictions_vs_actual.png Predicciones Ridge vs precio real (test)
"""
import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yaml

warnings.filterwarnings("ignore")
sns.set_theme(style="darkgrid", context="notebook")

BASE = Path(__file__).resolve().parent.parent
FIG_DIR = BASE / "reports" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

PROC_CSV = BASE / "data" / "processed" / "precio_cobre_features.csv"
RAW_CSV = BASE / "data" / "raw" / "precio_cobre_yahoo.csv"
RIDGE = BASE / "models" / "ridge_model.pkl"
LR = BASE / "models" / "linear_regression.pkl"
FEATS = BASE / "models" / "feature_names.pkl"
SUMMARY = BASE / "models" / "results_summary.json"

COLORS = {
    "actual": "#2c3e50",
    "ridge": "#e74c3c",
    "lr": "#3498db",
}


def fig_price_history() -> None:
    raw = pd.read_csv(RAW_CSV, parse_dates=["fecha"])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(raw["fecha"], raw["precio_cobre_usd_lb"], color=COLORS["actual"], linewidth=1.0)
    ax.set_title("Precio del cobre (USD/lb) — 2010 a hoy", fontsize=14, fontweight="bold")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("USD / libra")
    # Anotar crisis
    crisis = [("2020-03-01", "COVID-19"), ("2022-03-01", "Guerra Ucrania")]
    for date, label in crisis:
        d = pd.Timestamp(date)
        if raw["fecha"].min() <= d <= raw["fecha"].max():
            ax.axvline(d, color="gray", linestyle="--", alpha=0.5)
            ax.annotate(label, xy=(d, raw["precio_cobre_usd_lb"].max() * 0.95),
                        fontsize=9, color="gray")
    fig.tight_layout()
    out = FIG_DIR / "01_price_history.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  {out.name}")


def fig_lag1_scatter() -> None:
    df = pd.read_csv(PROC_CSV, parse_dates=["fecha"])
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(df["lag_1"], df["precio_cobre_usd_lb"], alpha=0.3, s=8, color=COLORS["actual"])
    lo = min(df["lag_1"].min(), df["precio_cobre_usd_lb"].min())
    hi = max(df["lag_1"].max(), df["precio_cobre_usd_lb"].max())
    ax.plot([lo, hi], [lo, hi], "r--", linewidth=1.2, label="y = x (prediccion trivial)")
    r = df["lag_1"].corr(df["precio_cobre_usd_lb"])
    ax.set_title(f"Precio de ayer (lag_1) vs precio de hoy — r = {r:.4f}",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("lag_1 (USD/lb)")
    ax.set_ylabel("precio (USD/lb)")
    ax.legend(loc="upper left")
    fig.tight_layout()
    out = FIG_DIR / "02_lag1_scatter.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  {out.name}")


def fig_model_comparison() -> None:
    summary = json.loads(SUMMARY.read_text())
    ridge = summary["ridge"]["test_metrics"]
    lr = summary["linear_regression"]["test_metrics"]

    metrics_names = ["R²", "MAE (USD)", "RMSE (USD)", "MAPE (%)"]
    ridge_vals = [ridge["r2"], ridge["mae"], ridge["rmse"], ridge["mape_pct"]]
    lr_vals = [lr["r2"], lr["mae"], lr["rmse"], lr["mape_pct"]]

    fig, axes = plt.subplots(1, 4, figsize=(14, 4))
    for i, (name, r_val, l_val) in enumerate(zip(metrics_names, ridge_vals, lr_vals)):
        axes[i].bar(["Ridge", "Linear"], [r_val, l_val],
                    color=[COLORS["ridge"], COLORS["lr"]], alpha=0.85)
        axes[i].set_title(name, fontweight="bold")
        for j, v in enumerate([r_val, l_val]):
            label = f"{v:.4f}" if name == "R²" else f"{v:.4f}"
            axes[i].text(j, v, label, ha="center", va="bottom", fontsize=10)
        axes[i].set_ylim(0, max(r_val, l_val) * 1.2)
    fig.suptitle("Comparacion Ridge vs Linear Regression (Test set)",
                 fontsize=14, fontweight="bold")
    fig.tight_layout()
    out = FIG_DIR / "03_model_comparison.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  {out.name}")


def fig_predictions() -> None:
    df = pd.read_csv(PROC_CSV, parse_dates=["fecha"])
    with open(FEATS, "rb") as f:
        feature_cols = pd.read_pickle(BASE / "models" / "feature_names.pkl") if False else __import__("pickle").load(f)
    ridge = joblib.load(RIDGE)
    lr = joblib.load(LR)

    n = len(df)
    a = int(n * 0.8)
    b = a + int(n * 0.1)
    test = df.iloc[b:].copy()
    X_test = test[feature_cols]
    y_test = test["precio_cobre_usd_lb"]

    test = test.assign(
        pred_ridge=ridge.predict(X_test),
        pred_lr=lr.predict(X_test),
    )

    # Limitar a los ultimos 120 dias para que se vea bien
    test_tail = test.tail(120).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(test_tail["fecha"], test_tail["precio_cobre_usd_lb"],
            color=COLORS["actual"], linewidth=1.6, label="Precio real")
    ax.plot(test_tail["fecha"], test_tail["pred_ridge"],
            color=COLORS["ridge"], linewidth=1.2, linestyle="--", label="Ridge (pred)")
    ax.plot(test_tail["fecha"], test_tail["pred_lr"],
            color=COLORS["lr"], linewidth=1.0, linestyle=":", label="Linear (pred)")
    ax.set_title("Predicciones vs realidad (ultimos 120 dias del test set)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("USD / libra")
    ax.legend(loc="upper left")
    fig.tight_layout()
    out = FIG_DIR / "04_predictions_vs_actual.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  {out.name}")


def main() -> None:
    print("Regenerando figuras...")
    fig_price_history()
    fig_lag1_scatter()
    fig_model_comparison()
    fig_predictions()
    print(f"Listo. {len(list(FIG_DIR.glob('*.png')))} figuras en {FIG_DIR}")


if __name__ == "__main__":
    main()
