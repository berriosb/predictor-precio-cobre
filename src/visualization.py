"""
Modulo de visualizacion para el proyecto de prediccion de precios del cobre.

Este modulo proporciona funciones estandarizadas para:
- Graficos de series temporales
- Comparacion de predicciones vs valores reales
- Analisis de residuales
- Comparacion de modelos
- Heatmaps de correlacion
- Feature importance
"""

import os
from typing import Optional, List, Dict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
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


def setup_plot_style(config: Optional[dict] = None):
    """
    Configura el estilo global de las graficas.

    Args:
        config: Diccionario de configuracion (opcional)
    """
    if config is None:
        config = load_config()

    # Configurar estilo de matplotlib/seaborn con fallback
    try:
        plt.style.use('seaborn-v0_8-darkgrid')
    except OSError:
        try:
            plt.style.use('seaborn-darkgrid')
        except OSError:
            plt.style.use('default')
            print("Advertencia: usando estilo 'default' (estilos seaborn no disponibles)")

    sns.set_palette("husl")

    # Configuracion de plots
    plt.rcParams['figure.figsize'] = config['visualization']['figure_size']
    plt.rcParams['figure.dpi'] = config['visualization']['dpi']
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 11
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 9
    plt.rcParams['ytick.labelsize'] = 9
    plt.rcParams['legend.fontsize'] = 10


