"""
Modulo de Feature Engineering para series temporales del precio del cobre.

Este modulo proporciona funciones para crear features predictoras:
- Lags: valores pasados de la serie temporal
- Rolling statistics: promedios moviles, desviaciones, min/max
- Features temporales: year, month, day, dayofweek, etc.
- Features de tendencia: cambios, retornos, volatilidad
"""

from typing import List, Optional
import pandas as pd
import numpy as np
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


def create_lag_features(
    df: pd.DataFrame,
    column: str = 'precio_cobre_usd_lb',
    lags: List[int] = [1, 2, 3, 7, 14, 30]
) -> pd.DataFrame:
    """
    Crea features de lags (valores pasados).

    Args:
        df: DataFrame con los datos
        column: Nombre de la columna a la que aplicar lags
        lags: Lista de numeros de dias hacia atras

    Returns:
        DataFrame con nuevas columnas lag_1, lag_2, etc.
    """
    df_copy = df.copy()

    for lag in lags:
        df_copy[f'lag_{lag}'] = df_copy[column].shift(lag)

    print(f"Lags creados: {lags}")
    return df_copy


def create_rolling_features(
    df: pd.DataFrame,
    column: str = 'precio_cobre_usd_lb',
    windows: List[int] = [7, 30, 90],
    stats: List[str] = ['mean', 'std', 'min', 'max']
) -> pd.DataFrame:
    """
    Crea features de rolling statistics (estadisticos moviles).

    Args:
        df: DataFrame con los datos
        column: Nombre de la columna a la que aplicar rolling
        windows: Lista de tamaños de ventana (en dias)
        stats: Lista de estadisticos a calcular ['mean', 'std', 'min', 'max']

    Returns:
        DataFrame con nuevas columnas rolling_mean_7, rolling_std_30, etc.
    """
    df_copy = df.copy()

    # Mapeo de estadisticos a funciones
    stat_funcs = {
        'mean': 'mean',
        'std': 'std',
        'min': 'min',
        'max': 'max'
    }

    for window in windows:
        # shift(1) para evitar data leakage: las rolling stats del dia T
        # solo deben mirar hacia el pasado (no incluir el precio de T).
        rolling_window = df_copy[column].shift(1).rolling(window=window)
        for stat in stats:
            if stat in stat_funcs:
                df_copy[f'rolling_{stat}_{window}'] = getattr(rolling_window, stat_funcs[stat])()

    print(f"Rolling features creados para ventanas: {windows}")
    return df_copy


def create_temporal_features(
    df: pd.DataFrame,
    date_column: str = 'fecha'
) -> pd.DataFrame:
    """
    Crea features temporales desde la columna de fecha.

    Args:
        df: DataFrame con los datos
        date_column: Nombre de la columna de fecha

    Returns:
        DataFrame con nuevas columnas: year, month, day, dayofweek, quarter, etc.
    """
    df_copy = df.copy()

    # Asegurar que la columna es datetime
    if not pd.api.types.is_datetime64_any_dtype(df_copy[date_column]):
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])

    # Extraer componentes temporales
    df_copy['year'] = df_copy[date_column].dt.year
    df_copy['month'] = df_copy[date_column].dt.month
    df_copy['day'] = df_copy[date_column].dt.day
    df_copy['dayofweek'] = df_copy[date_column].dt.dayofweek  # 0=Lunes, 6=Domingo
    df_copy['quarter'] = df_copy[date_column].dt.quarter

    # Features binarios
    df_copy['is_month_start'] = df_copy[date_column].dt.is_month_start.astype(int)
    df_copy['is_month_end'] = df_copy[date_column].dt.is_month_end.astype(int)

    print("Features temporales creados: year, month, day, dayofweek, quarter, is_month_start, is_month_end")
    return df_copy


def create_trend_features(
    df: pd.DataFrame,
    column: str = 'precio_cobre_usd_lb'
) -> pd.DataFrame:
    """
    Crea features de tendencia y volatilidad.

    Args:
        df: DataFrame con los datos
        column: Nombre de la columna de precio

    Returns:
        DataFrame con nuevas columnas: price_diff, price_pct_change, volatility_7d, volatility_30d
    """
    df_copy = df.copy()

    # Diferencia dia a dia (con shift para evitar leakage: usa precio de T-1 vs T-2)
    df_copy['price_diff'] = df_copy[column].shift(1).diff()

    # Cambio porcentual (retorno) - mismo principio
    df_copy['price_pct_change'] = df_copy[column].shift(1).pct_change() * 100

    # Volatilidad: desviacion estandar de los retornos (ya shifted)
    df_copy['volatility_7d'] = df_copy['price_pct_change'].rolling(window=7).std()
    df_copy['volatility_30d'] = df_copy['price_pct_change'].rolling(window=30).std()

    print("Features de tendencia creados: price_diff, price_pct_change, volatility_7d, volatility_30d")
    return df_copy


