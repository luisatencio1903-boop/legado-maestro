import streamlit as st
import pandas as pd
import time
import os
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
    .stApp {
        background-color: #f4f7f9;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0d47a1;
        color: white;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-bottom: 5px solid #0d47a1;
    }

    .report-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #1565c0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }

    .plan-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: #333;
    }

    .stButton button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    URL_HOJA = st.secrets["GSHEETS_URL"]
except:
    st.error("Error crítico de conexión.")
    st.stop()

if 'auth_dir' not in st.session_state:
    st.session_state.auth_dir = False

if not st.session_state.auth_dir:
    st.title("🛡️ Sistema Central de Dirección")
    st.subheader("Acceso Restringido - T.E.L. E.R.A.C.")
    
    with st.form("login_director"):
        cedula = st.text_input("Cédula de Identidad:")
        clave = st.text_input("Contraseña:", type="password")
        btn_login = st.form_submit_button("INGRESAR AL PANEL DE CONTROL", use_container_width=True)
        
        if btn_login:
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
            match = df_u[(df_u['C_L'] == limpiar_id(cedula)) & (df_u['CLAVE'] == clave)]
            
            if not match.empty:
                if match.iloc[0]['ROL'] == "DIRECTOR":
                    st.session_state.auth_dir = True
                    st.session_state.u_dir = match.iloc[0].to_dict()
                    st.success("Identidad Verificada. Iniciando monitor de gestión...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Acceso Denegado: Su usuario no posee privilegios de Dirección.")
            else:
                st.error("Cédula o contraseña inválida.")
    st.stop()

with st.sidebar:
    st.title("🛡️ SUPER DIRECTOR")
    st.markdown(f"**Gestión:** {st.session_state.u_dir['NOMBRE']}")
    st.divider()
    
    opcion = st.radio(
        "MÓDULOS ESTRATÉGICOS:",
        [
            "📊 Informe Diario Gestión", 
            "📩 Revisión de Planes",
            "📸 Validar Evidencias", 
            "🏆 Ranking de Méritos"
        ]
    )
    
    st.write("")
    st.write("")
    if st.button("🔒 CERRAR SESIÓN", use_container_width=True):
        st.session_state.auth_dir = False
        st.rerun()

if opcion == "📊 Informe Diario Gestión":
    from vistas import informe_diario
    informe_diario.render_informe(conn, URL_HOJA)

elif opcion == "📩 Revisión de Planes":
    from vistas import revision_planes
    revision_planes.render_revision(conn, URL_HOJA)

elif opcion == "📸 Validar Evidencias":
    from vistas import validar_evidencias
    validar_evidencias.render_validacion(conn, URL_HOJA)

elif opcion == "🏆 Ranking de Méritos":
    from vistas import ranking_meritos
    ranking_meritos.render_ranking(conn, URL_HOJA)
