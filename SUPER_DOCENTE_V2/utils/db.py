import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. CONEXIÓN MAESTRA ---
def conectar_db():
    """
    Establece el puente con Google Sheets.
    Si falla aquí, el sistema no arranca.
    """
    if "GSHEETS_URL" not in st.secrets:
        st.error("⚠️ Error Crítico: No se encontró 'GSHEETS_URL' en los secrets.toml")
        st.stop()
    
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"⚠️ Error conectando a la Nube: {e}")
        return None

# --- 2. CARGA DE DATOS (CON CACHÉ) ---
# Descarga la lista de profes y alumnos una vez cada 10 minutos (600s)
# para que Google no nos bloquee por exceso de tráfico.
@st.cache_data(ttl=600)
def cargar_datos_maestros(_conn):
    url = st.secrets["GSHEETS_URL"]
    try:
        # Cargamos los usuarios (profesores)
        profes = _conn.read(spreadsheet=url, worksheet="USUARIOS")
        
        # Cargamos la matrícula (alumnos) - REGLA DE ORO: Nombre exacto
        matricula = _conn.read(spreadsheet=url, worksheet="MATRICULA_GLOBAL")
        
        return profes, matricula
    except Exception as e:
        # Si falla, devolvemos tablas vacías para que no explote la app
        st.warning(f"No se pudieron cargar los datos maestros: {e}")
        return pd.DataFrame(), pd.DataFrame()
