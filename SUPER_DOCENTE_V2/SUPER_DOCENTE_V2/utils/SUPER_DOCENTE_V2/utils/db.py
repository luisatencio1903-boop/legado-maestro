import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- CONEXIÓN PRINCIPAL ---
def conectar_db():
    """Establece la conexión con Google Sheets usando st.connection."""
    if "GSHEETS_URL" not in st.secrets:
        st.error("⚠️ Error Crítico: No se encontró 'GSHEETS_URL' en los secrets.")
        st.stop()
    
    try:
        return st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error(f"⚠️ Error conectando a la BD: {e}")
        return None

# --- CARGA DE DATOS MAESTROS (CACHÉ) ---
# Esta función descarga Usuarios y Matrícula una sola vez y los guarda en memoria por 10 min.
@st.cache_data(ttl=600)
def cargar_datos_maestros(_conn):
    url = st.secrets["GSHEETS_URL"]
    try:
        profes = _conn.read(spreadsheet=url, worksheet="USUARIOS")
        # Aseguramos leer la hoja correcta que corregimos en la V13.5
        matricula = _conn.read(spreadsheet=url, worksheet="MATRICULA_GLOBAL")
        return profes, matricula
    except Exception as e:
        st.warning(f"No se pudieron cargar los datos maestros: {e}")
        return pd.DataFrame(), pd.DataFrame()
