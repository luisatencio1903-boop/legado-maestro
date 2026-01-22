import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="Legado Maestro - Zulia", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, label, .stMarkdown, .stMetric { color: #000000 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #004a99; color: white !important; font-weight: bold; border-radius: 8px; height: 3em; }
    .card-aula { background: #f8f9fa; padding: 20px; border-radius: 12px; border-left: 10px solid #004a99; margin-bottom: 15px; color: black !important; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    .status-vivo { color: #d9534f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    URL_HOJA = st.secrets["GSHEETS_URL"]
except:
    st.error("Error de conexión con Google Sheets. Verifique sus Secrets.")
    st.stop()

def limpiar_id(v): 
    return str(v).strip().split('.')[0].replace(',', '').replace('.', '')

# --- 3. INICIALIZACIÓN SEGURA DE VARIABLES (ANTI-ERRORES) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'u' not in st.session_state: st.session_state.u = None
if 'plan_edicion' not in st.session_state: st.session_state.plan_edicion = ""
if 'clase_activa' not in st.session_state: st.session_state.clase_activa = False
if 'fin_meta' not in st.session_state: st.session_state.fin_meta = None
if 'meta_mins' not in st.session_state: st.session_state.meta_mins = 45 # Valor por defecto seguro
if 'eval_tecnica' not in st.session_state: st.session_state.eval_tecnica = ""

# --- 4. SISTEMA DE ACCESO ---
if not st.session_state.auth:
    st.title("🛡️ Seguridad Legado Maestro - Zulia")
    t_log, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Nómina"])

    with t_log:
        c_in = st.text_input("Cédula de Identidad", key="login_c")
        p_in = st.text_input("Contraseña", type="password", key="login_p")
        if st.button("ACCEDER AL SISTEMA"):
            try:
                df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
                df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
                match = df_u[(df_u['C_L'] == limpiar_id(c_in)) & (df_u['CLAVE'] == p_in)]
                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.u = match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
            except Exception as e: st.error(f"Error leyendo base de datos: {e}")

    with t_reg:
        c_re = st.text_input("Cédula para validar", key="reg_c")
        p_re = st.text_input("Nueva Clave", type="password", key="reg_p")
        if st.button("ACTIVAR CUENTA"):
            try:
                df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
                df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
                ced_limpia = limpiar_id(c_re)
                if ced_limpia in df_u['C_L'].values:
                    idx = df_u.index[df_u['C_L'] == ced_limpia][0]
                    df_u.loc[idx, 'CLAVE'] = p_re
                    df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                    conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_u.drop(columns=['C_L']))
                    st.success("✅ Activado. Inicie sesión.")
                else: st.error("🚫 No encontrado en nómina.")
            except: st.error("Error al registrar.")

# --- 5. PANEL PRINCIPAL ---
else:
    u = st.session_state.u
    st.sidebar.title(f"👤 {u['NOMBRE']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    try:
        df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
    except:
        st.error("No se pudo leer la Hoja1. Verifique que exista en Google Sheets.")
        st.stop()

    # === VISTA DOCENTE ===
    if u['ROL'] == "DOCENTE":
        st.header(f"👨‍🏫 Aula Virtual: {u['NOMBRE']}")
        t1, t2, t3, t4 = st.tabs(["📅 Planificación", "🚀 Ejecución", "📝 Evaluación IA", "📂 Expediente"])

        # Pestaña 1: Planificación
        with t1:
            p_existente = df_act[(df_act['USUARIO'] == u['NOMBRE']) & (df_act['ESTADO'].isin(['PENDIENTE', 'APROBADO']))]
            if not p_existente.empty:
                st.info(f"Plan Activo: {p_existente.iloc[-1]['TEMA']} ({p_existente.iloc[-1]['ESTADO']})")
            else:
                tema = st.text_input("Tema de la clase:")
                if st.button("🧠 Generar Propuesta"):
                    try:
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        res = client.chat.completions.create(messages=[{"role":"user","content":f"Plan técnico breve para {tema}"}], model="llama-3.3-70b-versatile")
                        st.session_state.plan_edicion = res.choices[0].message.content
                    except: st.warning("Error conectando con la IA.")
                
                if st.session_state.plan_edicion:
                    plan_final = st.text_area("Editar plan:", value=st.session_state.plan_edicion)
                    if st.button("📤 ENVIAR"):
                        nueva = pd.DataFrame([{"FECHA": datetime.now().strftime("%d/%m/%Y"), "USUARIO": u['NOMBRE'], "TEMA": tema, "CONTENIDO": plan_final, "ESTADO": "PENDIENTE"}])
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=pd.concat([df_act, nueva], ignore_index=True))
                        st.success("Enviado."); st.rerun()

        # Pestaña 2: Ejecución (BLINDADA CONTRA ERRORES)
        with t2:
            ap = df_act[(df_act['USUARIO']==u['NOMBRE']) & (df_act['ESTADO'].isin(['APROBADO', 'EN CURSO']))]
            if ap.empty: st.warning("Esperando aprobación.")
            else:
                act = ap.iloc[-1]
                st.markdown(f"<div class='card-aula'><b>Tema:</b> {act['TEMA']}</div>", unsafe_allow_html=True)
                
                # Selector de tiempo SEGURO
                if not st.session_state.clase_activa:
                    val_ini = st.session_state.meta_mins if st.session_state.meta_mins > 0 else 45
                    mins = st.number_input("Duración (min):", 1, 180, int(val_ini))
                    st.session_state.meta_mins = mins
                    
                    if st.button("▶️ INICIAR"):
                        st.session_state.clase_activa = True
                        st.session_state.fin_meta = datetime.now() + timedelta(minutes=mins)
                        idx = ap.index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'EN CURSO'
                        df_act.loc[idx, 'HORA_INICIO'] = datetime.now().strftime("%H:%M")
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.rerun()
                else:
                    # Lógica de progreso BLINDADA
                    if st.session_state.fin_meta:
                        restante = st.session_state.fin_meta - datetime.now()
                        secs_rest = restante.total_seconds()
                        total_secs = st.session_state.meta_mins * 60
                        
                        if secs_rest > 0:
                            mins_show, secs_show = divmod(int(secs_rest), 60)
                            st.markdown(f"### ⏳ {mins_show:02d}:{secs_show:02d}")
                            try:
                                prog = max(0.0, min(1.0, 1 - (secs_rest / total_secs)))
                                st.progress(prog)
                            except: st.progress(0.5) # Fallback si falla el cálculo
                        else:
                            st.error("⏰ TIEMPO CUMPLIDO")
                    
                    if st.button("⏹️ CULMINAR"):
                        st.session_state.clase_activa = False
                        idx = df_act[df_act['USUARIO']==u['NOMBRE']].index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'FINALIZADO'
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.success("Finalizado."); st.rerun()

        # Pestaña 3: Evaluación IA
        with t3:
            alum = st.text_input("Alumno:")
            nota = st.text_area("Observación:")
            if st.button("🪄 PROCESAR"):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(messages=[{"role":"user","content":f"Informe técnico para {alum}: {nota}"}], model="llama-3.3-70b-versatile")
                    st.session_state.eval_tecnica = res.choices[0].message.content
                except: st.error("Error IA")
            
            if st.session_state.eval_tecnica:
                st.info(st.session_state.eval_tecnica)
                if st.button("💾 GUARDAR"):
                    try:
                        df_ev = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                        nueva = pd.DataFrame([{"FECHA":datetime.now().strftime("%d/%m/%Y"), "ALUMNO":alum, "INFORME":st.session_state.eval_tecnica}])
                        conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=pd.concat([df_ev, nueva], ignore_index=True))
                        st.success("Guardado.")
                    except: st.error("Falta pestaña EVALUACIONES en Excel")

        # Pestaña 4: Expedientes
        with t4:
            try:
                df_ev = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                sel = st.selectbox("Alumno:", df_ev['ALUMNO'].unique())
                st.table(df_ev[df_ev['ALUMNO']==sel])
            except: st.write("Sin datos o falta pestaña EVALUACIONES.")

    # === VISTA DIRECTOR ===
    elif u['ROL'] == "DIRECTOR":
        st.title("🏛️ Torre de Control")
        df_dia = df_act[df_act['FECHA'] == datetime.now().strftime("%d/%m/%Y")]
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Pendientes")
            for i, r in df_dia[df_dia['ESTADO'] == 'PENDIENTE'].iterrows():
                with st.expander(f"{r['USUARIO']}"):
                    st.write(r['CONTENIDO'])
                    if st.button("✅ APROBAR", key=f"ap_{i}"):
                        df_act.loc[i, 'ESTADO'] = 'APROBADO'
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.rerun()
        with c2:
            st.subheader("En Vivo")
            for _, r in df_dia[df_dia['ESTADO'] == 'EN CURSO'].iterrows():
                st.markdown(f"<div class='card-aula'>{r['USUARIO']}<br><span class='status-vivo'>● EN VIVO</span></div>", unsafe_allow_html=True)
