import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURACIÓN DE INTERFAZ (ALTO CONTRASTE) ---
st.set_page_config(page_title="Legado Maestro - Sistema Integral", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #000000 !important; font-weight: 600 !important; }
    .stButton>button { background-color: #004a99; color: white !important; border-radius: 10px; font-weight: bold; }
    .card-aula { background: #f1f3f5; padding: 20px; border-radius: 15px; border-left: 10px solid #004a99; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .status-vivo { color: #d9534f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN Y UTILIDADES ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

def limpiar_id(v): return str(v).strip().split('.')[0]

# --- 3. MANEJO DE ESTADOS DE SESIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.u_data = None
    st.session_state.plan_temp = ""
    st.session_state.clase_activa = False

# --- 4. SISTEMA DE ACCESO (LOGIN Y REGISTRO REAL) ---
if not st.session_state.auth:
    st.title("🛡️ Seguridad Legado Maestro")
    t_log, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Nómina"])

    with t_log:
        c_in = st.text_input("Cédula de Identidad", key="c_in")
        p_in = st.text_input("Contraseña", type="password", key="p_in")
        if st.button("ACCEDER"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['ID_L'] = df_u['CEDULA'].apply(limpiar_id)
            match = df_u[(df_u['ID_L'] == limpiar_id(c_in)) & (df_u['CLAVE'] == p_in)]
            if not match.empty:
                st.session_state.auth = True
                st.session_state.u_data = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("Cédula o clave incorrecta.")

    with t_reg:
        st.subheader("Validación de Personal Autorizado")
        c_re = st.text_input("Ingrese Cédula para Validar", key="c_re")
        p_re = st.text_input("Cree su Clave de Acceso", type="password", key="p_re")
        if st.button("ACTIVAR CUENTA"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['ID_L'] = df_u['CEDULA'].apply(limpiar_id)
            if limpiar_id(c_re) in df_u['ID_L'].values:
                idx = df_u.index[df_u['ID_L'] == limpiar_id(c_re)][0]
                df_u.loc[idx, 'CLAVE'] = p_re
                df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_u.drop(columns=['ID_L']))
                st.success("Cuenta activada. Ya puede iniciar sesión.")
            else: st.error("Cédula no encontrada en nómina oficial.")

# --- 5. PANEL DE CONTROL POST-LOGIN ---
else:
    user = st.session_state.u_data
    st.sidebar.title(f"👤 {user['NOMBRE']}")
    st.sidebar.write(f"Rol: **{user['ROL']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)

    # ================= VISTA DOCENTE =================
    if user['ROL'] == "DOCENTE":
        st.header("👨‍🏫 Mi Aula Virtual")
        tab1, tab2, tab3 = st.tabs(["📅 Planificación", "🚀 Ejecución y Cronómetro", "📜 Historial"])

        with tab1:
            st.subheader("Elaboración de Planificación Semanal")
            tema = st.text_input("Tema de la Actividad:")
            if st.button("🧠 Generar Propuesta con IA"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(messages=[{"role":"user","content":f"Plan técnico de 8 puntos para {tema}"}], model="llama-3.3-70b-versatile")
                st.session_state.plan_temp = res.choices[0].message.content
            
            if st.session_state.plan_temp:
                # EDITOR PEDAGÓGICO: El docente evalúa y modifica
                plan_final = st.text_area("Evalúe y modifique el contenido:", value=st.session_state.plan_temp, height=300)
                if st.button("📤 ENVIAR PARA APROBACIÓN"):
                    nueva = pd.DataFrame([{"FECHA":datetime.now().strftime("%d/%m/%Y"), "USUARIO":user['NOMBRE'], "TEMA":tema, "CONTENIDO":plan_final, "ESTADO":"PENDIENTE"}])
                    conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=pd.concat([df_act, nueva], ignore_index=True))
                    st.success("Plan enviado al Director.")

        with tab2:
            st.subheader("Ejecución de Clase")
            aprobado = df_act[(df_act['USUARIO']==user['NOMBRE']) & (df_act['ESTADO']=='APROBADO')]
            
            if aprobado.empty: st.warning("Esperando aprobación del Director para iniciar.")
            else:
                act = aprobado.iloc[-1]
                st.markdown(f"<div class='card-aula'><b>Actividad Autorizada:</b> {act['TEMA']}</div>", unsafe_allow_html=True)
                
                if not st.session_state.clase_activa:
                    duracion = st.number_input("Minutos de duración:", 10, 180, 45)
                    if st.button("▶️ INICIAR ACTIVIDAD"):
                        st.session_state.clase_activa = True
                        st.session_state.fin_meta = datetime.now() + timedelta(minutes=duracion)
                        # Actualizar en Excel
                        idx = aprobado.index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'EN CURSO'
                        df_act.loc[idx, 'HORA_INICIO'] = datetime.now().strftime("%H:%M")
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.rerun()
                else:
                    restante = st.session_state.fin_meta - datetime.now()
                    if restante.total_seconds() > 0:
                        mins, segs = divmod(int(restante.total_seconds()), 60)
                        st.markdown(f"### ⏳ Tiempo Restante: {mins:02d}:{segs:02d}")
                    else: st.error("⏰ TIEMPO CUMPLIDO")
                    
                    st.file_uploader("📸 Cargar Evidencia en Vivo")
                    if st.button("⏹️ CULMINAR ACTIVIDAD"):
                        st.session_state.clase_activa = False
                        idx = df_act[df_act['USUARIO']==user['NOMBRE']].index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'FINALIZADO'
                        df_act.loc[idx, 'HORA_FIN'] = datetime.now().strftime("%H:%M")
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.balloons()
                        st.rerun()

    # ================= VISTA DIRECTOR =================
    elif user['ROL'] == "DIRECTOR":
        st.title("🏛️ Torre de Control Institucional")
        fecha_sel = st.date_input("Consultar Fecha:", datetime.now()).strftime("%d/%m/%Y")
        df_dia = df_act[df_act['FECHA'] == fecha_sel]

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📥 Planes por Revisar")
            pend = df_dia[df_dia['ESTADO'] == 'PENDIENTE']
            for i, r in pend.iterrows():
                with st.expander(f"De: {r['USUARIO']} - {r['TEMA']}"):
                    st.write(r['CONTENIDO'])
                    obs = st.text_input("Observaciones:", key=f"o_{i}")
                    if st.button("✅ APROBAR", key=f"b_{i}"):
                        df_act.loc[i, 'ESTADO'] = 'APROBADO'
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.rerun()
        with col_b:
            st.subheader("👀 Monitor en Vivo")
            vivos = df_dia[df_dia['ESTADO'] == 'EN CURSO']
            for _, r in vivos.iterrows():
                st.markdown(f"<div class='card-aula'><h4>{r['USUARIO']}</h4><p class='status-vivo'>● EN CLASE</p><p>{r['TEMA']}</p></div>", unsafe_allow_html=True)
