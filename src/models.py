"""
Modulo de entrenamiento y evaluacion de modelos para prediccion de precios del cobre.

Este modulo proporciona funciones para:
- Split temporal de datos (sin shuffle)
- Entrenamiento de modelos baseline: Linear Regression, ARIMA
- Entrenamiento de modelos avanzados: Ridge, XGBoost, Random Forest, SARIMAX
- Evaluacion de modelos con metricas (MAE, RMSE, R2, MAPE)
- Comparacion de multiples modelos
- Feature importance para modelos basados en arboles
- Persistencia de modelos
"""

import os
from typing import Tuple, Dict, Optional
import pandas as pd
import numpy as np
import yaml
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
import warnings

# Suprimir warnings específicos de statsmodels y convergencia
warnings.filterwarnings('ignore', category=UserWarning, module='statsmodels')
warnings.filterwarnings('ignore', category=FutureWarning, module='statsmodels')
warnings.filterwarnings('ignore', category=RuntimeWarning)


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


def split_data(
    df: pd.DataFrame,
    train_size: float = 0.8,
    val_size: float = 0.1,
    test_size: float = 0.1
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split temporal de datos para series temporales (sin shuffle).

    IMPORTANTE: En series temporales NO se hace shuffle. El split es cronologico.

    Args:
        df: DataFrame con los datos
        train_size: Proporcion de datos para entrenamiento
        val_size: Proporcion de datos para validacion
        test_size: Proporcion de datos para test

    Returns:
        Tupla (train_df, val_df, test_df)
    """
    # Verificar que las proporciones suman 1.0
    total = train_size + val_size + test_size
    if not np.isclose(total, 1.0):
        raise ValueError(f"Las proporciones deben sumar 1.0 (actual: {total})")

    # Calcular indices de corte
    n = len(df)
    train_end = int(n * train_size)
    val_end = train_end + int(n * val_size)

    # Split cronologico
    train_df = df.iloc[:train_end].copy()
    val_df = df.iloc[train_end:val_end].copy()
    test_df = df.iloc[val_end:].copy()

    print(f"Split temporal completado:")
    print(f"  - Train: {len(train_df)} filas ({train_size*100:.0f}%)")
    print(f"  - Val:   {len(val_df)} filas ({val_size*100:.0f}%)")
    print(f"  - Test:  {len(test_df)} filas ({test_size*100:.0f}%)")
    print(f"  - Total: {len(df)} filas")

    return train_df, val_df, test_df


def prepare_features_target(
    df: pd.DataFrame,
    target_column: str = 'precio_cobre_usd_lb',
    exclude_columns: list = ['fecha']
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Separa features (X) y target (y).

    Args:
        df: DataFrame con datos
        target_column: Nombre de la columna target
        exclude_columns: Columnas a excluir de features (ej. fecha)

    Returns:
        Tupla (X, y) donde X son las features y y es el target
    """
    # Columnas a excluir: target + columnas especificadas
    exclude = [target_column] + exclude_columns

    # Seleccionar features (todas las columnas numericas excepto las excluidas)
    feature_columns = [col for col in df.columns if col not in exclude]

    X = df[feature_columns].copy()
    y = df[target_column].copy()

    return X, y


def train_linear_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: Optional[pd.DataFrame] = None,
    y_val: Optional[pd.Series] = None
) -> Tuple[LinearRegression, Dict[str, float]]:
    """
    Entrena un modelo de Linear Regression.

    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
        X_val: Features de validacion (opcional)
        y_val: Target de validacion (opcional)

    Returns:
        Tupla (modelo_entrenado, metricas_dict)
    """
    print("\nEntrenando Linear Regression...")

    # Crear y entrenar modelo
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predicciones en train
    y_train_pred = model.predict(X_train)

    # Calcular metricas en train
    metrics = {
        'train_mae': mean_absolute_error(y_train, y_train_pred),
        'train_rmse': np.sqrt(mean_squared_error(y_train, y_train_pred)),
        'train_r2': r2_score(y_train, y_train_pred)
    }

    # Si hay validacion, calcular metricas
    if X_val is not None and y_val is not None:
        y_val_pred = model.predict(X_val)
        metrics['val_mae'] = mean_absolute_error(y_val, y_val_pred)
        metrics['val_rmse'] = np.sqrt(mean_squared_error(y_val, y_val_pred))
        metrics['val_r2'] = r2_score(y_val, y_val_pred)

    print(f"  - Train MAE: {metrics['train_mae']:.4f}")
    print(f"  - Train RMSE: {metrics['train_rmse']:.4f}")
    print(f"  - Train R2: {metrics['train_r2']:.4f}")

    if 'val_mae' in metrics:
        print(f"  - Val MAE: {metrics['val_mae']:.4f}")
        print(f"  - Val RMSE: {metrics['val_rmse']:.4f}")
        print(f"  - Val R2: {metrics['val_r2']:.4f}")

    return model, metrics