def create_all_features(
    df: pd.DataFrame,
    config: Optional[dict] = None,
    config_path: str = 'config.yaml'
) -> pd.DataFrame:
    """
    Aplica todas las transformaciones de feature engineering.

    Args:
        df: DataFrame con los datos originales
        config: Diccionario de configuracion (si None, se carga desde archivo)
        config_path: Ruta al archivo de configuracion

    Returns:
        DataFrame con todas las features creadas y filas con NaN eliminadas
    """
    print("Iniciando feature engineering...")
    print(f"Datos originales: {len(df)} filas")

    # Cargar configuracion si no se proporciona
    if config is None:
        config = load_config(config_path)

    df_features = df.copy()

    # 1. Features temporales
    df_features = create_temporal_features(df_features)

    # 2. Lags
    lags = config['features']['lags']
    df_features = create_lag_features(df_features, lags=lags)

    # 3. Rolling statistics
    windows = config['features']['rolling_windows']
    stats = config['features']['rolling_stats']
    df_features = create_rolling_features(df_features, windows=windows, stats=stats)

    # 4. Tendencia
    df_features = create_trend_features(df_features)

    # Eliminar filas con NaN (resultado de lags y rolling)
    filas_antes = len(df_features)
    df_features = df_features.dropna()
    filas_despues = len(df_features)
    filas_eliminadas = filas_antes - filas_despues

    print(f"\nFeature engineering completado:")
    print(f"  - Filas con NaN eliminadas: {filas_eliminadas}")
    print(f"  - Filas finales: {filas_despues}")
    print(f"  - Total de columnas: {len(df_features.columns)}")

    return df_features


def get_feature_correlation(
    df: pd.DataFrame,
    target_column: str = 'precio_cobre_usd_lb',
    top_n: int = 20
) -> pd.DataFrame:
    """
    Calcula la correlacion de todas las features con el target.

    Args:
        df: DataFrame con features
        target_column: Nombre de la columna target
        top_n: Numero de features mas correlacionadas a retornar

    Returns:
        DataFrame con features ordenadas por correlacion absoluta
    """
    # Seleccionar solo columnas numericas
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Calcular correlaciones
    correlaciones = df[numeric_cols].corr()[target_column].sort_values(ascending=False)

    # Eliminar la correlacion consigo mismo
    correlaciones = correlaciones[correlaciones.index != target_column]

    # Crear DataFrame con correlaciones
    df_corr = pd.DataFrame({
        'feature': correlaciones.index,
        'correlacion': correlaciones.values,
        'correlacion_abs': np.abs(correlaciones.values)
    })

    # Ordenar por correlacion absoluta
    df_corr = df_corr.sort_values('correlacion_abs', ascending=False).head(top_n)

    return df_corr.reset_index(drop=True)


def save_processed_data(
    df: pd.DataFrame,
    config_path: str = 'config.yaml'
) -> str:
    """
    Guarda el DataFrame con features procesados.

    Args:
        df: DataFrame con features
        config_path: Ruta al archivo de configuracion

    Returns:
        Ruta del archivo guardado
    """
    import os

    # Cargar configuracion
    config = load_config(config_path)

    # Construir ruta de salida
    processed_path = config['paths']['processed_data']
    processed_file = config['files']['processed_csv']
    output_path = os.path.join(processed_path, processed_file)

    # Crear directorio si no existe
    os.makedirs(processed_path, exist_ok=True)

    # Guardar
    df.to_csv(output_path, index=False)
    print(f"\nDatos procesados guardados en: {output_path}")

    return output_path


def load_processed_data(config_path: str = 'config.yaml') -> pd.DataFrame:
    """
    Carga el DataFrame con features procesados.

    Args:
        config_path: Ruta al archivo de configuracion

    Returns:
        DataFrame con features procesados
    """
    import os

    # Cargar configuracion
    config = load_config(config_path)

    # Construir ruta
    processed_path = config['paths']['processed_data']
    processed_file = config['files']['processed_csv']
    input_path = os.path.join(processed_path, processed_file)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No se encontro el archivo: {input_path}")

    # Cargar
    df = pd.read_csv(input_path)

    # Parsear fecha
    if 'fecha' in df.columns:
        df['fecha'] = pd.to_datetime(df['fecha'])

    print(f"Datos procesados cargados desde: {input_path}")
    print(f"  - Filas: {len(df)}")
    print(f"  - Columnas: {len(df.columns)}")

    return df


if __name__ == '__main__':
    # Ejemplo de uso
    print("Ejecutando features.py...")
    print("-" * 50)

    # Cargar datos (asumiendo que ya fueron descargados)
    import sys
    sys.path.append('..')
    from src.data_loader import download_and_load

    # Cargar datos originales
    df = download_and_load(config_path='../config.yaml')

    # Aplicar feature engineering
    df_features = create_all_features(df, config_path='../config.yaml')

    # Mostrar correlaciones
    print("\nTop 10 features mas correlacionadas con el precio:")
    print("-" * 50)
    correlaciones = get_feature_correlation(df_features, top_n=10)
    print(correlaciones)

    # Guardar datos procesados
    save_processed_data(df_features, config_path='../config.yaml')

    # Mostrar muestra
    print("\nPrimeras 3 filas con features:")
    print("-" * 50)
    print(df_features.head(3))
