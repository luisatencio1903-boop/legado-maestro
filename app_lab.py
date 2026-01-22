import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURACIÓN DE INTERFAZ (ALTO CONTRASTE) ---
st.set_page_config(page_title="Legado Maestro - Torre de Control", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #004a99; color: white !important; height: 3em; border-radius: 10px; }
    .card-eval { background: #f1f3f5; padding: 25px; border-radius: 15px; border-left: 10px solid #28a745; margin-bottom: 20px; color: black; }
    .status-envivo { color: #d9534f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

# --- 3. LÓGICA DE SESIÓN ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
    st.session_state.u = None

# --- ACCESO (SIMPLIFICADO PARA LA DEMO) ---
if not st.session_state.auth:
    st.title("🛡️ Seguridad Legado Maestro")
    c = st.text_input("Cédula")
    p = st.text_input("Clave", type="password")
    if st.button("INGRESAR"):
        df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
        df_u['ID_C'] = df_u['CEDULA'].astype(str).str.split('.').str[0]
        match = df_u[(df_u['ID_C'] == c) & (df_u['CLAVE'] == p)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.u = match.iloc[0].to_dict()
            st.rerun()
else:
    u = st.session_state.u
    df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)

    # ================= VISTA DOCENTE =================
    if u['ROL'] == "DOCENTE":
        st.header(f"👨‍🏫 Aula Virtual: {u['NOMBRE']}")
        t1, t2, t3 = st.tabs(["📅 Planificación", "🚀 Ejecución y Evaluación IA", "📜 Memoria"])

        with t1:
            # BLOQUEO SI YA HAY PLAN
            plan_activo = df_act[(df_act['USUARIO'] == u['NOMBRE']) & (df_act['ESTADO'].isin(['PENDIENTE', 'APROBADO']))]
            if not plan_activo.empty:
                st.warning(f"Usted ya tiene un plan de '{plan_activo.iloc[-1]['TEMA']}' en estado: {plan_activo.iloc[-1]['ESTADO']}. No puede enviar otro hasta culminar este ciclo.")
            else:
                tema = st.text_input("Defina el tema central:")
                if st.button("🧠 Generar y Editar Plan"):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(messages=[{"role":"user","content":f"Planifica 8 puntos técnicos para {tema} en educación especial."}], model="llama-3.3-70b-versatile")
                    st.session_state.temp_edit = res.choices[0].message.content
                
                if 'temp_edit' in st.session_state:
                    p_final = st.text_area("Modifique su plan antes de enviar:", value=st.session_state.temp_edit, height=300)
                    if st.button("📤 ENVIAR PARA APROBACIÓN"):
                        nueva = pd.DataFrame([{"FECHA":datetime.now().strftime("%d/%m/%Y"), "USUARIO":u['NOMBRE'], "TEMA":tema, "CONTENIDO":p_final, "ESTADO":"PENDIENTE"}])
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=pd.concat([df_act, nueva], ignore_index=True))
                        st.success("Enviado con éxito.")

        with t2:
            clase = df_act[(df_act['USUARIO'] == u['NOMBRE']) & (df_act['ESTADO'].isin(['APROBADO', 'EN CURSO']))]
            if clase.empty: st.warning("Esperando aprobación para iniciar actividad.")
            else:
                act = clase.iloc[-1]
                st.subheader(f"Actividad: {act['TEMA']}")
                with st.expander("📖 Guía Pedagógica Detallada", expanded=False):
                    st.write(act['CONTENIDO'])
                
                # EJECUCIÓN CON CRONÓMETRO
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ INICIAR ACTIVIDAD"): st.session_state.inicio = datetime.now()
                with col2:
                    if st.button("⏹️ CULMINAR Y CERRAR META"):
                        st.balloons()
                        st.success("¡Objetivo Cumplido! Actividad reportada como finalizada.")

                # TRANSFORMADOR PEDAGÓGICO IA
                st.markdown("---")
                st.subheader("📝 Evaluación Anecdótica Transformada")
                alumno = st.text_input("Nombre del Alumno:")
                nota_prose = st.text_area("Describa lo observado con sus palabras (Lenguaje natural):")
                
                if st.button("🪄 PROCESAR EVALUACIÓN TÉCNICA"):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Traduce esta observación coloquial a un informe técnico pedagógico profesional para el alumno {alumno} basado en este tema: {act['TEMA']}. Observación: {nota_prose}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.eval_tech = res.choices[0].message.content
                
                if 'eval_tech' in st.session_state:
                    st.markdown(f"<div class='card-eval'><b>Informe Técnico Generado:</b><br>{st.session_state.eval_tech}</div>", unsafe_allow_html=True)
                    st.file_uploader("📸 Cargar Evidencia Final")

    # ================= VISTA DIRECTOR =================
    elif u['ROL'] == "DIRECTOR":
        st.title("🏛️ Monitor de Gestión Institucional")
        st.dataframe(df_act)
