#!/usr/bin/env python3
"""Exporta artefactos versionados del modelo a JSON para la web estática."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = ROOT / "predictor-precio-cobre"
OUTPUT = ROOT / "web" / "src" / "data" / "dashboard.json"
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

    history = [
        {"date": row["fecha"][:10], "price": round(float(row["precio_cobre_usd_lb"]), 4)}
        for row in rows
    ]
    downsampled = [
        point
        for index, point in enumerate(history)
        if index % 7 == 0 or index >= len(history) - 180 or index == len(history) - 1
    ]

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
            }
        )

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    output = {
        "generatedFrom": {
            "processed": str(PROCESSED.relative_to(ROOT)),
            "walkForward": str(WALK_FORWARD.relative_to(ROOT)),
            "summary": str(SUMMARY.relative_to(ROOT)),
        },
        "latest": downsampled[-1],
        "history": downsampled,
        "walkForward": comparisons,
        "metrics": {
            "averageR2": round(sum(row["r2"] for row in comparisons) / len(comparisons), 4),
            "averageMape": round(sum(row["mape"] for row in comparisons) / len(comparisons), 2),
            "ridgeWins": sum(row["ridgeMae"] < row["naiveMae"] for row in comparisons),
            "naiveWins": sum(row["naiveMae"] <= row["ridgeMae"] for row in comparisons),
            "features": summary["features"]["total"],
            "records": summary["datos_crudos"]["filas"],
            "alpha": summary["ridge"]["alpha"],
        },
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Exportado: {OUTPUT} ({len(downsampled)} puntos)")


if __name__ == "__main__":
    main()
