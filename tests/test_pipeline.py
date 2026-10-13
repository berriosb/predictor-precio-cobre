"""Tests de humo del pipeline.

El repo no tenia tests de Python. Estos cubren lo que no debe romperse en
silencio: que el config cargue, que el feature engineering aplique el
shift(1) anti-leakage, que los artefactos versionados existan y que
requirements.txt cubra los imports reales.

No requieren red ni entrenar modelos: corren en segundos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data_loader import load_config, validate_data  # noqa: E402
from src.features import create_all_features  # noqa: E402


@pytest.fixture(scope="module")
def config() -> dict:
    return load_config(config_path=str(ROOT / "config.yaml"))


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Serie sintetica con la forma que espera el pipeline."""
    n = 300
    rng = np.random.default_rng(seed=42)
    prices = 3.0 + np.cumsum(rng.normal(0, 0.02, n))
    return pd.DataFrame(
        {
            "fecha": pd.date_range("2020-01-01", periods=n, freq="B"),
            "precio_cobre_usd_lb": prices,
        }
    )


class TestConfig:
    def test_carga_config_de_la_raiz(self, config):
        assert isinstance(config, dict)
        assert "paths" in config
        assert "features" in config

    def test_declara_ticker_y_fechas(self, config):
        assert config["data"]["ticker"] == "HG=F"
        assert config["data"]["start_date"] == "2010-01-01"

    def test_lags_declarados_coinciden_con_readme(self, config):
        # El README publica 6 lags y 29 features en total.
        assert config["features"]["lags"] == [1, 2, 3, 7, 14, 30]


class TestDataValidation:
    def test_acepta_dataframe_valido(self, sample_df):
        es_valido, errores = validate_data(sample_df)
        assert es_valido, errores
        assert errores == []

    def test_rechaza_columnas_faltantes(self):
        incompleto = pd.DataFrame({"fecha": pd.date_range("2020-01-01", periods=3)})
        es_valido, errores = validate_data(incompleto)
        assert not es_valido
        assert errores


class TestFeatureEngineering:
    def test_genera_lags_declarados(self, sample_df, config):
        features = create_all_features(sample_df, config=config)
        for lag in config["features"]["lags"]:
            assert f"lag_{lag}" in features.columns

    def test_no_hay_leakage_en_lags(self, sample_df, config):
        """lag_1 del dia T debe ser el precio de T-1, no el de T.

        Es la invariante central del proyecto: si se rompe, el R2 de 0.95
        del README es fuga de informacion, no capacidad predictiva.
        """
        features = create_all_features(sample_df, config=config)
        limpio = features.dropna(subset=["lag_1"])

        precio_dia_anterior = sample_df["precio_cobre_usd_lb"].shift(1)
        esperado = precio_dia_anterior.loc[limpio.index]
        actual = limpio["lag_1"].to_numpy()
        esperado = esperado.to_numpy()

        assert np.allclose(actual, esperado), "lag_1 no refleja el dia anterior"

    def test_rolling_usa_shift_para_no_lookahead(self, sample_df, config):
        features = create_all_features(sample_df, config=config)
        ventana = config["features"]["rolling_windows"][0]
        stats = config["features"]["rolling_stats"][0]

        # Las columnas se nombran rolling_{stat}_{ventana}.
        media_col = f"rolling_{stats}_{ventana}"
        assert media_col in features.columns

        limpio = features.dropna(subset=[media_col])
        # Se recalcula sobre la serie ORIGINAL y luego se alinea por indice:
        # create_all_features ya descarto las filas iniciales, asi que un
        # rolling sobre el frame recortado no tendria historial suficiente.
        recalculado = (
            sample_df["precio_cobre_usd_lb"].rolling(ventana).mean().shift(1)
        ).reindex(limpio.index)
        assert np.allclose(limpio[media_col], recalculado)

    def test_descarta_filas_sin_features_completas(self, sample_df, config):
        """create_all_features elimina las filas que no pueden rellenarse.

        Con la ventana mayor de 90 dias, las primeras 90 quedan incompletas
        y se descartan. Es intencional: entrenar sobre filas con NaN daria
        resultados silenciosamente distintos.
        """
        ventana_max = max(config["features"]["rolling_windows"])
        features = create_all_features(sample_df, config=config)

        assert len(features) == len(sample_df) - ventana_max
        assert features.isnull().sum().sum() == 0


class TestArtefactosVersionados:
    """Los .pkl y .csv que la web y el README asumen presentes."""

    @pytest.mark.parametrize(
        "relpath",
        [
            "config.yaml",
            "requirements.txt",
            "data/processed/precio_cobre_features.csv",
            "models/ridge_model.pkl",
            "models/results_summary.json",
            "reports/walk_forward_results.csv",
        ],
    )
    def test_existe(self, relpath):
        assert (ROOT / relpath).exists(), f"falta {relpath}"

    def test_no_hay_repositorio_anidado(self):
        """El aplanado movio todo a la raiz; no debe reaparecer la carcasa."""
        anidado = ROOT / "predictor-precio-cobre"
        if not anidado.exists():
            return  # vacio o ausente: correcto
        # Solo toleramos un .venv local sin versionar.
        residuos = [p.name for p in anidado.iterdir() if p.name != ".venv"]
        assert residuos == [], f"anidado con residuos: {residuos}"


class TestManifest:
    def test_todo_import_tercero_esta_declarado(self):
        """Guard que habria detectado el hueco de statsmodels.

        Sin esto, `python src/retrain.py` falla con ImportError aunque
        requirements.txt parezca completo.
        """
        import subprocess

        script = ROOT / ".github" / "scripts" / "check_python_deps.py"
        resultado = subprocess.run(
            [sys.executable, str(script)], capture_output=True, text=True
        )
        assert resultado.returncode == 0, resultado.stdout + resultado.stderr