def train_arima(
    train_series: pd.Series,
    order: Tuple[int, int, int] = (5, 1, 2),
    seasonal: bool = False
) -> ARIMA:
    """
    Entrena un modelo ARIMA.

    Args:
        train_series: Serie temporal de entrenamiento (solo valores del target)
        order: Orden ARIMA (p, d, q)
            - p: autorregresivo (ultimos p valores)
            - d: diferenciacion (orden de diferenciacion)
            - q: media movil (ultimos q errores)
        seasonal: Si incluir componente estacional

    Returns:
        Modelo ARIMA entrenado
    """
    print(f"\nEntrenando ARIMA{order}...")

    # Crear y entrenar modelo
    model = ARIMA(train_series, order=order, seasonal_order=None if not seasonal else (1, 1, 1, 12))
    model_fit = model.fit()

    print(f"  - AIC: {model_fit.aic:.2f}")
    print(f"  - BIC: {model_fit.bic:.2f}")

    return model_fit


def evaluate_model(
    y_true: pd.Series,
    y_pred: np.ndarray,
    model_name: str = 'Model'
) -> Dict[str, float]:
    """
    Evalua un modelo calculando metricas de error.

    Args:
        y_true: Valores reales
        y_pred: Valores predichos
        model_name: Nombre del modelo (para print)

    Returns:
        Diccionario con metricas: MAE, RMSE, R2, MAPE
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100

    metrics = {
        'mae': mae,
        'rmse': rmse,
        'r2': r2,
        'mape': mape
    }

    print(f"\nMetricas de {model_name}:")
    print(f"  - MAE:  {mae:.4f} USD/lb")
    print(f"  - RMSE: {rmse:.4f} USD/lb")
    print(f"  - R2:   {r2:.4f}")
    print(f"  - MAPE: {mape:.2f}%")

    return metrics


def save_model(
    model,
    filename: str,
    config_path: str = 'config.yaml'
) -> str:
    """
    Guarda un modelo entrenado.

    Args:
        model: Modelo a guardar
        filename: Nombre del archivo (ej. 'linear_regression.pkl')
        config_path: Ruta al archivo de configuracion

    Returns:
        Ruta del archivo guardado
    """
    # Cargar configuracion
    config = load_config(config_path)

    # Construir ruta
    models_path = config['paths']['models']
    output_path = os.path.join(models_path, filename)

    # Crear directorio si no existe
    os.makedirs(models_path, exist_ok=True)

    # Guardar modelo
    joblib.dump(model, output_path)
    print(f"\nModelo guardado en: {output_path}")

    return output_path


def load_model(
    filename: str,
    config_path: str = 'config.yaml'
):
    """
    Carga un modelo guardado.

    Args:
        filename: Nombre del archivo (ej. 'linear_regression.pkl')
        config_path: Ruta al archivo de configuracion

    Returns:
        Modelo cargado
    """
    # Cargar configuracion
    config = load_config(config_path)

    # Construir ruta
    models_path = config['paths']['models']
    input_path = os.path.join(models_path, filename)

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"No se encontro el modelo: {input_path}")

    # Cargar modelo
    model = joblib.load(input_path)
    print(f"Modelo cargado desde: {input_path}")

    return model


def predict_arima(
    model_fit,
    start: int,
    end: int
) -> np.ndarray:
    """
    Genera predicciones con un modelo ARIMA entrenado.

    Args:
        model_fit: Modelo ARIMA entrenado
        start: Indice inicial de prediccion
        end: Indice final de prediccion

    Returns:
        Array con predicciones
    """
    predictions = model_fit.predict(start=start, end=end)
    return predictions.values


def compare_models(
    metrics_dict: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Compara metricas de multiples modelos.

    Args:
        metrics_dict: Diccionario con {nombre_modelo: {metrica: valor}}

    Returns:
        DataFrame con comparacion de modelos
    """
    df_comparison = pd.DataFrame(metrics_dict).T
    df_comparison = df_comparison.sort_values('mae')

    print("\nComparacion de Modelos:")
    print("=" * 70)
    print(df_comparison.to_string())
    print("=" * 70)

    return df_comparison


