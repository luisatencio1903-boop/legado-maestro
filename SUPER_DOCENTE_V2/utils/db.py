import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
from utils.maletin import persistir_en_dispositivo, recuperar_del_dispositivo

def conectar_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except:
        return None

def guardar_asistencia_hibrida(conn, datos):
    """Decide si guarda en Google o en el teléfono según la señal."""
    URL_HOJA = st.secrets["GSHEETS_URL"]
    hoy = datos["FECHA"]
    
    # 1. Intentar guardado en la Nube (Online)
    try:
        df = conn.read(spreadsheet=URL_HOJA, worksheet="ASISTENCIA", ttl=0)
        # Lógica de guardado normal...
        df_final = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
        conn.update(spreadsheet=URL_HOJA, worksheet="ASISTENCIA", data=df_final)
        st.success("✅ Sincronizado con Dirección (Google Sheets)")
        return True
    except:
        # 2. FALLBACK: Si no hay internet, al Maletín (Offline)
        persistir_en_dispositivo("cola_asistencia", datos)
        st.warning("📡 Sin señal. Registro protegido en la memoria del teléfono.")
        return False

def guardar_evaluacion_hibrida(conn, datos):
    """Guarda la nota del alumno en el teléfono si no hay internet."""
    URL_HOJA = st.secrets["GSHEETS_URL"]
    try:
        df = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
        df_final = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
        conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=df_final)
        st.success("✅ Evaluación enviada a la Nube.")
    except:
        # Guardar en una lista de pendientes dentro del celular
        pendientes = recuperar_del_dispositivo("cola_evaluaciones") or []
        pendientes.append(datos)
        persistir_en_dispositivo("cola_evaluaciones", pendientes)
        st.warning("📝 Evaluación guardada localmente (Modo Offline).")
