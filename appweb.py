import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Configuración página
st.set_page_config(
    page_title="Analizador Visual",
    layout="wide",
    page_icon="📊"
)

# CSS aun no manejamos el css asi que este css esta hecho con la ayuda de ia y videos de youtube
st.markdown("""
<style>
    :root {
        --primary-bg: #1a1a1a;
        --secondary-bg: #1a1a1a;
        --accent: #ff0038;
        --neon-glow: 0 0 10px rgba(255, 0, 56, 0.7);
        --text-primary: #ff0000;
        --text-secondary: #ff3333;
    }

    .stApp {
        background-color: var(--primary-bg);
        color: var(--text-primary);
        font-family: 'Courier New', monospace;
    }

    h1 {
        color: var(--accent) !important;
        text-align: center;
        font-weight: 700;
        letter-spacing: 2px;
        text-shadow: 0 0 8px rgba(255, 0, 56, 0.7);
        border-bottom: 1px solid var(--accent);
        padding-bottom: 12px;
        margin-bottom: 30px;
    }

    h2, h3 {
        border-left: 3px solid var(--accent);
        padding-left: 10px;
        color: var(--text-primary);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(to bottom, #111111, #000000);
        border-right: 1px solid var(--accent);
        box-shadow: var(--neon-glow);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2 {
        color: var(--accent) !important;
        border-bottom: 1px dashed var(--accent);
    }

    [data-testid="stExpander"] {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid #333;
        box-shadow: 0 0 15px rgba(255, 0, 56, 0.3);
        margin: 15px 0;
    }

    [data-testid="stExpander"] details summary {
        background: linear-gradient(to right, #1a1a1a, #2a2a2a) !important;
        color: var(--accent) !important;
        font-weight: bold;
        letter-spacing: 1px;
        border-bottom: 1px solid var(--accent);
    }

    .stButton > button {
        background: linear-gradient(to right, #222, #000);
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 0;
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s;
        box-shadow: var(--neon-glow);
    }

    .stButton > button:hover {
        background: linear-gradient(to right, #000, #222) !important;
        animation: neon-pulse 1.5s infinite;
        transform: translateY(-1px);
    }

    .stPlotlyChart {
        background: rgba(10, 10, 10, 0.7) !important;
        border: 1px solid var(--accent) !important;
        box-shadow: var(--neon-glow);
        padding: 20px;
        margin: 30px 0;
    }

    [data-testid="stDataFrame"] {
        background: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid var(--accent) !important;
        color: var(--text-primary) !important;
    }

    body::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            linear-gradient(rgba(255, 0, 56, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 0, 56, 0.03) 1px, transparent 1px);
        background-size: 20px 20px;
        z-index: -1;
        pointer-events: none;
    }

    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 8px;
        background: #000 !important;
        border-top: 1px solid var(--accent);
        color: var(--accent) !important;
        font-size: 0.8em;
        letter-spacing: 1px;
    }

    ::-webkit-scrollbar {
        width: 8px;
        background: #111;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--accent);
        border-radius: 0;
    }

    @keyframes neon-pulse {
        0%, 100% {
            box-shadow: var(--neon-glow), 0 0 20px rgba(255, 0, 56, 0.3);
        }
        50% {
            box-shadow: 0 0 15px rgba(255, 0, 56, 0.9), 0 0 30px rgba(255, 0, 56, 0.4);
        }
    }
</style>
""", unsafe_allow_html=True)

# Footer futurista
st.markdown("""
<div class="footer">
    SISTEMA DE VISUALIZACIÓN │ v2.4.1 │ ████████████ 87%
</div>
""", unsafe_allow_html=True)


#Clase para manejar los datos 
class DataHandler:
    def __init__(self, custom_url=None):
        self.default_csv_url = "https://datos.gob.cl/dataset/permisos-de-circulacion-12025/resource/346da1c7-5a58-4b25-966e-6c832228cdb3/download/permiso-de-circulacion-2025.csv"
        self.url = custom_url if custom_url else self.default_csv_url

    def get_data(self, limit=1000):
        try:
            if self.url.endswith(".csv"):
                df = pd.read_csv(self.url, sep=";", encoding="latin1")
            elif "datastore_search" in self.url:
                response = requests.get(self.url, timeout=10)
                data = json.loads(response.text)
                records = data["result"]["records"]
                df = pd.DataFrame(records)
            else:
                raise ValueError("Formato de enlace no compatible.")
            
            df.columns = [col.strip().upper() for col in df.columns]

            if "FECHA" in df.columns:
                df["FECHA"] = pd.to_datetime(df["FECHA"], errors='coerce')

            return df.head(limit)
        except Exception as e:
            st.error(f"Error al obtener datos: {str(e)}")
            return pd.DataFrame()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuración Global")

    custom_url = st.text_input("🔗 Enlace personalizado (opcional)", placeholder="https://datos.gob.cl/...")

    limit = st.slider("Límite de registros", 100, 5000, value=1000, step=100)

    if st.button("Cargar Datos", type="primary", key="btn_cargar_datos"):
        with st.spinner("Obteniendo datos..."):
            handler = DataHandler(custom_url if custom_url else None)
            st.session_state.df = handler.get_data(limit=limit)

    st.markdown("---")
    st.markdown(
        """
        ### Cómo usar esta app

        1. Puedes dejar el enlace en blanco o pegar uno de datos.gob.cl.
        2. Una vez pegado el enlace presiona enter
        3. Haz click en **Cargar Datos** para obtener el conjunto de datos.
        4. Selecciona variables y tipo de gráfico.
        5. Haz clic en **Generar Visualización**.
        """
    )

