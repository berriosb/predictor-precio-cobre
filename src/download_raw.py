"""
Descarga datos crudos del precio del cobre desde Yahoo Finance.
Replica la logica del notebook 01_descarga_datos.ipynb para que
cualquiera pueda regenerar data/raw/precio_cobre_yahoo.csv.

Uso:
    python src/download_raw.py
"""
import yfinance as yf
import pandas as pd
from pathlib import Path

# Mismo rango que el notebook original
TICKER = "HG=F"  # Copper Futures
START_DATE = "2010-01-01"
END_DATE = None  # hasta hoy

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "precio_cobre_yahoo.csv"


def download_copper_yahoo(start_date: str = START_DATE, end_date: str | None = END_DATE) -> pd.DataFrame:
    print(f"Descargando {TICKER} desde {start_date}...")
    df = yf.download(TICKER, start=start_date, end=end_date, progress=False)
    if df.empty:
        raise RuntimeError("Yahoo Finance no devolvio datos. Revisa tu conexion o el ticker.")

    # aplanar multi-indice de columnas si yfinance lo devuelve
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # conservar solo fecha + precio de cierre, normalizar nombres
    df = df.reset_index()
    df = df.rename(columns={"Date": "fecha", "Close": "precio_cobre_usd_lb"})
    df = df[["fecha", "precio_cobre_usd_lb"]].copy()
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
    df = df.sort_values("fecha").reset_index(drop=True)
    df = df.dropna(subset=["precio_cobre_usd_lb"])
    print(f"Descargados {len(df)} registros desde {df['fecha'].iloc[0]} hasta {df['fecha'].iloc[-1]}")
    return df


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = download_copper_yahoo()
    df.to_csv(OUT_PATH, index=False)
    print(f"Guardado en {OUT_PATH}")


if __name__ == "__main__":
    main()