def plot_time_series(
    df: pd.DataFrame,
    date_column: str = 'fecha',
    value_column: str = 'precio_cobre_usd_lb',
    title: str = 'Precio del Cobre 2010-2024',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Grafico de serie temporal.

    Args:
        df: DataFrame con los datos
        date_column: Nombre de la columna de fecha
        value_column: Nombre de la columna de valores
        title: Titulo del grafico
        save_path: Ruta donde guardar el grafico (None = no guarda)

    Returns:
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df[date_column], df[value_column], linewidth=1.5, color='#2E86AB')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio (USD/lb)')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def plot_predictions(
    dates: pd.Series,
    y_true: pd.Series,
    y_pred: np.ndarray,
    model_name: str = 'Model',
    split_name: str = 'Test',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Grafico de predicciones vs valores reales.

    Args:
        dates: Serie con fechas
        y_true: Valores reales
        y_pred: Valores predichos
        model_name: Nombre del modelo
        split_name: Nombre del conjunto (Train/Val/Test)
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(dates, y_true, label='Real', linewidth=2, color='#2E86AB', alpha=0.8)
    ax.plot(dates, y_pred, label='Prediccion', linewidth=2, color='#A23B72', linestyle='--', alpha=0.8)

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio (USD/lb)')
    ax.set_title(f'{model_name} - Predicciones vs Real ({split_name})', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def plot_residuals(
    y_true: pd.Series,
    y_pred: np.ndarray,
    model_name: str = 'Model',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Analisis de residuales (errores).

    Args:
        y_true: Valores reales
        y_pred: Valores predichos
        model_name: Nombre del modelo
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    residuals = y_true - y_pred

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # 1. Scatter plot: residuales vs predicciones
    axes[0].scatter(y_pred, residuals, alpha=0.5, color='#2E86AB')
    axes[0].axhline(y=0, color='red', linestyle='--', linewidth=2)
    axes[0].set_xlabel('Predicciones')
    axes[0].set_ylabel('Residuales')
    axes[0].set_title('Residuales vs Predicciones')
    axes[0].grid(True, alpha=0.3)

    # 2. Histograma de residuales
    axes[1].hist(residuals, bins=30, edgecolor='black', color='#F18F01', alpha=0.7)
    axes[1].set_xlabel('Residuales')
    axes[1].set_ylabel('Frecuencia')
    axes[1].set_title('Distribucion de Residuales')
    axes[1].grid(True, alpha=0.3)

    # 3. Q-Q plot (normalidad)
    stats.probplot(residuals, dist="norm", plot=axes[2])
    axes[2].set_title('Q-Q Plot (Normalidad)')
    axes[2].grid(True, alpha=0.3)

    fig.suptitle(f'Analisis de Residuales - {model_name}', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def compare_models(
    metrics_dict: Dict[str, Dict[str, float]],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Grafico de comparacion de modelos.

    Args:
        metrics_dict: Diccionario con {nombre_modelo: {metrica: valor}}
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    df_metrics = pd.DataFrame(metrics_dict).T

    # Seleccionar metricas principales
    metrics_to_plot = ['mae', 'rmse', 'r2']
    df_plot = df_metrics[metrics_to_plot]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    colors = ['#2E86AB', '#A23B72', '#F18F01']

    # MAE
    df_plot['mae'].plot(kind='bar', ax=axes[0], color=colors[0], alpha=0.8)
    axes[0].set_title('MAE (Mean Absolute Error)', fontweight='bold')
    axes[0].set_ylabel('MAE (USD/lb)')
    axes[0].set_xlabel('Modelo')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(True, alpha=0.3)

    # RMSE
    df_plot['rmse'].plot(kind='bar', ax=axes[1], color=colors[1], alpha=0.8)
    axes[1].set_title('RMSE (Root Mean Squared Error)', fontweight='bold')
    axes[1].set_ylabel('RMSE (USD/lb)')
    axes[1].set_xlabel('Modelo')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(True, alpha=0.3)

    # R2
    df_plot['r2'].plot(kind='bar', ax=axes[2], color=colors[2], alpha=0.8)
    axes[2].set_title('R2 Score', fontweight='bold')
    axes[2].set_ylabel('R2')
    axes[2].set_xlabel('Modelo')
    axes[2].tick_params(axis='x', rotation=45)
    axes[2].axhline(y=0.85, color='red', linestyle='--', linewidth=1, label='Target: 0.85')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    fig.suptitle('Comparacion de Modelos', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    target_column: str = 'precio_cobre_usd_lb',
    top_n: int = 20,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Heatmap de correlacion de features.

    Args:
        df: DataFrame con features
        target_column: Nombre de la columna target
        top_n: Numero de features mas correlacionadas a mostrar
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    # Seleccionar solo columnas numericas
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    # Calcular correlaciones con el target
    correlations = df[numeric_cols].corr()[target_column].abs().sort_values(ascending=False)

    # Seleccionar top N features (incluyendo el target)
    top_features = correlations.head(top_n + 1).index.tolist()

    # Calcular matriz de correlacion
    corr_matrix = df[top_features].corr()

    # Crear heatmap
    fig, ax = plt.subplots(figsize=(12, 10))

    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt='.2f',
        cmap='coolwarm',
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title(f'Correlacion entre Top {top_n} Features y Target', fontsize=14, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def plot_feature_importance(
    importance_df: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Grafico de importancia de features.

    Args:
        importance_df: DataFrame con columnas ['feature', 'coefficient', 'abs_coefficient']
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Ordenar por coeficiente absoluto
    df_sorted = importance_df.sort_values('abs_coefficient', ascending=True)

    # Colores: positivos en azul, negativos en rojo
    colors = ['#2E86AB' if x >= 0 else '#A23B72' for x in df_sorted['coefficient']]

    ax.barh(df_sorted['feature'], df_sorted['coefficient'], color=colors, alpha=0.8)
    ax.set_xlabel('Coeficiente')
    ax.set_ylabel('Feature')
    ax.set_title('Importancia de Features (Linear Regression)', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def plot_train_val_test_split(
    df: pd.DataFrame,
    train_end_idx: int,
    val_end_idx: int,
    date_column: str = 'fecha',
    value_column: str = 'precio_cobre_usd_lb',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Visualiza el split de datos train/val/test.

    Args:
        df: DataFrame completo
        train_end_idx: Indice final de train
        val_end_idx: Indice final de validacion
        date_column: Nombre de la columna de fecha
        value_column: Nombre de la columna de valores
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    # Train
    ax.plot(df[date_column][:train_end_idx], df[value_column][:train_end_idx],
            label='Train', color='#2E86AB', linewidth=1.5)

    # Validation
    ax.plot(df[date_column][train_end_idx:val_end_idx], df[value_column][train_end_idx:val_end_idx],
            label='Validation', color='#F18F01', linewidth=1.5)

    # Test
    ax.plot(df[date_column][val_end_idx:], df[value_column][val_end_idx:],
            label='Test', color='#A23B72', linewidth=1.5)

    ax.set_xlabel('Fecha')
    ax.set_ylabel('Precio (USD/lb)')
    ax.set_title('Split Temporal: Train / Validation / Test', fontsize=14, fontweight='bold')
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def plot_seasonal_decomposition(
    df: pd.DataFrame,
    date_column: str = 'fecha',
    value_column: str = 'precio_cobre_usd_lb',
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Descomposicion de serie temporal (tendencia, estacionalidad, residual).

    Args:
        df: DataFrame con los datos
        date_column: Nombre de la columna de fecha
        value_column: Nombre de la columna de valores
        save_path: Ruta donde guardar el grafico

    Returns:
        Figura de matplotlib
    """
    from statsmodels.tsa.seasonal import seasonal_decompose

    # Preparar serie temporal
    ts = df.set_index(date_column)[value_column]

    # Descomponer (frecuencia anual: 252 dias habiles aprox)
    decomposition = seasonal_decompose(ts, model='additive', period=252, extrapolate_trend='freq')

    fig, axes = plt.subplots(4, 1, figsize=(14, 10))

    # Original
    decomposition.observed.plot(ax=axes[0], color='#2E86AB')
    axes[0].set_ylabel('Original')
    axes[0].set_title('Descomposicion de Serie Temporal', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)

    # Tendencia
    decomposition.trend.plot(ax=axes[1], color='#F18F01')
    axes[1].set_ylabel('Tendencia')
    axes[1].grid(True, alpha=0.3)

    # Estacionalidad
    decomposition.seasonal.plot(ax=axes[2], color='#A23B72')
    axes[2].set_ylabel('Estacionalidad')
    axes[2].grid(True, alpha=0.3)

    # Residual
    decomposition.resid.plot(ax=axes[3], color='#06A77D')
    axes[3].set_ylabel('Residual')
    axes[3].set_xlabel('Fecha')
    axes[3].grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        print(f"Grafico guardado en: {save_path}")

    return fig


def save_figure(fig: plt.Figure, filename: str, config_path: str = 'config.yaml'):
    """
    Guarda una figura en la carpeta de reportes.

    Args:
        fig: Figura de matplotlib
        filename: Nombre del archivo (incluir extension)
        config_path: Ruta al archivo de configuracion
    """
    config = load_config(config_path)
    figures_path = config['paths']['figures']

    os.makedirs(figures_path, exist_ok=True)

    output_path = os.path.join(figures_path, filename)
    fig.savefig(output_path, dpi=config['visualization']['dpi'], bbox_inches='tight')
    print(f"Figura guardada en: {output_path}")


if __name__ == '__main__':
    # Ejemplo de uso
    print("Ejecutando visualization.py...")
    print("-" * 50)

    # Configurar estilo
    setup_plot_style()

    # Cargar datos procesados
    import sys
    sys.path.append('..')
    from src.features import load_processed_data

    df = load_processed_data(config_path='../config.yaml')

    # Grafico de serie temporal
    fig1 = plot_time_series(df, title='Precio del Cobre 2010-2024')
    save_figure(fig1, 'serie_temporal.png', config_path='../config.yaml')

    # Heatmap de correlacion
    fig2 = plot_correlation_heatmap(df, top_n=15)
    save_figure(fig2, 'correlacion_heatmap.png', config_path='../config.yaml')

    print("\nVisualizaciones completadas.")
