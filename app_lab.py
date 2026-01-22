import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. ESTILOS Y CONFIGURACIÓN ---
st.set_page_config(page_title="Legado Maestro - Zulia 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 700 !important; }
    .stButton>button { background-color: #004a99; color: white !important; font-weight: bold; border-radius: 10px; }
    .card-aula { background: #f8f9fa; padding: 20px; border-radius: 12px; border-left: 10px solid #004a99; margin-bottom: 15px; color: black; }
    .status-vivo { color: #d9534f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

def limpiar(v): return str(v).strip().split('.')[0].replace(',', '').replace('.', '')

# --- 3. ESTADOS DE SESIÓN ---
if 'auth' not in st.session_state:
    st.session_state.update({
        'auth': False, 'u': None, 'plan_edicion': "", 
        'clase_activa': False, 'fin_meta': None, 'meta_mins': 45, # Arregla el NameError
        'eval_tecnica': "", 'tema_actual': ""
    })

# --- 4. ACCESO ---
if not st.session_state.auth:
    st.title("🛡️ Seguridad Legado Maestro")
    t1, t2 = st.tabs(["🔐 Entrar", "📝 Registrarse"])
    with t1:
        c = st.text_input("Cédula", key="lc")
        p = st.text_input("Clave", type="password", key="lp")
        if st.button("INGRESAR"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar)
            match = df_u[(df_u['C_L'] == limpiar(c)) & (df_u['CLAVE'] == p)]
            if not match.empty:
                st.session_state.auth = True
                st.session_state.u = match.iloc[0].to_dict()
                st.rerun()
            else: st.error("Cédula o clave incorrecta.")
    with t2:
        rc = st.text_input("Cédula Nómina", key="rc")
        rp = st.text_input("Crear Clave", type="password", key="rp")
        if st.button("ACTIVAR"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar)
            if limpiar(rc) in df_u['C_L'].values:
                idx = df_u.index[df_u['C_L'] == limpiar(rc)][0]
                df_u.loc[idx, 'CLAVE'] = rp
                df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_u.drop(columns=['C_L']))
                st.success("Activado.")
                # --- 5. PANEL DE CONTROL (POST-LOGIN) ---
else:
    u = st.session_state.u
    st.sidebar.title(f"👤 {u['NOMBRE']}")
    st.sidebar.write(f"Rol: **{u['ROL']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.auth = False
        st.rerun()

    # Leemos la base de actividades (Hoja1)
    df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)

    # ================= VISTA DOCENTE =================
    if u['ROL'] == "DOCENTE":
        st.header(f"👨‍🏫 Aula Virtual: {u['NOMBRE']}")
        t_plan, t_ejec, t_eval, t_exp = st.tabs(["📅 Planificación", "🚀 Ejecución", "🪄 Evaluación IA", "📂 Expedientes"])

        # --- PESTAÑA 1: PLANIFICACIÓN ---
        with t_plan:
            plan_activo = df_act[(df_act['USUARIO'] == u['NOMBRE']) & (df_act['ESTADO'].isin(['PENDIENTE', 'APROBADO']))]
            
            if not plan_activo.empty:
                st.info(f"Usted tiene un plan de '{plan_activo.iloc[-1]['TEMA']}' en estado: {plan_activo.iloc[-1]['ESTADO']}.")
            else:
                st.subheader("Elaboración de la Semana")
                tema_clase = st.text_input("¿Qué tema desea planificar?")
                
                if st.button("🧠 Generar Propuesta IA"):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role":"user","content":f"Plan técnico de 8 puntos para {tema_clase} en educación especial."}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.plan_edicion = res.choices[0].message.content
                
                if st.session_state.plan_edicion:
                    p_final = st.text_area("Evalúe y modifique su plan:", value=st.session_state.plan_edicion, height=300)
                    if st.button("📤 ENVIAR A DIRECCIÓN"):
                        nueva = pd.DataFrame([{
                            "FECHA": datetime.now().strftime("%d/%m/%Y"),
                            "USUARIO": u['NOMBRE'],
                            "TEMA": tema_clase,
                            "CONTENIDO": p_final,
                            "ESTADO": "PENDIENTE"
                        }])
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=pd.concat([df_act, nueva], ignore_index=True))
                        st.success("Plan enviado con éxito.")
                        st.rerun()

        # --- PESTAÑA 2: EJECUCIÓN (CRONÓMETRO) ---
        with t_ejec:
            st.subheader("Control de Clase en Vivo")
            aprobado = df_act[(df_act['USUARIO']==u['NOMBRE']) & (df_act['ESTADO'].isin(['APROBADO', 'EN CURSO']))]
            
            if aprobado.empty:
                st.warning("Esperando aprobación del Director para iniciar.")
            else:
                act = aprobado.iloc[-1]
                st.markdown(f"<div class='card-aula'><b>Tema Autorizado:</b> {act['TEMA']}</div>", unsafe_allow_html=True)
                
                if not st.session_state.clase_activa:
                    # Aquí usamos st.session_state para que el valor persista
                    st.session_state.meta_mins = st.number_input("Establecer duración (min):", 10, 180, st.session_state.meta_mins)
                    
                    if st.button("▶️ INICIAR ACTIVIDAD"):
                        st.session_state.clase_activa = True
                        st.session_state.fin_meta = datetime.now() + timedelta(minutes=st.session_state.meta_mins)
                        
                        # Actualizar en Excel para que el Director vea "EN CURSO"
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
                        st.progress(max(0.0, min(1.0, 1 - (restante.total_seconds() / (st.session_state.meta_mins * 60)))))
                    else:
                        st.error("⏰ ¡TIEMPO CUMPLIDO!")

                    if st.button("⏹️ CULMINAR ACTIVIDAD"):
                        st.session_state.clase_activa = False
                        idx = df_act[df_act['USUARIO']==u['NOMBRE']].index[-1]
                        df_act.loc[idx, 'ESTADO'] = 'FINALIZADO'
                        df_act.loc[idx, 'HORA_FIN'] = datetime.now().strftime("%H:%M")
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                        st.balloons()
                        st.success("Actividad finalizada. Reporte enviado al Director.")
                        st.rerun()
                        # --- PESTAÑA 3: EVALUACIÓN IA (TRANSFORMADOR) ---
        with t_eval:
            st.subheader("🪄 Transformador de Lenguaje Pedagógico")
            st.info("Escriba lo que observó en clase y la IA lo redactará de forma técnica.")
            
            nombre_alumno = st.text_input("Nombre del Alumno:", placeholder="Ej: Greilyz Flores")
            nota_natural = st.text_area("Descripción anecdótica (Cómo se comportó, qué logró):", height=150)
            
            if st.button("🪄 PROCESAR INFORME TÉCNICO"):
                if nombre_alumno and nota_natural:
                    with st.spinner("Traduciendo a terminología profesional..."):
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        res = client.chat.completions.create(
                            messages=[{"role":"user","content":f"Convierte esta observación informal en un informe técnico pedagógico profesional para el alumno {nombre_alumno}. Sé preciso y usa lenguaje de educación especial. Nota: {nota_natural}"}],
                            model="llama-3.3-70b-versatile"
                        )
                        st.session_state.eval_tecnica = res.choices[0].message.content
                else:
                    st.warning("Por favor ingrese el nombre y la nota.")

            if st.session_state.eval_tecnica:
                st.markdown(f"<div class='card-aula'><b>Informe Generado:</b><br>{st.session_state.eval_tecnica}</div>", unsafe_allow_html=True)
                
                if st.button("💾 GUARDAR EN EXPEDIENTE DIGITAL"):
                    # Guardar en la pestaña EVALUACIONES
                    df_ev = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                    nueva_ev = pd.DataFrame([{
                        "FECHA": datetime.now().strftime("%d/%m/%Y"),
                        "DOCENTE": u['NOMBRE'],
                        "ALUMNO": nombre_alumno.upper(),
                        "TEMA": act['TEMA'] if not aprobado.empty else "Actividad General",
                        "ANECDOTA": nota_natural,
                        "INFORME_TECNICO": st.session_state.eval_tecnica
                    }])
                    conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=pd.concat([df_ev, nueva_ev], ignore_index=True))
                    st.success(f"Registro guardado en el expediente de {nombre_alumno}")
                    st.balloons()

        # --- PESTAÑA 4: EXPEDIENTES (EL BOLETÍN) ---
        with t_exp:
            st.subheader("📂 Consulta de Historial y Boletín")
            df_hist = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
            
            if df_hist.empty:
                st.write("Aún no hay evaluaciones registradas.")
            else:
                lista_estudiantes = df_hist['ALUMNO'].unique()
                sel_estudiante = st.selectbox("Seleccione Alumno para ver historial:", lista_estudiantes)
                
                registros = df_hist[df_hist['ALUMNO'] == sel_estudiante]
                st.write(f"Evaluaciones encontradas: **{len(registros)}**")
                
                with st.expander("Ver todas las notas técnicas"):
                    st.table(registros[['FECHA', 'TEMA', 'INFORME_TECNICO']])
                
                if st.button("📜 GENERAR SÍNTESIS DE LAPSO (IA)"):
                    with st.spinner("Analizando historial para el boletín..."):
                        toda_la_data = " ".join(registros['INFORME_TECNICO'].tolist())
                        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                        res = client.chat.completions.create(
                            messages=[{"role":"user","content":f"Basado en este historial de informes técnicos: {toda_la_data}, redacta una síntesis pedagógica final para el boletín del alumno {sel_estudiante}."}],
                            model="llama-3.3-70b-versatile"
                        )
                        st.markdown(f"<div style='background:#e3f2fd; padding:20px; border-radius:10px; color:black;'>{res.choices[0].message.content}</div>", unsafe_allow_html=True)
                        # ==========================================
    # MODULO DIRECTOR / SUPERVISOR
    # ==========================================
    elif u['ROL'] in ["DIRECTOR", "SUPERVISOR"]:
        st.title("🏛️ Torre de Control Institucional")
        
        # Filtro de Fecha para ver Pasado, Hoy y Futuro
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            fecha_consulta = st.date_input("📅 Consultar Fecha:", datetime.now())
            f_str = fecha_consulta.strftime("%d/%m/%Y")
        
        df_dia = df_act[df_act['FECHA'] == f_str]
        
        # Métricas rápidas
        m1, m2, m3 = st.columns(3)
        m1.metric("Planes en Revisión", len(df_dia[df_dia['ESTADO'] == 'PENDIENTE']))
        m2.metric("Clases en Vivo", len(df_dia[df_dia['ESTADO'] == 'EN CURSO']))
        m3.metric("Objetivos Cumplidos", len(df_dia[df_dia['ESTADO'] == 'FINALIZADO']))

        st.markdown("---")

        col_izq, col_der = st.columns(2)

        # --- COLUMNA IZQUIERDA: APROBACIONES (FUTURO/PENDIENTE) ---
        with col_izq:
            st.subheader("📥 Planificaciones por Aprobar")
            pendientes = df_dia[df_dia['ESTADO'] == 'PENDIENTE']
            
            if pendientes.empty:
                st.write("No hay planes pendientes para esta fecha.")
            else:
                for i, row in pendientes.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div class='card-aula'>
                                <b>Docente:</b> {row['USUARIO']}<br>
                                <b>Tema:</b> {row['TEMA']}
                            </div>
                        """, unsafe_allow_html=True)
                        with st.expander("🔍 Revisar Contenido Técnico"):
                            st.write(row['CONTENIDO'])
                            # Cuadro de sugerencias que pediste
                            sugerencia = st.text_input("Sugerencias de modificación:", key=f"sug_{i}")
                            
                            if st.button("✅ APROBAR PLANIFICACIÓN", key=f"btn_ap_{i}"):
                                df_act.loc[i, 'ESTADO'] = 'APROBADO'
                                # Si hay sugerencia, la guardamos (opcional, podrías añadir columna OBSERVACIONES)
                                conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_act)
                                st.success(f"Plan de {row['USUARIO']} aprobado.")
                                st.rerun()

        # --- COLUMNA DERECHA: MONITOR EN VIVO (HOY/PRESENTE) ---
        with col_der:
            st.subheader("👀 Monitor de Actividad en Tiempo Real")
            vivos = df_dia[df_dia['ESTADO'] == 'EN CURSO']
            
            if vivos.empty:
                st.write("No hay docentes en aula en este momento.")
            else:
                for _, r in vivos.iterrows():
                    st.markdown(f"""
                        <div class='card-aula'>
                            <h4 style='margin:0;'>{r['USUARIO']}</h4>
                            <span class='status-vivo'>● EN VIVO (Dando clase)</span><br>
                            <b>Tema:</b> {r['TEMA']}<br>
                            <b>Hora de Inicio:</b> {r['HORA_INICIO']}
                        </div>
                    """, unsafe_allow_html=True)

        # --- SECCIÓN INFERIOR: HISTORIAL DE EVALUACIONES (PASADO) ---
        st.markdown("---")
        if st.checkbox("📜 Ver Memoria de Evaluaciones Técnicas"):
            df_evals_dir = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
            st.subheader("Registros Anecdóticos del Plantel")
            st.dataframe(df_evals_dir)