# --- Cargar datos en memoria ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

df = st.session_state.df.copy()

st.header("Appweb Solemne 2 - Taller de Programación")
st.subheader("📋 Datos Crudos con Filtros")
st.dataframe(df, use_container_width=True)

# --- Filtro dinámico ---
if not df.empty:
    st.markdown("---")
    st.subheader("🔍 Búsqueda Avanzada")

    col1, col2 = st.columns(2)

    with col1:
        filtro_columna = st.selectbox(
            "Selecciona columna para filtrar",
            df.columns.tolist(),
            key="select_filtro_col"
        )

    with col2:
        if pd.api.types.is_numeric_dtype(df[filtro_columna]):
            min_val = float(df[filtro_columna].min())
            max_val = float(df[filtro_columna].max())
            val_range = st.slider(
                f"Rango de {filtro_columna}",
                min_val, max_val, (min_val, max_val)
            )
            df_filtrado = df[df[filtro_columna].between(*val_range)]
        else:
            opciones = df[filtro_columna].dropna().unique().tolist()
            seleccion = st.multiselect(
                f"Valores de {filtro_columna}",
                opciones,
                default=opciones,
                key="select_filtro_val"
            )
            df_filtrado = df[df[filtro_columna].isin(seleccion)]

    st.dataframe(df_filtrado, use_container_width=True)
    st.markdown(f"**Registros encontrados:** {len(df_filtrado)}")
    st.markdown("---")
else:
    st.info("Cargue datos para comenzar")
    st.stop()

# --- Visualización ---
cols = df.columns.tolist()

col1, col2, col3 = st.columns([0.4, 0.4, 0.2])

with col1:
    x_var = st.selectbox("📌 Variable Eje X", cols, key="select_x")

with col2:
    y_var = st.selectbox("📌 Variable Eje Y", cols, key="select_y")

with col3:
    chart_type = st.selectbox("📊 Tipo de gráfico", ["Barras", "Líneas", "Torta", "Histograma", "Dispersión"], key="select_chart")

if st.button("Generar Visualización", key="btn_generar_viz"):
    try:
        if chart_type == "Torta":
            fig, ax = plt.subplots(figsize=(8, 8))
            df[x_var].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            ax.set_title(f"Distribución de {x_var}")
            st.pyplot(fig)
        else:
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == "Barras":
                if pd.api.types.is_numeric_dtype(df[y_var]):
                    df.groupby(x_var)[y_var].mean().plot(kind='bar', ax=ax)
                    ax.set_ylabel(f"Promedio de {y_var}")
                else:
                    df[x_var].value_counts().plot(kind='bar', ax=ax)
                    ax.set_ylabel(f"Conteo de {x_var}")

            elif chart_type == "Líneas":
                if pd.api.types.is_numeric_dtype(df[y_var]):
                    df.groupby(x_var)[y_var].mean().sort_index().plot(kind='line', ax=ax, marker='o')
                    ax.set_ylabel(f"Promedio de {y_var}")
                else:
                    df[x_var].value_counts().sort_index().plot(kind='line', ax=ax, marker='o')
                    ax.set_ylabel(f"Conteo de {x_var}")

            elif chart_type == "Histograma":
                if pd.api.types.is_numeric_dtype(df[y_var]):
                    df[y_var].dropna().plot(kind='hist', bins=20, ax=ax)
                    ax.set_xlabel(y_var)
                    ax.set_ylabel("Frecuencia")
                else:
                    st.warning("Seleccione una variable numérica para el histograma")
                    st.stop()

            elif chart_type == "Dispersión":
                if pd.api.types.is_numeric_dtype(df[x_var]) and pd.api.types.is_numeric_dtype(df[y_var]):
                    df.plot(kind='scatter', x=x_var, y=y_var, ax=ax)
                else:
                    st.warning("Seleccione variables numéricas para gráfico de dispersión")
                    st.stop()

            ax.set_title(f"{chart_type}: {x_var} vs {y_var}")
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al generar gráfico: {str(e)}")
