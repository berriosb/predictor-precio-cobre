"""
Aplicación Web - Predictor de Precio del Cobre
Streamlit App para demostrar el modelo Ridge Regression entrenado

Autor: Bastian Berrios
GitHub: @BastianBerriosalarcon
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Obtener directorio base del script
BASE_DIR = Path(__file__).parent

# Configuración de página
st.set_page_config(
    page_title="Predictor Precio Cobre",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-top: 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
    }
    .prediction-box {
        background: linear-gradient(135deg, #2E86AB 0%, #A23B72 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================
# FUNCIONES DE CARGA
# ============================

@st.cache_data
def load_data():
    """Cargar datos procesados con features"""
    df = pd.read_csv(BASE_DIR / 'data' / 'processed' / 'precio_cobre_features.csv')
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

@st.cache_resource
def load_model():
    """Cargar modelo Ridge entrenado"""
    with open(BASE_DIR / 'models' / 'ridge_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

@st.cache_data
def load_feature_names():
    """Cargar nombres de features"""
    with open(BASE_DIR / 'models' / 'feature_names.pkl', 'rb') as f:
        feature_names = pickle.load(f)
    return feature_names

@st.cache_data
def load_metrics():
    """Cargar métricas del modelo"""
    import json
    with open(BASE_DIR / 'models' / 'results_summary.json', 'r') as f:
        metrics = json.load(f)
    return metrics

# ============================
# CARGA DE DATOS
# ============================

try:
    df = load_data()
    model = load_model()
    feature_names = load_feature_names()
    metrics = load_metrics()

    # Obtener último registro
    last_row = df.iloc[-1]
    last_date = last_row['fecha']
    last_price = last_row['precio']

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
    st.stop()

# ============================
# HEADER
# ============================

st.markdown('<p class="main-header">Predictor de Precio del Cobre</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Modelo de Machine Learning con Ridge Regression | R² = 99.14%</p>', unsafe_allow_html=True)

# Advertencia sobre limitaciones del modelo
st.warning("""
**Limitaciones del Modelo Predictivo:**

Este modelo Ridge Regression fue entrenado con datos históricos y funciona mejor para **predicciones de corto plazo en condiciones normales de mercado**. Sin embargo:

- **No predice eventos extremos:** Caídas súbitas causadas por crisis económicas, cambios geopolíticos o shocks de demanda no pueden anticiparse sin datos externos (noticias, indicadores macro).
- **Alta autocorrelación:** El modelo asume que el precio futuro será similar al reciente. Si hay un cambio brusco en los últimos días, las predicciones partirán de ese último valor conocido.
- **Sin variables exógenas:** No incorpora factores como tipo de cambio USD, tasas de interés, inventarios globales o sentiment de noticias.
- **Datos históricos:** Las predicciones se basan en el último precio registrado en el dataset. Si el mercado cambió recientemente, actualizar los datos mejora la precisión.