def get_feature_importance(
    model: LinearRegression,
    feature_names: list,
    top_n: int = 10
) -> pd.DataFrame:
    """
    Obtiene la importancia de features de un modelo Linear Regression.

    Args:
        model: Modelo Linear Regression entrenado
        feature_names: Lista de nombres de features
        top_n: Numero de features mas importantes a retornar

    Returns:
        DataFrame con features ordenadas por importancia absoluta
    """
    # Obtener coeficientes
    coefficients = model.coef_

    # Crear DataFrame
    df_importance = pd.DataFrame({
        'feature': feature_names,
        'coefficient': coefficients,
        'abs_coefficient': np.abs(coefficients)
    })

    # Ordenar por coeficiente absoluto
    df_importance = df_importance.sort_values('abs_coefficient', ascending=False)

    return df_importance.head(top_n).reset_index(drop=True)


if __name__ == '__main__':
    # Ejemplo de uso
    print("Ejecutando models.py...")
    print("-" * 50)

    # Cargar datos procesados
    import sys
    sys.path.append('..')
    from src.features import load_processed_data

    df = load_processed_data(config_path='../config.yaml')

    # Split temporal
    config = load_config(config_path='../config.yaml')
    train_df, val_df, test_df = split_data(
        df,
        train_size=config['split']['train_size'],
        val_size=config['split']['val_size'],
        test_size=config['split']['test_size']
    )

    # Preparar datos para Linear Regression
    X_train, y_train = prepare_features_target(train_df)
    X_val, y_val = prepare_features_target(val_df)
    X_test, y_test = prepare_features_target(test_df)

    # Entrenar Linear Regression
    lr_model, lr_metrics = train_linear_regression(X_train, y_train, X_val, y_val)

    # Evaluar en test
    y_test_pred_lr = lr_model.predict(X_test)
    lr_test_metrics = evaluate_model(y_test, y_test_pred_lr, 'Linear Regression (Test)')

    # Feature importance
    print("\nTop 10 Features mas importantes:")
    print("-" * 50)
    importance = get_feature_importance(lr_model, X_train.columns.tolist(), top_n=10)
    print(importance)

    # Guardar modelo
    save_model(lr_model, 'linear_regression.pkl', config_path='../config.yaml')


# ============================================================================
# MODELOS AVANZADOS (Notebook 05)
# ============================================================================

def train_ridge_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    alphas: list = None
) -> Tuple[object, Dict[str, float]]:
    """
    Entrena Ridge Regression con Grid Search para encontrar mejor alpha.

    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
        X_val: Features de validacion
        y_val: Target de validacion
        alphas: Lista de alphas a probar (default: [0.01, 0.1, 1, 10, 100, 1000])

    Returns:
        Tupla (modelo_entrenado, metricas_dict)
    """
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GridSearchCV, TimeSeriesSplit

    if alphas is None:
        alphas = [0.01, 0.1, 1, 10, 100, 1000]

    print("Entrenando Ridge Regression con Grid Search...")
    print(f"Alphas a probar: {alphas}")

    ridge = Ridge()
    param_grid = {'alpha': alphas}
    tscv = TimeSeriesSplit(n_splits=5)

    grid_search = GridSearchCV(
        ridge,
        param_grid,
        cv=tscv,
        scoring='neg_mean_absolute_error',
        n_jobs=-1
    )

    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_

    print(f"Mejor alpha: {grid_search.best_params_['alpha']}")
    print(f"Mejor MAE (CV): ${-grid_search.best_score_:.4f} USD/lb")

    # Evaluar en validacion
    y_val_pred = best_model.predict(X_val)
    metrics = evaluate_model(y_val, y_val_pred, 'Ridge Regression')

    return best_model, metrics


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_estimators: int = 500,
    learning_rate: float = 0.01,
    max_depth: int = 5
) -> Tuple[object, Dict[str, float]]:
    """
    Entrena modelo XGBoost para regresion.

    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
        X_val: Features de validacion
        y_val: Target de validacion
        n_estimators: Numero de arboles
        learning_rate: Tasa de aprendizaje
        max_depth: Profundidad maxima de arboles

    Returns:
        Tupla (modelo_entrenado, metricas_dict)
    """
    try:
        import xgboost as xgb
    except ImportError:
        raise ImportError("XGBoost no instalado. Ejecutar: pip install xgboost")

    print("Entrenando XGBoost...")

    model = xgb.XGBRegressor(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        early_stopping_rounds=50,
        verbose=False
    )

    # Evaluar
    y_val_pred = model.predict(X_val)
    metrics = evaluate_model(y_val, y_val_pred, 'XGBoost')

    return model, metrics


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_estimators: int = 300,
    max_depth: int = 10
) -> Tuple[object, Dict[str, float]]:
    """
    Entrena modelo Random Forest para regresion.

    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
        X_val: Features de validacion
        y_val: Target de validacion
        n_estimators: Numero de arboles
        max_depth: Profundidad maxima

    Returns:
        Tupla (modelo_entrenado, metricas_dict)
    """
    from sklearn.ensemble import RandomForestRegressor

    print("Entrenando Random Forest...")

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    # Evaluar
    y_val_pred = model.predict(X_val)
    metrics = evaluate_model(y_val, y_val_pred, 'Random Forest')

    return model, metrics


