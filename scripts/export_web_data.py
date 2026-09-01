#!/usr/bin/env python3
"""Exporta artefactos versionados del modelo a JSON para la web estática.

Genera dos artefactos:
- web/src/data/dashboard.json: datos agregados ya consumidos por la web
- web/public/cobre-hgf.csv: dataset completo (sin downsample) para descarga
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "predictor-precio-cobre"
DASHBOARD_JSON = ROOT / "web" / "src" / "data" / "dashboard.json"
PUBLIC_CSV = ROOT / "web" / "public" / "cobre-hgf.csv"
PROCESSED = MODEL_ROOT / "data" / "processed" / "precio_cobre_features.csv"
WALK_FORWARD = MODEL_ROOT / "reports" / "walk_forward_results.csv"
SUMMARY = MODEL_ROOT / "models" / "results_summary.json"

WINDOWS = [
    ("2020-01-01", "2020-12-31"),
    ("2021-01-01", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
]


def mean_absolute_error(actual: list[float], predicted: list[float]) -> float:
    return sum(abs(a - p) for a, p in zip(actual, predicted, strict=True)) / len(actual)


def main() -> None:
    with PROCESSED.open(encoding="utf-8") as source:
        rows = list(csv.DictReader(source))

    # 1) CSV público: dataset completo sin downsample, columnas mínimas
    PUBLIC_CSV.parent.mkdir(parents=True, exist_ok=True)
    with PUBLIC_CSV.open("w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out)
        writer.writerow(["fecha", "precio_cobre_usd_lb"])
        for row in rows:
            writer.writerow([row["fecha"][:10], f"{float(row['precio_cobre_usd_lb']):.4f}"])
    print(f"CSV público: {PUBLIC_CSV} ({len(rows)} filas)")

    # 2) history para el chart: downsample (semanal + últimos 180 días + último)
    history_full = [
        {"date": row["fecha"][:10], "price": round(float(row["precio_cobre_usd_lb"]), 4)}
        for row in rows
    ]
    history_downsampled = [
        point
        for index, point in enumerate(history_full)
        if index % 7 == 0 or index >= len(history_full) - 180 or index == len(history_full) - 1
    ]

    # 3) Comparación walk-forward
    with WALK_FORWARD.open(encoding="utf-8") as source:
        walk_forward_rows = list(csv.DictReader(source))

    comparisons = []
    for (start, end), result in zip(WINDOWS, walk_forward_rows, strict=True):
        window_rows = [row for row in rows if start <= row["fecha"][:10] <= end]
        actual = [float(row["precio_cobre_usd_lb"]) for row in window_rows]
        naive = [float(row["lag_1"]) for row in window_rows]
        comparisons.append(
            {
                "year": result["ventana"],
                "ridgeMae": float(result["mae_usd"]),
                "naiveMae": round(mean_absolute_error(actual, naive), 4),
                "r2": float(result["r2"]),
                "mape": float(result["mape_pct"]),
                "trainRows": int(result["train_filas"]),
                "testRows": int(result["test_filas"]),
                "rmse": float(result["rmse_usd"]),
                "testStart": start,
                "testEnd": end,
            }
        )

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    output = {
        "generatedFrom": {
            "processed": str(PROCESSED.relative_to(ROOT)),
            "walkForward": str(WALK_FORWARD.relative_to(ROOT)),
            "summary": str(SUMMARY.relative_to(ROOT)),
        },
        "latest": history_full[-1],
        "history": history_downsampled,
        "walkForward": comparisons,
        "metrics": {
            "averageR2": round(sum(row["r2"] for row in comparisons) / len(comparisons), 4),
            "averageMape": round(sum(row["mape"] for row in comparisons) / len(comparisons), 2),
            "averageMae": round(
                sum((row["ridgeMae"] + row["naiveMae"]) / 2 for row in comparisons) / len(comparisons),
                4,
            ),
            "ridgeWins": sum(row["ridgeMae"] < row["naiveMae"] for row in comparisons),
            "naiveWins": sum(row["naiveMae"] <= row["ridgeMae"] for row in comparisons),
            "features": summary["features"]["total"],
            "records": summary["datos_crudos"]["filas"],
            "alpha": summary["ridge"]["alpha"],
        },
    }

    DASHBOARD_JSON.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_JSON.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Dashboard JSON: {DASHBOARD_JSON} ({len(history_downsampled)} puntos downsampleados)")


if __name__ == "__main__":
    main()