**Recomendación:** Usa este modelo como referencia de tendencia, no como única fuente para decisiones financieras. Complementa con análisis fundamental y noticias del mercado.
""")

st.markdown("---")

# ============================
# SIDEBAR
# ============================

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Copper_cathode.jpg/300px-Copper_cathode.jpg",
                 caption="Cátodo de cobre puro", use_container_width=True)

st.sidebar.header("Información del Modelo")
st.sidebar.metric("R² Score", f"{metrics.get('test_r2', 0):.4f}")
st.sidebar.metric("MAE", f"${metrics.get('test_mae', 0):.4f} USD/lb")
st.sidebar.metric("RMSE", f"${metrics.get('test_rmse', 0):.4f} USD/lb")
st.sidebar.metric("MAPE", f"{metrics.get('test_mape', 0):.2f}%")

st.sidebar.markdown("---")
st.sidebar.header("Datos del Modelo")
st.sidebar.write(f"**Total registros:** {len(df):,}")
st.sidebar.write(f"**Features:** {metrics.get('num_features', 42)}")
st.sidebar.write(f"**Periodo:** 2010 - 2025")
st.sidebar.write(f"**Test size:** {metrics.get('test_size', 0):,} registros")

st.sidebar.markdown("---")
st.sidebar.markdown("""
### Enlaces
- [GitHub Repo](https://github.com/BastianBerriosalarcon)
- [LinkedIn](https://linkedin.com/in/bastian-berrios)
- [Documentación](https://github.com)
""")

# ============================
# MAIN CONTENT
# ============================

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["Predicción", "Histórico", "Análisis", "Sobre el Modelo"])

# ============================
# TAB 1: PREDICCIÓN
# ============================

with tab1:
    st.header("Predicción del Precio del Cobre")

    # Selector de horizonte de predicción
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Último Precio Registrado")
        st.metric(
            label=f"Fecha: {last_date.strftime('%Y-%m-%d')}",
            value=f"${last_price:.4f} USD/lb"
        )
    with col2:
        horizon_days = st.selectbox(
            "Horizonte de predicción",
            options=[1, 3, 7, 14, 30],
            index=0,
            help="Número de días a predecir hacia adelante"
        )

    st.markdown("---")

    # Función para generar predicciones iterativas
    def predict_multi_step(model, df, feature_names, n_days):
        """
        Genera predicciones para múltiples días hacia adelante.
        Usa predicciones anteriores para generar features de los siguientes días.
        """
        predictions = []
        dates = []
        current_data = df.copy()

        for day in range(n_days):
            # Obtener última fila
            last_row = current_data.iloc[-1:].copy()

            # Predecir
            X = last_row[feature_names].values
            pred = model.predict(X)[0]
            predictions.append(pred)

            # Calcular fecha de predicción
            next_date = pd.to_datetime(last_row['fecha'].values[0]) + timedelta(days=1)
            dates.append(next_date)

            # Crear nueva fila con predicción (para siguiente iteración)
            new_row = last_row.copy()
            new_row['fecha'] = next_date
            new_row['precio'] = pred

            # Actualizar features básicas que dependen del precio
            if len(current_data) > 0:
                prev_price = current_data.iloc[-1]['precio']
                new_row['price_pct_change'] = (pred - prev_price) / prev_price
                new_row['lag_1'] = prev_price
                if len(current_data) > 1:
                    new_row['lag_2'] = current_data.iloc[-2]['precio']
                if len(current_data) > 2:
                    new_row['lag_3'] = current_data.iloc[-3]['precio']
                if len(current_data) > 6:
                    new_row['lag_7'] = current_data.iloc[-7]['precio']
                    new_row['rolling_mean_7'] = current_data.iloc[-6:]['precio'].mean()

            # Agregar nueva fila al dataset
            current_data = pd.concat([current_data, new_row], ignore_index=True)

        return predictions, dates

    # Generar predicciones
    with st.spinner(f'Generando predicciones para los próximos {horizon_days} días...'):
        predictions, pred_dates = predict_multi_step(model, df, feature_names, horizon_days)

    # Calcular intervalos de confianza
    rmse = metrics.get('test_rmse', 0.0345)

    # El intervalo crece con el horizonte (más incertidumbre a futuro)
    lower_bounds = [p - 2 * rmse * np.sqrt(i+1) for i, p in enumerate(predictions)]
    upper_bounds = [p + 2 * rmse * np.sqrt(i+1) for i, p in enumerate(predictions)]

    # Métricas principales
    st.subheader(f"Predicciones para los próximos {horizon_days} días")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Día 1",
            f"${predictions[0]:.4f}",
            delta=f"{((predictions[0] - last_price) / last_price * 100):+.2f}%"
        )

    with col2:
        last_pred = predictions[-1]
        st.metric(
            f"Día {horizon_days}",
            f"${last_pred:.4f}",
            delta=f"{((last_pred - last_price) / last_price * 100):+.2f}%"
        )

    with col3:
        avg_pred = np.mean(predictions)
        st.metric(
            "Precio Promedio",
            f"${avg_pred:.4f}"
        )

    with col4:
        price_range = max(predictions) - min(predictions)
        st.metric(
            "Rango de Variación",
            f"${price_range:.4f}"
        )

    st.markdown("---")

    # Gráfico de predicciones con intervalo de confianza
    st.subheader("Proyección Temporal")

    fig_forecast = go.Figure()

    # Histórico reciente (últimos 30 días)
    recent_df = df.tail(30)
    fig_forecast.add_trace(go.Scatter(
        x=recent_df['fecha'],
        y=recent_df['precio'],
        mode='lines',
        name='Histórico',
        line=dict(color='#2E86AB', width=2),
        hovertemplate='<b>Fecha:</b> %{x}<br><b>Precio:</b> $%{y:.4f}<extra></extra>'
    ))

    # Predicciones
    fig_forecast.add_trace(go.Scatter(
        x=pred_dates,
        y=predictions,
        mode='lines+markers',
        name='Predicción',
        line=dict(color='#F18F01', width=3, dash='dash'),
        marker=dict(size=8),
        hovertemplate='<b>Fecha:</b> %{x}<br><b>Precio:</b> $%{y:.4f}<extra></extra>'
    ))

    # Intervalo de confianza
    fig_forecast.add_trace(go.Scatter(
        x=pred_dates + pred_dates[::-1],
        y=upper_bounds + lower_bounds[::-1],
        fill='toself',
        fillcolor='rgba(248, 143, 1, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Intervalo 95%',
        hoverinfo='skip'
    ))

    # Línea vertical separadora
    fig_forecast.add_vline(
        x=last_date.to_pydatetime(),
        line_dash="dot",
        line_color="gray"
    )

    fig_forecast.update_layout(
        title=f"Predicción del Precio del Cobre - Próximos {horizon_days} días",
        xaxis_title="Fecha",
        yaxis_title="Precio (USD/lb)",
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_forecast, use_container_width=True)

    # Tabla de predicciones detallada
    st.subheader("Tabla de Predicciones Detalladas")

    pred_df = pd.DataFrame({
        'Fecha': [d.strftime('%Y-%m-%d') for d in pred_dates],
        'Predicción (USD/lb)': [f'${p:.4f}' for p in predictions],
        'Límite Inferior': [f'${lb:.4f}' for lb in lower_bounds],
        'Límite Superior': [f'${ub:.4f}' for ub in upper_bounds],
        'Cambio vs Hoy': [f'{((p - last_price) / last_price * 100):+.2f}%' for p in predictions]
    })

    st.dataframe(pred_df, use_container_width=True, hide_index=True)

    # Interpretación
    st.info(f"""
    **Interpretación:**
    - Se proyecta el precio del cobre para los próximos **{horizon_days} días** basándose en tendencias históricas
    - Predicción para mañana: **${predictions[0]:.4f} USD/lb** ({((predictions[0] - last_price) / last_price * 100):+.2f}% vs último dato registrado)
    - Predicción día {horizon_days}: **${predictions[-1]:.4f} USD/lb** ({((predictions[-1] - last_price) / last_price * 100):+.2f}% vs último dato registrado)
    - El intervalo de confianza se amplía con el horizonte temporal (mayor incertidumbre a futuro)
    - **Nota**: Predicciones de largo plazo (>7 días) tienen mayor incertidumbre. Estas proyecciones asumen condiciones normales de mercado sin shocks externos.
    """)

    # Última actualización del dataset
    st.caption(f"**Último dato registrado en el dataset:** {last_date.strftime('%Y-%m-%d')} | Precio: ${last_price:.4f} USD/lb")

# ============================
# TAB 2: HISTÓRICO
# ============================

with tab2:
    st.header("Serie Temporal Histórica")

    # Selector de rango de fechas
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha inicio", value=df['fecha'].min(),
                                   min_value=df['fecha'].min(), max_value=df['fecha'].max())
    with col2:
        end_date = st.date_input("Fecha fin", value=df['fecha'].max(),
                                min_value=df['fecha'].min(), max_value=df['fecha'].max())

    # Filtrar datos
    mask = (df['fecha'] >= pd.Timestamp(start_date)) & (df['fecha'] <= pd.Timestamp(end_date))
    df_filtered = df[mask]

    # Gráfico interactivo
    fig_historical = go.Figure()

    fig_historical.add_trace(go.Scatter(
        x=df_filtered['fecha'],
        y=df_filtered['precio'],
        mode='lines',
        name='Precio del Cobre',
        line=dict(color='#2E86AB', width=2),
        hovertemplate='<b>Fecha:</b> %{x}<br><b>Precio:</b> $%{y:.4f} USD/lb<extra></extra>'
    ))

    # Agregar media móvil 30 días si existe
    if 'rolling_mean_30' in df_filtered.columns:
        fig_historical.add_trace(go.Scatter(
            x=df_filtered['fecha'],
            y=df_filtered['rolling_mean_30'],
            mode='lines',
            name='Media Móvil 30 días',
            line=dict(color='#F18F01', width=1, dash='dash'),
            hovertemplate='<b>MA30:</b> $%{y:.4f} USD/lb<extra></extra>'
        ))

    fig_historical.update_layout(
        title=f"Precio del Cobre: {start_date} a {end_date}",
        xaxis_title="Fecha",
        yaxis_title="Precio (USD/lb)",
        height=500,
        hovermode='x unified'
    )

    st.plotly_chart(fig_historical, use_container_width=True)

    # Estadísticas del período
    st.subheader("Estadísticas del Período Seleccionado")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio Promedio", f"${df_filtered['precio'].mean():.4f}")
    col2.metric("Precio Máximo", f"${df_filtered['precio'].max():.4f}")
    col3.metric("Precio Mínimo", f"${df_filtered['precio'].min():.4f}")
    col4.metric("Volatilidad (std)", f"${df_filtered['precio'].std():.4f}")

# ============================
# TAB 3: ANÁLISIS
# ============================

with tab3:
    st.header("Análisis de Features y Rendimiento")

    # Top features
    st.subheader("Top 10 Features Más Importantes")

    # Obtener coeficientes del modelo
    feature_importance = pd.DataFrame({
        'Feature': feature_names,
        'Coeficiente': model.coef_
    })
    feature_importance['Importancia_Abs'] = feature_importance['Coeficiente'].abs()
    feature_importance = feature_importance.sort_values('Importancia_Abs', ascending=False)

    top_10 = feature_importance.head(10)

    fig_features = go.Figure()

    colors = ['green' if c > 0 else 'red' for c in top_10['Coeficiente']]

    fig_features.add_trace(go.Bar(
        y=top_10['Feature'],
        x=top_10['Coeficiente'],
        orientation='h',
        marker_color=colors,
        text=[f'{c:.4f}' for c in top_10['Coeficiente']],
        textposition='auto',
    ))

    fig_features.update_layout(
        title="Coeficientes del Modelo Ridge (Top 10 Features)",
        xaxis_title="Coeficiente",
        yaxis_title="Feature",
        height=500,
        yaxis={'categoryorder':'total ascending'}
    )

    st.plotly_chart(fig_features, use_container_width=True)

    st.markdown("""
    **Interpretación:**
    - **Verde**: Feature con impacto positivo en el precio
    - **Rojo**: Feature con impacto negativo en el precio
    - Los lags (precios pasados) dominan la predicción, confirmando la alta autocorrelación del mercado
    """)

    # Distribución de precio
    st.subheader("Distribución del Precio del Cobre")

    fig_dist = go.Figure()

    fig_dist.add_trace(go.Histogram(
        x=df['precio'],
        nbinsx=50,
        marker_color='#2E86AB',
        opacity=0.7,
        name='Frecuencia'
    ))

    fig_dist.update_layout(
        title="Histograma de Precios (2010-2025)",
        xaxis_title="Precio (USD/lb)",
        yaxis_title="Frecuencia",
        height=400
    )

    st.plotly_chart(fig_dist, use_container_width=True)

# ============================
# TAB 4: SOBRE EL MODELO
# ============================

with tab4:
    st.header("Información del Proyecto")

    st.markdown("""
    ## Objetivo del Proyecto

    Predecir el precio del cobre (USD/lb) utilizando datos históricos y técnicas de Machine Learning.

    ## Dataset

    - **Fuente:** Yahoo Finance (ticker `HG=F` - Copper Futures)
    - **Período:** Mayo 2010 - Octubre 2025 (15+ años)
    - **Registros:** 3,872 datos diarios
    - **Features creadas:** 42 variables predictivas

    ## Modelo Seleccionado: Ridge Regression

    ### Por qué Ridge ganó

    1. **Simplicidad > Complejidad**: Superó a XGBoost, Random Forest y otros modelos complejos
    2. **Relación lineal fuerte**: El precio del cobre tiene memoria extrema (lag_1 correlación = 0.9975)
    3. **Maneja multicolinealidad**: Regularización L2 controla features correlacionadas
    4. **Regularización óptima**: Alpha = 0.01 (muy leve, casi Linear Regression)

    ### Métricas de Rendimiento

    | Métrica | Valor | Interpretación |
    |---------|-------|----------------|
    | **R² Score** | 0.9914 | 99.14% de la varianza explicada |
    | **MAE** | $0.0173 | Error promedio de 1.7 centavos |
    | **RMSE** | $0.0345 | Desviación típica del error |
    | **MAPE** | 0.38% | Error porcentual medio |

    ## Pipeline de Feature Engineering

    Se crearon **42 features** organizadas en 7 grupos:

    1. **Estacionalidad** (6): mes, trimestre, encoding cíclico
    2. **Volatilidad** (6): retornos, desviación estándar móvil
    3. **Tendencia** (7): medias móviles, momentum
    4. **Outliers** (4): Z-score, flags de movimientos extremos
    5. **Lags** (6): precios pasados (1, 2, 3, 7, 14, 30 días)
    6. **Estadísticas** (6): dispersión, rangos, posición relativa
    7. **Intrasemanal** (7): día de semana, inicio/fin de mes

    ## Resultados Destacados

    - **Ridge Regression** superó a 5 modelos competidores
    - **Feature más importante:** `lag_1` (precio de ayer)
    - **Autocorrelación extrema:** El mercado del cobre tiene "memoria perfecta"
    - **Modelo production-ready:** Listo para deployment

    ## Tecnologías Utilizadas

    - **Python 3.8+**
    - **scikit-learn** (Ridge Regression)
    - **pandas, numpy** (manipulación de datos)
    - **Streamlit** (aplicación web)
    - **Plotly** (visualizaciones interactivas)

    ## Autor

    **Bastian Berrios**
    - GitHub: [@BastianBerriosalarcon](https://github.com/BastianBerriosalarcon)
    - Email: bastianberrios.a@gmail.com

    ## Licencia

    MIT License - Ver repositorio para más detalles

    ---

    *Proyecto desarrollado como parte de portafolio profesional de Data Science*
    """)

# ============================
# FOOTER
# ============================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Predictor de Precio del Cobre | Desarrollado por Bastian Berrios</p>
    <p>© 2025 | <a href='https://github.com/BastianBerriosalarcon'>GitHub</a> | Versión 1.0</p>
</div>
""", unsafe_allow_html=True)