def train_sarimax(
    y_train: pd.Series,
    X_train: pd.DataFrame,
    y_val: pd.Series,
    X_val: pd.DataFrame,
    top_n_features: int = 10,
    auto_arima: bool = True
) -> Tuple[object, Dict[str, float], list]:
    """
    Entrena modelo SARIMAX (ARIMA con variables exogenas).

    Args:
        y_train: Target de entrenamiento
        X_train: Features de entrenamiento
        y_val: Target de validacion
        X_val: Features de validacion
        top_n_features: Numero de features exogenas a usar
        auto_arima: Si usar auto_arima para encontrar mejor orden

    Returns:
        Tupla (modelo_entrenado, metricas_dict, features_exogenas_usadas)
    """
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        import pmdarima as pm
    except ImportError:
        raise ImportError("pmdarima no instalado. Ejecutar: pip install pmdarima")

    print("Entrenando SARIMAX...")

    # Seleccionar top features por correlacion
    correlations = X_train.corrwith(y_train).abs().sort_values(ascending=False)
    top_features = correlations.head(top_n_features).index.tolist()

    print(f"\nTop {top_n_features} features exogenas seleccionadas:")
    for i, feat in enumerate(top_features, 1):
        print(f"  {i}. {feat} (corr: {correlations[feat]:.4f})")

    exog_train = X_train[top_features]
    exog_val = X_val[top_features]

    if auto_arima:
        print("\nBuscando mejor orden con auto_arima...")
        auto_model = pm.auto_arima(
            y_train,
            exogenous=exog_train,
            start_p=1, start_q=1,
            max_p=7, max_q=7,
            d=1,
            seasonal=False,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )
        order = auto_model.order
        print(f"Mejor orden: {order}")
    else:
        order = (0, 1, 0)  # Default simple

    # Entrenar SARIMAX
    model = SARIMAX(y_train, exog=exog_train, order=order)
    model_fit = model.fit(disp=False)

    # Evaluar
    y_val_pred = model_fit.forecast(steps=len(y_val), exog=exog_val)
    metrics = evaluate_model(y_val, y_val_pred, 'SARIMAX')

    return model_fit, metrics, top_features


def get_feature_importance_tree(
    model: object,
    feature_names: list,
    top_n: int = 20
) -> pd.DataFrame:
    """
    Obtiene feature importance de modelos basados en arboles (XGBoost, RF).

    Args:
        model: Modelo entrenado (XGBoost o RandomForest)
        feature_names: Lista de nombres de features
        top_n: Numero de top features a retornar

    Returns:
        DataFrame con features y su importancia
    """
    importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    return importance.head(top_n)


def compare_models(
    models_dict: Dict[str, Tuple[object, Dict]],
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> pd.DataFrame:
    """
    Compara multiples modelos en el test set.

    Args:
        models_dict: Diccionario {nombre_modelo: (modelo, metricas_val)}
        X_test: Features de test
        y_test: Target de test

    Returns:
        DataFrame con comparacion de metricas
    """
    results = []

    for name, (model, val_metrics) in models_dict.items():
        # Predecir en test
        if 'SARIMAX' in name or 'ARIMA' in name:
            # Modelos de series temporales necesitan tratamiento especial
            continue  # Skip por ahora, requiere manejo especial

        y_pred = model.predict(X_test)

        # Calcular metricas
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        results.append({
            'Modelo': name,
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2,
            'MAPE (%)': mape
        })

    df_results = pd.DataFrame(results).sort_values('R2', ascending=False)
    return df_results