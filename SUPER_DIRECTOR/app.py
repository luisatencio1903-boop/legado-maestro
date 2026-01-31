import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection

st.set_page_config(
    page_title="SUPER DIRECTOR 1.0",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def ahora_ve():
    return datetime.utcnow() - timedelta(hours=4)

def limpiar_id(v):
    if v is None: return ""
    return str(v).strip().upper().replace(',', '').replace('.', '').replace('V-', '').replace('E-', '').replace(' ', '')

st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border-left: 8px solid #0d47a1; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    URL_HOJA = st.secrets["GSHEETS_URL"]
except Exception as e:
    st.error("Error de conexión.")
    st.stop()

if 'auth_dir' not in st.session_state:
    st.session_state.auth_dir = False

if not st.session_state.auth_dir:
    st.title("🛡️ Acceso: SUPER DIRECTOR")
    with st.form("login_director"):
        cedula = st.text_input("Cédula de Identidad:")
        clave = st.text_input("Contraseña:", type="password")
        btn_login = st.form_submit_button("Entrar al Panel de Control")
        
        if btn_login:
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
            match = df_u[(df_u['C_L'] == limpiar_id(cedula)) & (df_u['CLAVE'] == clave)]
            
            if not match.empty:
                if match.iloc[0]['ROL'] == "DIRECTOR":
                    st.session_state.auth_dir = True
                    st.session_state.u_dir = match.iloc[0].to_dict()
                    st.success("Cargando sistemas...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Acceso Denegado: Requiere rol de DIRECTOR.")
            else:
                st.error("Credenciales incorrectas.")
    st.stop()

with st.sidebar:
    st.title("🛡️ SUPER DIRECTOR")
    st.write(f"Director: **{st.session_state.u_dir['NOMBRE']}**")
    st.divider()
    
    opcion = st.radio(
        "SISTEMAS DE CONTROL:",
        ["📊 Informe Diario Gestión", "📸 Validar Evidencias", "🏆 Ranking de Méritos"]
    )
    
    st.write("")
    if st.button("🔒 Cerrar Sesión"):
        st.session_state.auth_dir = False
        st.rerun()

if opcion == "📊 Informe Diario Gestión":
    from vistas import informe_diario
    informe_diario.render_informe(conn, URL_HOJA)

elif opcion == "📸 Validar Evidencias":
    st.info("Módulo de Validación en desarrollo.")

elif opcion == "🏆 Ranking de Méritos":
    st.info("Módulo de Ranking en desarrollo.")
