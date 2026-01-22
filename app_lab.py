import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# ==========================================
# 1. CONFIGURACIÓN DE INTERFAZ Y ESTILOS
# ==========================================
st.set_page_config(page_title="Legado Maestro - Torre de Control Zulia", layout="wide")

# Forzamos alto contraste: Fondo Blanco, Letras Negras
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, h4, p, span, label, .stMarkdown { color: #000000 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #004a99; color: white !important; font-weight: bold; border-radius: 10px; height: 3.5em; }
    .card-aula { background: #f8f9fa; padding: 25px; border-radius: 15px; border-left: 10px solid #004a99; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: black !important; }
    .status-vivo { color: #d9534f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f3f5; border-radius: 5px 5px 0 0; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CONEXIÓN Y UTILIDADES TÉCNICAS
# ==========================================
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

def limpiar_id(v):
    """Limpia la cédula de espacios, puntos y decimales de Google Sheets"""
    return str(v).strip().split('.')[0].replace(',', '').replace('.', '')

# Inicialización de estados de sesión
if 'auth' not in st.session_state:
    st.session_state.update({
        'auth': False, 'u': None, 'plan_edicion': "", 
        'clase_activa': False, 'fin_meta': None, 
        'eval_tecnica': "", 'tema_actual': ""
    })

# ==========================================
# 3. SISTEMA DE ACCESO (LOGIN Y REGISTRO)
# ==========================================
if not st.session_state.auth:
    st.title("🛡️ Seguridad Legado Maestro")
    t_log, t_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Nómina"])

    with t_log:
        c_in = st.text_input("Cédula de Identidad", key="login_c")
        p_in = st.text_input("Contraseña", type="password", key="login_p")
        if st.button("ACCEDER AL PANEL"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
            match = df_u[(df_u['C_L'] == limpiar_id(c_in)) & (df_u['CLAVE'] == p_in)]
            if not match.empty:
                st.session_state.auth = True
                st.session_state.u = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("❌ Cédula o contraseña incorrecta.")

    with t_reg:
        st.subheader("Validación de Personal Autorizado")
        c_re = st.text_input("Ingrese su Cédula para validar", key="reg_c")
        p_re = st.text_input("Cree su Clave de Acceso", type="password", key="reg_p")
        if st.button("ACTIVAR MI CUENTA"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
            ced_limpia = limpiar_id(c_re)
            if ced_limpia in df_u['C_L'].values:
                idx = df_u.index[df_u['C_L'] == ced_limpia][0]
                if pd.notna(df_u.loc[idx, 'CLAVE']) and str(df_u.loc[idx, 'CLAVE']) != "":
                    st.warning("Usted ya tiene una cuenta activa.")
                else:
                    df_u.loc[idx, 'CLAVE'] = p_re
                    df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                    conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_u.drop(columns=['C_L']))
                    st.success("✅ Cuenta activada exitosamente. Ya puede iniciar sesión.")
            else: st.error("🚫 Su cédula no aparece en la nómina oficial.")

# ==========================================
# 4. PANEL DE CONTROL POST-AUTENTICACIÓN
# ==========================================
else:
    user = st.session_state.u
    st.sidebar.title(f"👤 {user['NOMBRE']}")
    st.sidebar.info(f"Rol: {user['ROL']}")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    # Leemos la base de actividades
    df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)

    # ==========================================
    # MODULO DOCENTE
    # ==========================================
    if user['ROL'] == "DOCENTE":
        st.header("👨‍🏫 Gestión Pedagógica del Aula")
        p1, p2, p3 = st.tabs(["📅 Planificación Semanal", "🚀 Ejecución en Vivo", "📝 Evaluación Técnica IA"])

        with p1:
            # Verificamos si ya hay un plan pendiente o aprobado
            plan_existente = df_act[(df_act['USUARIO'] == user['NOMBRE']) & (df_act['ESTADO'].isin(['PENDIENTE', 'APROBADO']))]
            
            if not plan_existente.empty:
                status = plan_existente.iloc[-1]
                st.markdown(f"<div class='card-aula'><h4>Plan actual: {status['TEMA']}</h4>Estado: <b>{status['ESTADO']}</b><br>Espere a finalizar este ciclo para enviar uno nuevo.</div>", unsafe_allow_html=True)
            else:
                st.subheader("Crear Planificación")
                st.session_state.tema_actual = st.text_input("Tema de la clase:", placeholder="Ej: Circuitos Eléctricos")
                
                if st.button("🧠 GENERAR PROPUESTA CON IA"):
                    with st.spinner("La IA está analizando estrategias pedagógicas..."):
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        res = client.chat.completions.create(
                            messages=[{"role":"user","content":f"Como especialista en educación especial, planifica 8 puntos técnicos para {st.session_state.tema_actual} incluyendo Exploración, Desarrollo y Reflexión."}],
                            model="llama-3.3-70b-versatile"
                        )
                        st.session_state.plan_edicion = res.choices[0].message.content
                
                if st.session_state.plan_edicion:
                    # EDITOR PEDAGÓGICO
                    plan_final = st.text_area("Evalúe y modifique el plan según su aula:", value=st.session_state.plan_edicion, height=350)
                    if st.button("📤 ENVIAR PARA APROBACIÓN DEL DIRECTOR"):
                        nueva_fila = pd.DataFrame([{
                            "FECHA": datetime.now().strftime("%d/%m/%Y"),
                            "USUARIO": user['NOMBRE'],
                            "ROL": user['ROL'],
                            "AULA": "MANTENIMIENTO",
                            "TEMA": st.session_state.tema_actual,
                            "CONTENIDO": plan_final,
                            "ESTADO": "PENDIENTE",
                            "HORA_INICIO": "--:--",
                            "HORA_FIN": "--:--"
                        }])
                        df_final = pd.concat([df_act, nueva_fila], ignore_index=True)
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_final)
                        st.session_state.plan_edicion = ""
                        st.success("✅ Plan enviado. El Director ha sido notificado.")
                        st.rerun()

        with p2:
            st.subheader("Control de Actividad Diaria")
            clase_hoy = df_act[(df_act['USUARIO'] == user['NOMBRE']) & (df_act['ESTADO'].isin(['APROBADO', 'EN CURSO']))]
            
            if clase_hoy.empty:
                st.warning("⚠️ No tiene actividades aprobadas para hoy.")
            else:
                act = clase_hoy.iloc[-1]
                with st.expander("📖 Ver Planificación Aprobada", expanded=True):
                    st.markdown(f"<div class='card-aula'>{act['CONTENIDO']}</div>", unsafe_allow_html=True)
                
                if not st.session_state.clase_activa:
                    meta_mins = st.number_input("Establecer duración de la clase (min):", 10, 180, 45)
                    if st.button("▶️ INICIAR CLASE Y NOTIFICAR"):
                        st.session_state.clase_activa = True
                        st.session_state.fin_meta = datetime.now() + timedelta(minutes=meta_mins)
                        # Actualizar estado en Excel
                        idx = clase_hoy.index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'EN CURSO'
                        df_act.loc[idx, 'HORA_INICIO'] = datetime.now().strftime("%H:%M")
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.rerun()
                else:
                    restante = st.session_state.fin_meta - datetime.now()
                    if restante.total_seconds() > 0:
                        mins, segs = divmod(int(restante.total_seconds()), 60)
                        st.markdown(f"### <span class='status-vivo'>⏳ TIEMPO RESTANTE: {mins:02d}:{segs:02d}</span>", unsafe_allow_html=True)
                        st.progress(max(0.0, min(1.0, 1 - (restante.total_seconds() / (meta_mins*60)))))
                    else: st.error("⏰ ¡TIEMPO CUMPLIDO! Por favor, culmine la actividad.")
                    
                    if st.button("⏹️ CULMINAR ACTIVIDAD"):
                        st.session_state.clase_activa = False
                        idx = df_act[df_act['USUARIO'] == user['NOMBRE']].index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'FINALIZADO'
                        df_act.loc[idx, 'HORA_FIN'] = datetime.now().strftime("%H:%M")
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.balloons()
                        st.rerun()

        with p3:
            st.subheader("Transformador Anecdótico (IA)")
            alumno = st.text_input("Nombre del Alumno:")
            nota_prose = st.text_area("Describa lo observado en lenguaje natural:")
            if st.button("🪄 PROCESAR EVALUACIÓN TÉCNICA"):
                with st.spinner("Traduciendo a terminología pedagógica..."):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Traduce esto a un informe técnico pedagógico para {alumno}: {nota_prose}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.eval_tecnica = res.choices[0].message.content
            
            if st.session_state.eval_tecnica:
                st.markdown(f"<div class='card-aula'><b>Evaluación Técnica:</b><br>{st.session_state.eval_tecnica}</div>", unsafe_allow_html=True)
                st.file_uploader("📸 Cargar Evidencia Fotográfica Final")

    # ==========================================
    # MODULO DIRECTOR
    # ==========================================
    elif user['ROL'] == "DIRECTOR":
        st.title("🏛️ Torre de Control Institucional")
        f_sel = st.date_input("Consultar Fecha:", datetime.now()).strftime("%d/%m/%Y")
        df_dia = df_act[df_act['FECHA'] == f_sel]

        c_a, c_b = st.columns(2)
        with c_a:
            st.subheader("📥 Planes por Revisar")
            pendientes = df_dia[df_dia['ESTADO'] == 'PENDIENTE']
            if pendientes.empty: st.write("No hay planes pendientes.")
            for i, r in pendientes.iterrows():
                with st.expander(f"Plan de {r['USUARIO']} - {r['TEMA']}"):
                    st.write(r['CONTENIDO'])
                    obs = st.text_input("Sugerencia de cambio:", key=f"obs_{i}")
                    if st.button("✅ APROBAR PLAN", key=f"btn_{i}"):
                        df_act.loc[i, 'ESTADO'] = 'APROBADO'
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.rerun()
        with c_b:
            st.subheader("👀 Monitor en Vivo")
            vivos = df_dia[df_dia['ESTADO'] == 'EN CURSO']
            if vivos.empty: st.write("No hay clases activas en este momento.")
            for _, r in vivos.iterrows():
                st.markdown(f"""
                    <div class='card-aula'>
                        <h4>{r['USUARIO']}</h4>
                        <span class='status-vivo'>● EN VIVO</span><br>
                        <b>Tema:</b> {r['TEMA']}<br>
                        <b>Inició:</b> {r['HORA_INICIO']}
                    </div>
                """, unsafe_allow_html=True)
