import pandas as pd
import streamlit as st
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="🌇 Sensores Urbanos",
    page_icon="🌿",
    layout="wide"
)

# --- ESTILO VISUAL PERSONALIZADO ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
            background-color: #F5F7FA;
            color: #1E1E1E;
        }

        h1, h2, h3, h4 {
            color: #102A43;
            font-weight: 600;
        }

        .block-container {
            padding: 2rem 3rem;
        }

        /* Cards */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 20px;
            box-shadow: 0px 6px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #E5F6EE;
            color: #1E3A34;
            border-radius: 12px;
            padding: 10px 16px;
            font-weight: 500;
            transition: all 0.3s;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #38B2AC, #4FD1C5);
            color: white !important;
            transform: scale(1.05);
        }

        /* Botones */
        .stButton>button, .stDownloadButton>button {
            background: linear-gradient(90deg, #38B2AC, #4FD1C5);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.4rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .stButton>button:hover, .stDownloadButton>button:hover {
            background: linear-gradient(90deg, #319795, #2C7A7B);
            transform: scale(1.03);
        }

        /* Upload box */
        .uploadedFile {
            border: 2px dashed #4FD1C5;
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            background-color: #F0FCF9;
            margin-bottom: 20px;
        }

        /* Alertas */
        .stAlert {
            border-radius: 12px;
        }

        /* Scrollbars bonitos */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-thumb {
            background: #A0AEC0;
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("""
# 🌆 Análisis de Sensores Urbanos  
Explora y analiza datos recolectados en diferentes puntos de la ciudad.  
**Visualiza, filtra y entiende el pulso ambiental de Medellín.**
""")

# --- MAPA EN CARD ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📍 Ubicación del Sensor - Universidad EAFIT")

eafit_location = pd.DataFrame({
    'lat': [6.2006],
    'lon': [-75.5783]
})
st.map(eafit_location, zoom=15)
st.markdown('</div>', unsafe_allow_html=True)

# --- SUBIR ARCHIVO ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📂 Subir Archivo CSV para Análisis")
uploaded_file = st.file_uploader("Selecciona un archivo CSV con tus datos de sensores", type=['csv'])
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        if 'Time' in df.columns:
            other_cols = [c for c in df.columns if c != 'Time']
            if len(other_cols) > 0:
                df = df.rename(columns={other_cols[0]: 'variable'})
            df['Time'] = pd.to_datetime(df['Time'])
            df = df.set_index('Time')
        else:
            df = df.rename(columns={df.columns[0]: 'variable'})

        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Visualización", "📊 Estadísticas", "🎚️ Filtros", "🗺️ Información"
        ])

        # VISUALIZACIÓN
        with tab1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🌈 Visualización de Datos")
            chart_type = st.radio("Tipo de gráfico:", ["Línea", "Área", "Barra"], horizontal=True)
            
            if chart_type == "Línea":
                st.line_chart(df["variable"], height=300)
            elif chart_type == "Área":
                st.area_chart(df["variable"], height=300)
            else:
                st.bar_chart(df["variable"], height=300)

            if st.checkbox("👁️ Mostrar datos crudos"):
                st.dataframe(df)
            st.markdown('</div>', unsafe_allow_html=True)

        # ESTADÍSTICAS
        with tab2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📊 Estadísticas Generales")
            stats = df["variable"].describe()
            c1, c2 = st.columns(2)
            with c1:
                st.dataframe(stats)
            with c2:
                st.metric("Promedio", f"{stats['mean']:.2f}")
                st.metric("Máximo", f"{stats['max']:.2f}")
                st.metric("Mínimo", f"{stats['min']:.2f}")
                st.metric("Desviación Estándar", f"{stats['std']:.2f}")
            st.markdown('</div>', unsafe_allow_html=True)

        # FILTROS
        with tab3:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🎚️ Filtros Interactivos")

            min_val, max_val = df["variable"].min(), df["variable"].max()
            mean_val = df["variable"].mean()

            if min_val == max_val:
                st.warning(f"⚠️ Todos los valores son iguales: {min_val:.2f}")
                st.info("No se pueden aplicar filtros si no hay variación en los datos.")
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
            st.markdown('</div>', unsafe_allow_html=True)

        # INFORMACIÓN
        with tab4:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🗺️ Detalles del Sitio")
            col1, col2 = st.columns(2)
            with col1:
                st.write("#### 📌 Ubicación")
                st.write("- **Lugar:** Universidad EAFIT")
                st.write("- **Latitud:** 6.2006")
                st.write("- **Longitud:** -75.5783")
                st.write("- **Altitud:** ~1.495 m.s.n.m")
            with col2:
                st.write("#### 🔧 Sensor")
                st.write("- **Tipo:** ESP32")
                st.write("- **Variable medida:** Configurable")
                st.write("- **Frecuencia:** Dependiente del proyecto")
                st.write("- **Entorno:** Campus universitario 🌳")
            st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocurrió un error: {str(e)}")
        st.info("Verifica que el CSV tenga columnas válidas para análisis.")
else:
    st.warning("📄 Sube un archivo CSV para comenzar el análisis.")

# FOOTER
st.markdown("""
---
🌱 **Desarrollado con Streamlit** | Universidad EAFIT - Medellín  
💚 Proyecto de Análisis de Datos Ambientales
""")
