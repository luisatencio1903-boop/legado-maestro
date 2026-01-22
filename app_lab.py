import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURACIÓN DE ALTO CONTRASTE ---
st.set_page_config(page_title="Legado Maestro - Torre de Control", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-weight: 500; }
    .stButton>button { background-color: #004a99; color: white !important; border-radius: 10px; }
    .card-director { 
        background: #f8f9fa; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #004a99;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-vivo { color: #d9534f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN Y LIMPIEZA DE DATOS ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

def limpiar_id(valor):
    """Elimina decimales .0 y espacios de las cédulas"""
    return str(valor).strip().split('.')[0]

# --- 3. MANEJO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.u_data = None

# --- 4. SISTEMA DE ACCESO (LOGIN Y REGISTRO) ---
if not st.session_state.autenticado:
    st.title("🛡️ Acceso Seguro: Legado Maestro")
    tab_login, tab_registro = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Nómina"])

    with tab_login:
        l_ced = st.text_input("Cédula", key="l_ced")
        l_pass = st.text_input("Contraseña", type="password", key="l_pass")
        if st.button("INGRESAR AL SISTEMA"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['ID_TEMP'] = df_u['CEDULA'].apply(limpiar_id)
            match = df_u[(df_u['ID_TEMP'] == limpiar_id(l_ced)) & (df_u['CLAVE'] == l_pass)]
            
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.u_data = match.iloc[0].to_dict()
                st.success("Acceso exitoso...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Cédula o clave incorrecta.")

    with tab_registro:
        st.subheader("Activación de Cuenta Docente")
        r_ced = st.text_input("Ingrese su Cédula", key="r_ced")
        r_pass = st.text_input("Cree su Clave Personal", type="password", key="r_pass")
        if st.button("VALIDAR Y ACTIVAR"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['ID_TEMP'] = df_u['CEDULA'].apply(limpiar_id)
            ced_limpia = limpiar_id(r_ced)

            if ced_limpia in df_u['ID_TEMP'].values:
                idx = df_u.index[df_u['ID_TEMP'] == ced_limpia][0]
                if pd.notna(df_u.loc[idx, 'CLAVE']) and str(df_u.loc[idx, 'CLAVE']) != "":
                    st.warning("Usted ya está activo en el sistema.")
                else:
                    df_u.loc[idx, 'CLAVE'] = r_pass
                    df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                    df_final_u = df_u.drop(columns=['ID_TEMP'])
                    conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_final_u)
                    st.success("✅ ¡Registro exitoso! Ya puede ir a la pestaña Entrar.")
            else:
                st.error("🚫 Cédula no autorizada en nómina.")

# --- 5. INTERFAZ DE TRABAJO (DOCENTE / DIRECTOR) ---
else:
    u = st.session_state.u_data
    st.sidebar.title(f"👤 {u['NOMBRE']}")
    st.sidebar.write(f"Rol: **{u['ROL']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # --- VISTA DOCENTE (ESTILO NAVEGADOR) ---
    if u['ROL'] == "DOCENTE":
        st.header("👨‍🏫 Panel de Aula")
        t_semana, t_hoy, t_memoria = st.tabs(["📅 Planificación Semanal", "🚀 Clase de Hoy", "📜 Historial"])

        with t_semana:
            tema = st.text_input("Tema para la próxima semana:")
            if st.button("🧠 Generar con IA y Enviar"):
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Plan técnico de 8 puntos para {tema}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.plan_texto = res.choices[0].message.content
                st.info("Plan enviado para revisión del Director.")
                # Aquí se guardaría en Hoja1 con ESTADO='PENDIENTE'

        with t_hoy:
            st.subheader(f"Actividad: {datetime.now().strftime('%d/%m/%Y')}")
            # Simulamos un plan aprobado para la demo
            st.success("✅ Plan Aprobado por Dirección")
            if st.button("▶️ INICIAR ACTIVIDAD"):
                st.info("Clase en curso. Reportando a la Torre de Control...")
            st.file_uploader("📸 Cargar Evidencia Fotográfica")

    # --- VISTA DIRECTOR (TORRE DE CONTROL INTERACTIVA) ---
    elif u['ROL'] == "DIRECTOR":
        st.title("🏛️ Torre de Control Institucional")
        
        # Monitor del día (Lunes, Martes, etc.)
        dia_actual = datetime.now().strftime('%A %d/%m')
        st.subheader(f"Monitoreo de Hoy: {dia_actual}")
        
        # Tarjeta de actividad en vivo (Lo que pediste)
        st.markdown(f"""
            <div class="card-director">
                <h3>Docente: {u['NOMBRE']}</h3>
                <p><b>Aula:</b> Mantenimiento | <b>Estado:</b> <span class="status-vivo">● EN VIVO</span></p>
                <p><b>Tema:</b> Motores Eléctricos | <b>Inicio:</b> 08:30 AM</p>
                <hr>
                <p><b>Sugerencias Pedagógicas:</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        sug = st.text_input("Escriba su observación para el docente:")
        if st.button("ENVIAR OBSERVACIÓN"):
            st.success("Sugerencia enviada al aula del docente.")
