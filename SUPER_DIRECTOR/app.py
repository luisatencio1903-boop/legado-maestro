import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from streamlit_gsheets import GSheetsConnection
from utils.comunes import ahora_ve, limpiar_id, cargar_universo_datos

st.set_page_config(
    page_title="SUPER DIRECTOR 1.0",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="collapsedControl"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f1f5f9; }
    .stSelectbox label { font-size: 1.2rem !important; font-weight: 800 !important; color: #1e3a8a !important; }
    .stButton button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: 700; background-color: #1e3a8a; color: white; border: none; }
    .plan-box { background-color: white; padding: 20px; border-radius: 10px; border-left: 8px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border-top: 5px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    URL_HOJA = st.secrets["GSHEETS_URL"]
except:
    st.error("Error de conexión.")
    st.stop()

if 'auth_dir' not in st.session_state:
    st.session_state.auth_dir = False
if 'vista_actual' not in st.session_state:
    st.session_state.vista_actual = "HOME"

if not st.session_state.auth_dir:
    st.title("🛡️ Acceso: SUPER DIRECTOR")
    with st.form("login_dir"):
        cedula = st.text_input("Cédula:")
        clave = st.text_input("Contraseña:", type="password")
        if st.form_submit_button("INGRESAR"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
            match = df_u[(df_u['C_L'] == limpiar_id(cedula)) & (df_u['CLAVE'] == clave)]
            if not match.empty and match.iloc[0]['ROL'] == "DIRECTOR":
                st.session_state.auth_dir = True
                st.session_state.u_dir = match.iloc[0].to_dict()
                st.rerun()
            else:
                st.error("No autorizado.")
    st.stop()

col_sync, col_logout = st.columns([1, 1])
with col_sync:
    if st.button("♻️ ACTUALIZAR"):
        st.cache_data.clear()
        st.toast("Sincronizando universo de datos...")
        time.sleep(1)
        st.rerun()
with col_logout:
    if st.button("🔒 SALIR"):
        st.session_state.auth_dir = False
        st.rerun()

universo = cargar_universo_datos(conn, URL_HOJA)

if st.session_state.vista_actual == "HOME":
    st.write(f"**Director:** {st.session_state.u_dir['NOMBRE']}")
    st.title("🛡️ Panel de Control")
    st.divider()

    st.markdown("### 🚦 ESTADO DEL PLANTEL (HOY)")
    hoy = ahora_ve().strftime("%d/%m/%Y")
    df_as = universo["asistencia"]
    df_ej = universo["ejecucion"]
    
    data_hoy = df_as[df_as['FECHA'] == hoy]
    pres = len(data_hoy[data_hoy['TIPO'] == "ASISTENCIA"])
    fals = len(data_hoy[data_hoy['TIPO'] == "INASISTENCIA"])
    pend_as = len(df_as[df_as['ESTADO_DIRECTOR'] == "PENDIENTE"])
    pend_ej = len(df_ej[df_ej['ESTADO'] == "PENDIENTE"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Presentes", f"{pres}")
    c2.metric("Faltas", f"{fals}")
    c3.metric("Pendientes", f"{pend_as + pend_ej}")

    st.divider()

    st.markdown("### 🛠️ GESTIÓN ESTRATÉGICA")
    sel = st.selectbox(
        "Seleccione una herramienta:",
        [
            "(Seleccionar)",
            "📊 Informe Diario Gestión",
            "📩 Revisión de Planes",
            "📸 Validar Evidencias",
            "🏆 Ranking de Méritos"
        ]
    )

    if sel != "(Seleccionar)":
        st.session_state.vista_actual = sel
        st.rerun()

else:
    if st.button("⬅️ VOLVER AL MENÚ"):
        st.session_state.vista_actual = "HOME"
        st.rerun()
    
    st.subheader(st.session_state.vista_actual)
    st.divider()

    if st.session_state.vista_actual == "📊 Informe Diario Gestión":
        from vistas import informe_diario
        informe_diario.render_informe(universo)
    elif st.session_state.vista_actual == "📩 Revisión de Planes":
        from vistas import revision_planes
        revision_planes.render_revision(conn, URL_HOJA, universo)
    elif st.session_state.vista_actual == "📸 Validar Evidencias":
        from vistas import validar_evidencias
        validar_evidencias.render_validacion(conn, URL_HOJA, universo)
    elif st.session_state.vista_actual == "🏆 Ranking de Méritos":
        from vistas import ranking_meritos
        ranking_meritos.render_ranking(universo)
