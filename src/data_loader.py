"""
Modulo para descarga y carga de datos del precio del cobre.

Este modulo proporciona funciones para:
- Descargar datos historicos del precio del cobre desde Yahoo Finance
- Cargar datos ya descargados desde archivos CSV
- Realizar limpieza basica y validacion de datos
"""

import os
from datetime import datetime
from typing import Optional, Tuple
import pandas as pd
import yfinance as yf
import yaml


def load_config(config_path: str = 'config.yaml') -> dict:
    """
    Carga la configuracion desde el archivo YAML.

    Args:
        config_path: Ruta al archivo de configuracion

    Returns:
        Diccionario con la configuracion del proyecto
    """
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config


def download_copper_yahoo(
    ticker: str = 'HG=F',
    start_date: str = '2010-01-01',
    end_date: Optional[str] = None,
    save_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Descarga datos historicos del precio del cobre desde Yahoo Finance.

    Args:
        ticker: Simbolo del ticker en Yahoo Finance (default: 'HG=F' para Copper Futures)
        start_date: Fecha inicial en formato 'YYYY-MM-DD'
        end_date: Fecha final en formato 'YYYY-MM-DD' (None = hasta hoy)
        save_path: Ruta donde guardar el CSV (None = no guarda)

    Returns:
        DataFrame con columnas ['fecha', 'precio_cobre_usd_lb']

    Raises:
        ValueError: Si no se pueden descargar datos
    """
    print(f"Descargando datos de {ticker} desde {start_date}...")

    try:
        # Descargar datos usando yfinance
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        df = yf.download(ticker, start=start_date, end=end_date, progress=False)

        if df.empty:
            raise ValueError(f"No se pudieron descargar datos para {ticker}")

        # Resetear indice para tener la fecha como columna
        df = df.reset_index()

        # Seleccionar solo las columnas necesarias
        # Usamos el precio de cierre (Close) como precio del cobre
        df = df[['Date', 'Close']].copy()

        # Renombrar columnas
        df.columns = ['fecha', 'precio_cobre_usd_lb']

        # Eliminar filas con valores nulos
        df = df.dropna()

        # Ordenar cronologicamente
        df = df.sort_values('fecha').reset_index(drop=True)

        print(f"Descarga exitosa: {len(df)} registros desde {df['fecha'].min()} hasta {df['fecha'].max()}")

        # Guardar si se especifica ruta
        if save_path:
            dir_path = os.path.dirname(save_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            df.to_csv(save_path, index=False)
            print(f"Datos guardados en: {save_path}")

        return df

    except Exception as e:
        raise ValueError(f"Error al descargar datos: {str(e)}")


def load_copper_data(
    file_path: str,
    parse_dates: bool = True
) -> pd.DataFrame:
    """
    Carga datos del precio del cobre desde un archivo CSV.

    Args:
        file_path: Ruta al archivo CSV
        parse_dates: Si True, convierte la columna fecha a datetime

    Returns:
        DataFrame con los datos del cobre

    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No se encontro el archivo: {file_path}")

    print(f"Cargando datos desde: {file_path}")

    try:
        # Cargar CSV
        df = pd.read_csv(file_path)

        # Parsear fechas si se solicita
        if parse_dates and 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])

        # Eliminar valores nulos
        df = df.dropna()

        # Ordenar cronologicamente
        df = df.sort_values('fecha').reset_index(drop=True)

        print(f"Datos cargados: {len(df)} registros desde {df['fecha'].min()} hasta {df['fecha'].max()}")

        return df

    except Exception as e:
        raise ValueError(f"Error al cargar datos: {str(e)}")


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Genera un resumen estadistico de los datos del cobre.

    Args:
        df: DataFrame con los datos del cobre

    Returns:
        Diccionario con estadisticas descriptivas
    """
    summary = {
        'num_registros': len(df),
        'fecha_inicio': df['fecha'].min(),
        'fecha_fin': df['fecha'].max(),
        'precio_promedio': df['precio_cobre_usd_lb'].mean(),
        'precio_mediana': df['precio_cobre_usd_lb'].median(),
        'precio_min': df['precio_cobre_usd_lb'].min(),
        'precio_max': df['precio_cobre_usd_lb'].max(),
        'precio_std': df['precio_cobre_usd_lb'].std(),
        'valores_nulos': df.isnull().sum().sum()
    }

    return summary


def validate_data(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Valida que los datos cumplan con los requisitos minimos.

    Args:
        df: DataFrame con los datos del cobre

    Returns:
        Tupla (es_valido, lista_de_errores)
    """
    errores = []

    # Verificar columnas requeridas
    columnas_requeridas = ['fecha', 'precio_cobre_usd_lb']
    for col in columnas_requeridas:
        if col not in df.columns:
            errores.append(f"Falta la columna requerida: {col}")

    # Verificar que haya suficientes datos
    if len(df) < 100:
        errores.append(f"Datos insuficientes: {len(df)} registros (minimo 100)")

    # Verificar que no haya valores nulos
    if df.isnull().sum().sum() > 0:
        errores.append("El DataFrame contiene valores nulos")

    # Verificar que los precios sean positivos
    if (df['precio_cobre_usd_lb'] <= 0).any():
        errores.append("Existen precios negativos o cero")

    # Verificar que las fechas esten ordenadas
    if not df['fecha'].is_monotonic_increasing:
        errores.append("Las fechas no estan ordenadas cronologicamente")

    es_valido = len(errores) == 0

    return es_valido, errores


def download_and_load(
    config_path: str = 'config.yaml',
    force_download: bool = False
) -> pd.DataFrame:
    """
    Funcion de conveniencia que descarga o carga datos segun configuracion.

    Si el archivo ya existe y force_download=False, carga desde archivo.
    Si no existe o force_download=True, descarga datos nuevos.

    Args:
        config_path: Ruta al archivo de configuracion
        force_download: Si True, fuerza la descarga aunque exista el archivo

    Returns:
        DataFrame con los datos del cobre
    """
    # Cargar configuracion
    config = load_config(config_path)

    # Construir rutas
    raw_data_path = config['paths']['raw_data']
    raw_file = config['files']['raw_csv']
    full_path = os.path.join(raw_data_path, raw_file)

    # Verificar si existe el archivo
    file_exists = os.path.exists(full_path)

    if file_exists and not force_download:
        print(f"Archivo encontrado. Cargando desde: {full_path}")
        df = load_copper_data(full_path)
    else:
        if force_download:
            print("Forzando nueva descarga...")
        else:
            print("Archivo no encontrado. Descargando datos...")

        # Descargar datos
        ticker = config['data']['ticker']
        start_date = config['data']['start_date']
        end_date = config['data']['end_date']

        df = download_copper_yahoo(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            save_path=full_path
        )

    # Validar datos
    es_valido, errores = validate_data(df)
    if not es_valido:
        print("ADVERTENCIA: Los datos tienen problemas:")
        for error in errores:
            print(f"  - {error}")

    return df


if __name__ == '__main__':
    # Ejemplo de uso
    print("Ejecutando data_loader.py...")
    print("-" * 50)

    # Descargar datos
    df = download_and_load(config_path='../config.yaml')

    # Mostrar resumen
    print("\nResumen de datos:")
    print("-" * 50)
    summary = get_data_summary(df)
    for key, value in summary.items():
        print(f"{key}: {value}")

    # Mostrar primeras filas
    print("\nPrimeras 5 filas:")
    print("-" * 50)
    print(df.head())
