import streamlit as st
import pandas as pd
import requests
import time
from utils.maletin import persistir_en_dispositivo, recuperar_del_dispositivo

# ESCUDO DE ARRANQUE OFFLINE
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    GSheetsConnection = None

def conectar_db():
    if GSheetsConnection is None: return None
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except: return None

def guardar_asistencia_hibrida(conn, datos):
    URL_HOJA = st.secrets.get("GSHEETS_URL", "")
    if conn is not None and URL_HOJA:
        try:
            df = conn.read(spreadsheet=URL_HOJA, worksheet="ASISTENCIA", ttl=0)
            df_final = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
            conn.update(spreadsheet=URL_HOJA, worksheet="ASISTENCIA", data=df_final)
            st.success("✅ Sincronizado con Google Sheets")
            return True
        except: pass
    persistir_en_dispositivo("cola_asistencia", datos)
    st.warning("📡 Sin señal. Registro protegido en el teléfono.")
    return False

def guardar_evaluacion_hibrida(conn, datos):
    URL_HOJA = st.secrets.get("GSHEETS_URL", "")
    if conn is not None and URL_HOJA:
        try:
            df = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
            df_final = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
            conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=df_final)
            st.success("✅ Evaluación enviada.")
            return True
        except: pass
    pendientes = recuperar_del_dispositivo("cola_evaluaciones") or []
    pendientes.append(datos)
    persistir_en_dispositivo("cola_evaluaciones", pendientes)
    st.warning("📝 Evaluación guardada localmente.")
    return False

def cargar_datos_maestros(conn, url):
    if conn is None or not url: return pd.DataFrame(), pd.DataFrame()
    try:
        profes = conn.read(spreadsheet=url, worksheet="USUARIOS", ttl=600)
        matricula = conn.read(spreadsheet=url, worksheet="MATRICULA_GLOBAL", ttl=600)
        return profes, matricula
    except: return pd.DataFrame(), pd.DataFrame()
