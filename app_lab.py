import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Legado Maestro - BETA SISTEMA", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .status-live { color: #2ecc71; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN Y FUNCIONES DE BASE DE DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

def obtener_usuarios():
    return conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)

def actualizar_usuarios(df_users):
    conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_users)

def registrar_actividad(fila):
    df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    df_final = pd.concat([df_act, pd.DataFrame([fila])], ignore_index=True)
    conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_final)

# --- 3. GESTIÓN DE SESIÓN ---
if 'logueado' not in st.session_state:
    st.session_state.logueado = False
    st.session_state.datos_usuario = None

# --- 4. INTERFAZ DE ACCESO (LOGIN Y REGISTRO) ---
if not st.session_state.logueado:
    st.title("🛡️ Sistema de Seguridad Legado Maestro")
    
    tab_login, tab_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registro Nuevo"])
    
    with tab_login:
        u_cedula = st.text_input("Cédula de Identidad", key="login_ced")
        u_clave = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("INGRESAR"):
            df_u = obtener_usuarios()
            # Validar credenciales
            user_match = df_u[(df_u['CEDULA'].astype(str) == u_cedula) & (df_u['CLAVE'] == u_clave)]
            if not user_match.empty:
                st.session_state.logueado = True
                st.session_state.datos_usuario = user_match.iloc[0].to_dict()
                st.success("Acceso concedido...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Cédula o clave incorrecta.")

    with tab_registro:
        st.subheader("Validación de Nómina")
        r_cedula = st.text_input("Ingrese su Cédula para validar")
        r_clave = st.text_input("Cree una contraseña segura", type="password")
        if st.button("REGISTRAR CUENTA"):
            df_u = obtener_usuarios()
            if r_cedula in df_u['CEDULA'].astype(str).values:
                idx = df_u.index[df_u['CEDULA'].astype(str) == r_cedula][0]
                if pd.notna(df_u.loc[idx, 'CLAVE']) and df_u.loc[idx, 'CLAVE'] != "":
                    st.warning("Usted ya está registrado. Vaya a Iniciar Sesión.")
                else:
                    df_u.loc[idx, 'CLAVE'] = r_clave
                    df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                    actualizar_usuarios(df_u)
                    st.success("✅ Registro exitoso. Ya puede iniciar sesión.")
            else:
                st.error("🚫 Su cédula no está autorizada en la nómina. Contacte al Director.")

# --- 5. PANEL DE CONTROL (SEGÚN ROL) ---
else:
    user = st.session_state.datos_usuario
    st.sidebar.title(f"Bienvenido/a")
    st.sidebar.write(f"**{user['NOMBRE']}**")
    st.sidebar.info(f"Rol: {user['ROL']}")
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logueado = False
        st.rerun()

    # --- VISTA DOCENTE ---
    if user['ROL'] == "DOCENTE":
        st.header("👨‍🏫 Panel de Planificación en Vivo")
        tema = st.text_input("¿Qué actividad dará hoy?")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🧠 GENERAR GUÍA TÉCNICA (IA)"):
                with st.spinner("Consultando inteligencia pedagógica..."):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Genera 8 puntos para una clase de {tema}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.plan_ready = res.choices[0].message.content
                    st.markdown(st.session_state.plan_ready)

        with col2:
            if 'plan_ready' in st.session_state:
                if st.button("🚀 INICIAR CLASE Y REPORTAR"):
                    nueva_act = {
                        "FECHA": datetime.now().strftime("%d/%m/%Y"),
                        "USUARIO": user['NOMBRE'],
                        "ROL": user['ROL'],
                        "AULA": "MANTENIMIENTO",
                        "TEMA": tema,
                        "CONTENIDO": st.session_state.plan_ready,
                        "ESTADO": "EN CURSO",
                        "HORA_INICIO": datetime.now().strftime("%H:%M")
                    }
                    registrar_actividad(nueva_act)
                    st.balloons()
                    st.success("Enviado al Director.")

    # --- VISTA DIRECTOR / SUPERVISOR ---
    elif user['ROL'] in ["DIRECTOR", "SUPERVISOR"]:
        st.header(f"📊 Monitor de Gestión: {user['ROL']}")
        df_ver = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
        
        activos = len(df_ver[df_ver['ESTADO'] == 'EN CURSO'])
        st.metric("Docentes Activos Ahora", activos)
        
        st.subheader("Reporte de Actividades en el Estado")
        st.dataframe(df_ver)
