import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="🌇 Análisis de Sensores - Mi Ciudad",
    page_icon="🌿",
    layout="wide"
)

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            color: #1E1E1E;
            background-color: #F7F9FB;
        }

        .main {
            padding: 2rem 3rem;
            background: #FFFFFF;
            border-radius: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }

        h1, h2, h3 {
            color: #1B3C59;
            font-weight: 600;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #E9F5EE;
            color: #1B3C59;
            border-radius: 10px;
            padding: 10px 16px;
            font-weight: 500;
        }

        .stTabs [aria-selected="true"] {
            background-color: #4BB47E !important;
            color: white !important;
        }

        .stButton>button {
            background: linear-gradient(90deg, #4BB47E, #78C2AD);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
        }

        .stDownloadButton>button {
            background: #1B3C59;
            color: white;
            border-radius: 8px;
            padding: 8px 18px;
        }

        .stAlert {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- TÍTULO PRINCIPAL ---
st.title("🌇 Análisis de Sensores en Mi Ciudad")
st.markdown("""
Bienvenido al panel de análisis de datos de sensores urbanos.  
Esta herramienta permite explorar, visualizar y filtrar información recolectada en distintos puntos de la ciudad 🌿.
""")

# --- MAPA EAFIT ---
st.subheader("📍 Ubicación del Sensor - Universidad EAFIT")
eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783]
})
st.map(eafit_location, zoom=15)

# --- SUBIR ARCHIVO ---
st.markdown("### 📂 Cargar Archivo CSV")
uploaded_file = st.file_uploader("Seleccione su archivo de datos", type=['csv'])

# --- ANÁLISIS ---
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Renombrar columna variable
        if 'Time' in df.columns:
            other_cols = [c for c in df.columns if c != 'Time']
            if len(other_cols) > 0:
                df = df.rename(columns={other_cols[0]: 'variable'})
            df['Time'] = pd.to_datetime(df['Time'])
            df = df.set_index('Time')
        else:
            df = df.rename(columns={df.columns[0]: 'variable'})

        # --- TABS MODERNAS ---
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Visualización", "📊 Estadísticas", "🎚️ Filtros", "🗺️ Información"
        ])

        # --- TAB 1: VISUALIZACIÓN ---
        with tab1:
            st.markdown("### Visualización Interactiva")
            chart_type = st.selectbox("Tipo de gráfico:", ["Línea", "Área", "Barra"], index=0)

            if chart_type == "Línea":
                st.line_chart(df["variable"], height=300)
            elif chart_type == "Área":
                st.area_chart(df["variable"], height=300)
            else:
                st.bar_chart(df["variable"], height=300)

            if st.checkbox("👁️ Mostrar datos crudos"):
                st.dataframe(df)

        # --- TAB 2: ESTADÍSTICAS ---
        with tab2:
            st.markdown("### Resumen Estadístico 📊")
            stats = df["variable"].describe()
            col1, col2 = st.columns([1, 1])

            with col1:
                st.dataframe(stats)

            with col2:
                st.metric("Promedio", f"{stats['mean']:.2f}")
                st.metric("Máximo", f"{stats['max']:.2f}")
                st.metric("Mínimo", f"{stats['min']:.2f}")
                st.metric("Desviación Estándar", f"{stats['std']:.2f}")

        # --- TAB 3: FILTROS ---
        with tab3:
            st.markdown("### 🎚️ Filtros Interactivos")
            min_val, max_val = df["variable"].min(), df["variable"].max()
            mean_val = df["variable"].mean()

            if min_val == max_val:
                st.warning(f"⚠️ Todos los valores son iguales: {min_val:.2f}")
                st.info("No se pueden aplicar filtros sin variación en los datos.")
                st.dataframe(df)
            else:
                c1, c2 = st.columns(2)

                with c1:
                    min_slider = st.slider("Valor mínimo", min_val, max_val, mean_val, key="min_slider")
                    filtered_min = df[df["variable"] > min_slider]
                    st.dataframe(filtered_min)

                with c2:
                    max_slider = st.slider("Valor máximo", min_val, max_val, mean_val, key="max_slider")
                    filtered_max = df[df["variable"] < max_slider]
                    st.dataframe(filtered_max)

                st.download_button(
                    label="⬇️ Descargar CSV filtrado",
                    data=filtered_min.to_csv().encode('utf-8'),
                    file_name="datos_filtrados.csv",
                    mime="text/csv"
                )

        # --- TAB 4: INFORMACIÓN DEL SITIO ---
        with tab4:
            st.markdown("### 🗺️ Información del Sitio de Medición")
            col1, col2 = st.columns(2)

            with col1:
                st.write("#### 📌 Ubicación")
                st.write("- **Lugar:** Universidad EAFIT")
                st.write("- **Latitud:** 6.2006")
                st.write("- **Longitud:** -75.5783")
                st.write("- **Altitud:** ~1.495 m.s.n.m")

            with col2:
                st.write("#### 🔧 Detalles del Sensor")
                st.write("- **Tipo:** ESP32")
                st.write("- **Variable medida:** Según configuración")
                st.write("- **Frecuencia:** Configurable")
                st.write("- **Contexto:** Campus universitario 🌳")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {str(e)}")
        st.info("Asegúrese de que el archivo CSV tenga una columna válida con datos.")
else:
    st.warning("📄 Por favor, cargue un archivo CSV para comenzar el análisis.")

# --- FOOTER ---
st.markdown("""
---
🌱 **Desarrollado para el análisis de datos de sensores urbanos**  
📍 *Universidad EAFIT - Medellín, Colombia*  
""")
