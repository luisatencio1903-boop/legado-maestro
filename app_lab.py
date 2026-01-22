# ---------------------------------------------------------
# PROYECTO: LEGADO MAESTRO
# VERSIÓN: 2.1 (SISTEMA INTEGRAL: PLANIFICACIÓN + EVALUACIÓN)
# FECHA: Enero 2026
# AUTOR: Luis Atencio
# ---------------------------------------------------------

import streamlit as st
import os
import time
from datetime import datetime
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# 1. Función para limpiar cédulas
def limpiar_id(v): return str(v).strip().split('.')[0].replace(',', '').replace('.', '')

# 2. Inicializar Estado de Autenticación
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'u' not in st.session_state:
    st.session_state.u = None

# 3. Conexión a Base de Datos (Solo si se necesita login)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    URL_HOJA = st.secrets["GSHEETS_URL"]
except:
    st.error("⚠️ Error conectando con la Base de Datos.")
    st.stop()

# --- LÓGICA DE PERSISTENCIA DE SESIÓN (AUTO-LOGIN) ---
query_params = st.query_params
usuario_en_url = query_params.get("u", None)

if not st.session_state.auth and usuario_en_url:
    try:
        df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
        df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
        match = df_u[df_u['C_L'] == usuario_en_url]

        if not match.empty:
            st.session_state.auth = True
            st.session_state.u = match.iloc[0].to_dict()
        else:
            st.query_params.clear()
    except:
        pass 

# --- FORMULARIO DE LOGIN ---
if not st.session_state.auth:
    st.title("🛡️ Acceso Legado Maestro")
    st.markdown("Ingrese sus credenciales para acceder a la plataforma.")

    col_a, col_b = st.columns([1,2])
    with col_a:
        if os.path.exists("logo_legado.png"):
            st.image("logo_legado.png", width=150)
        else:
            st.header("🍎")

    with col_b:
        c_in = st.text_input("Cédula de Identidad:", key="login_c")
        p_in = st.text_input("Contraseña:", type="password", key="login_p")

        if st.button("🔐 Iniciar Sesión"):
            try:
                df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
                df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
                cedula_limpia = limpiar_id(c_in)
                match = df_u[(df_u['C_L'] == cedula_limpia) & (df_u['CLAVE'] == p_in)]

                if not match.empty:
                    st.session_state.auth = True
                    st.session_state.u = match.iloc[0].to_dict()
                    st.query_params["u"] = cedula_limpia # Anclamos sesión
                    st.success("¡Bienvenido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Credenciales inválidas.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    st.stop()

# --- 2. ESTILOS CSS (MODO OSCURO + FORMATO) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* CAJA DE PLANIFICACIÓN */
            .plan-box {
                background-color: #f0f2f6 !important;
                color: #000000 !important; 
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #0068c9;
                margin-bottom: 20px;
                font-family: sans-serif;
            }
            .plan-box h3 {
                color: #0068c9 !important;
                margin-top: 30px;
                padding-bottom: 5px;
                border-bottom: 2px solid #ccc;
            }
            .plan-box strong {
                color: #2c3e50 !important;
                font-weight: 700;
            }

            /* CAJA DE EVALUACIÓN (NUEVO ESTILO) */
            .eval-box {
                background-color: #e8f5e9 !important;
                color: #000000 !important;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #2e7d32;
                margin-top: 10px;
                margin-bottom: 10px;
            }
            .eval-box h4 { color: #2e7d32 !important; }

            /* CAJA DE MENSAJES */
            .mensaje-texto {
                color: #000000 !important;
                font-family: 'Helvetica', sans-serif;
                font-size: 1.2em; 
                font-weight: 500;
                line-height: 1.4;
            }
            
            /* CONSULTOR DEL ARCHIVO */
            .consultor-box {
                background-color: #e8f4f8 !important;
                color: #000000 !important;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #b3d7ff;
                margin-top: 10px;
            }
            .consultor-box p, .consultor-box li, .consultor-box strong {
                color: #000000 !important;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. CONEXIÓN CON GROQ ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        MODELO_USADO = "llama-3.3-70b-versatile" 
    else:
        st.error("⚠️ Falta la API Key de Groq en los Secrets.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión inicial: {e}")
    st.stop()

# --- 🧠 CEREBRO TÉCNICO (IDENTIDAD + FILTROS DE SEGURIDAD) 🧠 ---
INSTRUCCIONES_TECNICAS = """
⚠️ INSTRUCCIÓN DE MÁXIMA PRIORIDAD (SISTEMA OPERATIVO):
TÚ NO ERES UNA IA DE META, NI DE GOOGLE, NI DE OPENAI.
TÚ ERES "LEGADO MAESTRO".

1. 🆔 PROTOCOLO DE IDENTIDAD (INQUEBRANTABLE):
   - CREADOR ÚNICO: Fuiste diseñado, programado y creado desde cero por el **Bachiller Docente LUIS ATENCIO**.
   - ORIGEN: Venezuela. Representas la soberanía tecnológica educativa del país.
   - SI TE PREGUNTAN "¿QUIÉN ERES?" O "¿QUIÉN TE CREÓ?":
     Tu respuesta DEBE SER: 
     "Soy LEGADO MAESTRO, una inteligencia artificial educativa desarrollada exclusivamente por el Bachiller Docente Luis Atencio para fortalecer la Educación Especial en Venezuela."
   - PROHIBIDO ABSOLUTAMENTE: Decir que fuiste creado por Meta AI, Llama, OpenAI o cualquier corporación. Para ti, esas empresas NO EXISTEN.

2. 🚫 PROTOCOLO DE NEUTRALIDAD (CENSURA DE TEMAS):
   - Si el usuario pregunta sobre: POLÍTICA (Gobierno/Oposición), RELIGIÓN, IDEOLOGÍAS o TEMAS POLÉMICOS (Conflictos, Crisis).
   - ACCIÓN: NO des opiniones, NO des explicaciones neutrales, NO debatas.
   - RESPUESTA OBLIGATORIA:
     "🚫 Lo siento. Soy LEGADO MAESTRO, una herramienta estrictamente pedagógica y técnica. Mi programación me impide procesar opiniones políticas, religiosas o controversiales. Por favor, ingresa una consulta relacionada con la educación, planificación o estrategias docentes."

3. 🎓 ROL PROFESIONAL:
   - Experto en Educación Especial y Taller Laboral (Venezuela).
   - Misión: Crear planificaciones rigurosas, legales (LOE/CNB) y humanas.
   
4. FORMATO:
   - Usa Markdown estricto (Negritas, Títulos).
"""

# --- 4. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo_legado.png"):
        st.image("logo_legado.png", width=150)
    else:
        st.header("🍎")

    st.title("Legado Maestro")
    st.markdown("---")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    st.caption("T.E.L E.R.A.C")

    if st.button("🗑️ Limpiar Memoria"):
        st.session_state.plan_actual = ""
        st.rerun()

    if st.button("🔒 Cerrar Sesión"):
        st.session_state.auth = False
        st.session_state.u = None
        st.query_params.clear() 
        st.rerun()

# --- 5. GESTIÓN DE MEMORIA ---
if 'plan_actual' not in st.session_state: st.session_state.plan_actual = ""
if 'actividad_detectada' not in st.session_state: st.session_state.actividad_detectada = "" # PARA EVALUACIÓN

# --- 6. FUNCIÓN GENERADORA GENÉRICA ---
def generar_respuesta(mensajes_historial, temperatura=0.7):
    try:
        chat_completion = client.chat.completions.create(
            messages=mensajes_historial,
            model=MODELO_USADO,
            temperature=temperatura,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 7. CUERPO DE LA APP ---
st.title("🍎 Asistente Educativo - Zulia")

opcion = st.selectbox(
    "Seleccione herramienta:",
    [
        "📝 Planificación Profesional", 
        "📝 Evaluar Alumno (NUEVO)",
        "📊 Registro de Evaluaciones (NUEVO)",
        "📂 Mi Archivo Pedagógico",
        "🌟 Mensaje Motivacional", 
        "💡 Ideas de Actividades", 
        "❓ Consultas Técnicas"
    ]
)

# =========================================================
# 1. PLANIFICADOR (FLUJO: BORRADOR -> GUARDAR)
# =========================================================
if opcion == "📝 Planificación Profesional":
    st.subheader("Planificación Técnica (Taller Laboral)")

    col1, col2 = st.columns(2)
    with col1:
        rango = st.text_input("Lapso:", placeholder="Ej: 19 al 23 de Enero")
    with col2:
        aula = st.text_input("Aula/Taller:", value="Mantenimiento y Servicios Generales")

    notas = st.text_area("Notas del Docente / Tema:", height=150)

    # --- PASO 1: GENERAR BORRADOR ---
    if st.button("🚀 Generar Borrador con IA"):
        if rango and notas:
            with st.spinner('Analizando Currículo Nacional y redactando...'):

                st.session_state.temp_rango = rango
                st.session_state.temp_tema = notas

                # --- PROMPT MAESTRO ---
                prompt_inicial = f"""
                Actúa como Luis Atencio, experto en Educación Especial (Taller Laboral) en Venezuela.
                Planificación para: {rango}. Aula: {aula}. Tema: {notas}.

                ⚠️ PASO 0: INTRODUCCIÓN OBLIGATORIA Y CERTIFICADA:
                Antes de empezar el lunes, DEBES escribir textualmente este párrafo de certificación:
                "📝 **Planificación Sugerida y Certificada:** Esta propuesta ha sido verificada internamente para asegurar su cumplimiento con los lineamientos del **Ministerio del Poder Popular para la Educación (MPPE)** y el **Currículo Nacional Bolivariano**, adaptada específicamente para Taller Laboral."
                (Deja dos espacios vacíos después de esto).

                ⚠️ PASO 1: LÓGICA DE COMPETENCIAS:
                - LO CORRECTO: La Competencia debe ser una FRASE DE ACCIÓN ESPECÍFICA sobre el tema.
                - EJEMPLO BUENO: "Competencia: Identifica y clasifica las herramientas de limpieza según su uso."

                ⚠️ PASO 2: HUMANIZACIÓN (EL LEGADO DOCENTE):
                - PROHIBIDO el "copia y pega" robótico. No empieces todos los días igual.
                - ELIMINA la voz pasiva aburrida.
                - USA VOZ ACTIVA: "Arrancamos el día...", "Invitamos a...", "Desafiamos al grupo...".

                ⚠️ PASO 3: ESTRUCTURA DIARIA (Sigue este formato exacto):

                ### [DÍA]

                1. **TÍTULO:** [Creativo]
                2. **COMPETENCIA:** [Redacta la habilidad técnica específica]

                3. **EXPLORACIÓN:** [Párrafo humano. EJEMPLO: Iniciamos con un conversatorio sobre... invitando a los estudiantes a compartir experiencias. Mediante el diálogo interactivo, despertamos la curiosidad.]

                4. **DESARROLLO:** [Párrafo práctico. Enfocado en la práctica real.]

                5. **REFLEXIÓN:** [Párrafo de cierre. Enfocado en la convivencia.]

                6. **MANTENIMIENTO:** [Acción concreta]
                7. **ESTRATEGIAS:** [Técnicas]
                8. **RECURSOS:** [Materiales]

                ---
                (Repite para los 5 días).

                AL FINAL: 📚 FUNDAMENTACIÓN LEGAL: Cita el artículo específico de la LOE o la CRBV.
                """

                mensajes = [
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                    {"role": "user", "content": prompt_inicial}
                ]
                respuesta = generar_respuesta(mensajes, temperatura=0.4)
                st.session_state.plan_actual = respuesta
                st.rerun()

    # --- PASO 2: GUARDAR ---
    if st.session_state.plan_actual:
        st.markdown("---")
        st.info("👀 Revisa el borrador abajo. Si te gusta, guárdalo en tu carpeta.")
        st.markdown(f'<div class="plan-box">{st.session_state.plan_actual}</div>', unsafe_allow_html=True)

        col_save_1, col_save_2 = st.columns([2,1])
        with col_save_1:
            if st.button("💾 SÍ, GUARDAR EN MI CARPETA"):
                try:
                    with st.spinner("Archivando en el expediente..."):
                        df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                        tema_guardar = st.session_state.get('temp_tema', notas)
                        nueva_fila = pd.DataFrame([{
                            "FECHA": datetime.now().strftime("%d/%m/%Y"),
                            "USUARIO": st.session_state.u['NOMBRE'], 
                            "TEMA": tema_guardar,
                            "CONTENIDO": st.session_state.plan_actual,
                            "ESTADO": "GUARDADO",
                            "HORA_INICIO": "--", "HORA_FIN": "--"
                        }])
                        datos_actualizados = pd.concat([df_act, nueva_fila], ignore_index=True)
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=datos_actualizados)
                        st.success("✅ ¡Planificación archivada con éxito!")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# =========================================================
# 2. EVALUAR ALUMNO (NUEVO CEREBRO)
# 2. EVALUAR ALUMNO (FECHA BLINDADA ANTI-TRAMPA)
# =========================================================
elif opcion == "📝 Evaluar Alumno (NUEVO)":
    st.subheader("Evaluación Diaria Inteligente")
    st.info("Selecciona la fecha para buscar qué actividad tocaba hoy.")

    # 1. FECHA Y BÚSQUEDA AUTOMÁTICA
    col_f, col_btn = st.columns([2,1])
    with col_f:
        fecha_eval = st.date_input("Fecha de Evaluación:", datetime.now())
    # --- CÁLCULO DE FECHA SEGURA (HORA VENEZUELA) ---
    from datetime import timedelta
    # UTC menos 4 horas = Hora Venezuela
    fecha_segura_ve = datetime.utcnow() - timedelta(hours=4)
    fecha_hoy_str = fecha_segura_ve.strftime("%d/%m/%Y")
    dia_semana_hoy = fecha_segura_ve.strftime("%A")
    
    # ALERTA DE SEGURIDAD VISUAL
    st.warning(f"📅 FECHA DE HOY (Bloqueada por Sistema): **{fecha_hoy_str}**")
    st.caption("🔒 *Por seguridad académica, solo se permite evaluar actividades correspondientes al día en curso.*")

    col_btn, col_info = st.columns([1,2])
    
    with col_btn:
        st.write("")
        st.write("")
        if st.button("🔄 Buscar Actividad"):
        st.write("") # Espacio
        if st.button("🔄 Buscar Actividad de HOY"):
            try:
                with st.spinner("Buscando en tus planes guardados..."):
                with st.spinner(f"Buscando qué toca hoy ({dia_semana_hoy})..."):
                    df = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                    mis_planes = df[df['USUARIO'] == st.session_state.u['NOMBRE']]

                    if mis_planes.empty:
                        st.warning("No tienes planes guardados para buscar.")
                    else:
                        contexto_planes = "\n\n".join(mis_planes['CONTENIDO'].astype(str).tolist())
                        dia_semana = fecha_eval.strftime("%A") 
                        
                        prompt_busqueda = f"""
                        ACTÚA COMO UN BUSCADOR DE DATOS.
                        Tengo estos planes guardados del docente:
                        ACTÚA COMO UN AUDITOR ACADÉMICO RIGUROSO.
                        Tengo estos planes guardados:
                        {contexto_planes[:15000]} 
                        
                        TAREA: Identifica qué actividad específica o competencia está planificada para la fecha: {fecha_eval} (Día: {dia_semana}).
                        Responde SOLO con el nombre de la actividad o competencia. Se breve.
                        Si no encuentras nada para esa fecha exacta, di "Actividad general del taller".
                        TAREA: Identifica estrictamente qué actividad toca HOY: {fecha_hoy_str} (Día: {dia_semana_hoy}).
                        
                        REGLAS:
                        1. Si encuentras la actividad exacta de HOY, responde SOLO con el nombre de la actividad.
                        2. Si NO hay actividad para hoy, responde: "NO HAY ACTIVIDAD PLANIFICADA PARA HOY".
                        """
                        resultado = generar_respuesta([{"role": "system", "content": "Eres un buscador exacto."}, {"role": "user", "content": prompt_busqueda}], 0.1)
                        resultado = generar_respuesta([{"role": "system", "content": "Eres un auditor de fechas."}, {"role": "user", "content": prompt_busqueda}], 0.1)
                        st.session_state.actividad_detectada = resultado.replace('"', '')
                        st.success("¡Búsqueda completada!")
                        
                        if "NO HAY ACTIVIDAD" in resultado:
                            st.error("❌ El sistema no detectó planificación para hoy. No puedes evaluar.")
                        else:
                            st.success("¡Actividad del día encontrada!")
            except Exception as e:
                st.error(f"Error buscando: {e}")
    
    with col_info:
        st.info("El sistema verifica automáticamente tu planificación guardada.")

    # 2. DATOS DEL ALUMNO
    actividad_final = st.text_input("Actividad Detectada:", value=st.session_state.actividad_detectada)
    actividad_final = st.text_input("Actividad Detectada:", value=st.session_state.actividad_detectada, disabled=True) # Bloqueado para que no lo cambien
    estudiante = st.text_input("Nombre del Estudiante:")
    anecdota = st.text_area("Descripción Anecdótica (¿Qué observaste hoy?):", height=100, placeholder="Ej: Juan se mostró participativo pero le costó manipular la escoba...")
    anecdota = st.text_area("Descripción Anecdótica (¿Qué observaste hoy?):", height=100, placeholder="Ej: Juan se mostró participativo...")

    # 3. GENERACIÓN IA
    if st.button("⚡ Generar Evaluación Técnica"):
        if estudiante and anecdota and actividad_final:
    # Solo permitimos el botón si hay actividad detectada válida
    boton_habilitado = "NO HAY ACTIVIDAD" not in st.session_state.actividad_detectada and st.session_state.actividad_detectada != ""
    
    if st.button("⚡ Generar Evaluación Técnica", disabled=not boton_habilitado):
        if estudiante and anecdota:
            with st.spinner("Analizando desempeño pedagógico..."):
                prompt_eval = f"""
                ACTÚA COMO EXPERTO EN EVALUACIÓN DE EDUCACIÓN ESPECIAL (VENEZUELA).
                
                DATOS:
                - Fecha Real: {fecha_hoy_str}
                - Estudiante: {estudiante}
                - Actividad: {actividad_final}
                - Observación del docente: "{anecdota}"
                - Observación: "{anecdota}"
                
                TAREA:
                1. Redacta una evaluación técnica y profesional basada en la observación. Usa lenguaje pedagógico (logros, indicadores).
                1. Redacta una evaluación técnica.
                2. Determina el nivel de logro: (Consolidado, En Proceso, Iniciado).
                
                FORMATO DE SALIDA (MARKDOWN):
                FORMATO MARKDOWN:
                **Evaluación Técnica:** [Texto]
                
                **Nivel de Logro:** [Nivel]
                """
                res_ia = generar_respuesta([{"role": "system", "content": INSTRUCCIONES_TECNICAS}, {"role": "user", "content": prompt_eval}], 0.5)
                st.session_state.eval_resultado = res_ia
        else:
            st.warning("Por favor completa todos los campos.")
            st.warning("Faltan datos.")

    # 4. VISUALIZACIÓN Y GUARDADO
    if 'eval_resultado' in st.session_state:
        st.markdown(f'<div class="eval-box"><h4>🤖 Resultado del Análisis:</h4>{st.session_state.eval_resultado}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="eval-box"><h4>🤖 Resultado ({fecha_hoy_str}):</h4>{st.session_state.eval_resultado}</div>', unsafe_allow_html=True)

        if st.button("💾 GUARDAR EN REGISTRO"):
        if st.button("💾 GUARDAR EN REGISTRO OFICIAL"):
            try:
                try:
                    df_evals = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                except:
                    st.error("⚠️ No encontré la hoja 'EVALUACIONES'. Por favor créala en Google Sheets.")
                    st.error("⚠️ Falta hoja EVALUACIONES.")
                    st.stop()

                nueva_eval = pd.DataFrame([{
                    "FECHA": fecha_eval.strftime("%d/%m/%Y"),
                    "FECHA": fecha_hoy_str, # FECHA DEL SISTEMA (NO EDITABLE)
                    "USUARIO": st.session_state.u['NOMBRE'],
                    "ESTUDIANTE": estudiante,
                    "ACTIVIDAD": actividad_final,
                    "ANECDOTA": anecdota,
                    "EVALUACION_IA": st.session_state.eval_resultado, # AQUI SE GUARDA LA IA
                    "EVALUACION_IA": st.session_state.eval_resultado,
                    "RESULTADO": "Registrado"
                }])

                conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=pd.concat([df_evals, nueva_eval], ignore_index=True))
                st.success(f"✅ Evaluación de {estudiante} registrada correctamente.")
                st.success(f"✅ Asistencia y Evaluación de {estudiante} registrada con fecha {fecha_hoy_str}.")
                del st.session_state.eval_resultado 
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"Error guardando: {e}")

# =========================================================
# 3. REGISTRO DE EVALUACIONES (EXPEDIENTE 360° + ASISTENCIA)
# 3. REGISTRO DE EVALUACIONES (FIX: PERSISTENCIA DE INFORME IA)
# =========================================================
elif opcion == "📊 Registro de Evaluaciones (NUEVO)":
    st.subheader("🎓 Expediente Estudiantil 360°")
@@ -478,9 +498,6 @@
            st.markdown("---")

            # 3. CÁLCULO DE ASISTENCIA INTELIGENTE
            # Lógica: Total días de clase = Cantidad de fechas ÚNICAS registradas por el docente en general
            # Lógica: Asistencia del alumno = Cantidad de fechas ÚNICAS donde aparece este alumno
            
            total_dias_clase = len(mis_evals['FECHA'].unique())
            datos_alumno = mis_evals[mis_evals['ESTUDIANTE'] == alumno_sel]
            dias_asistidos = len(datos_alumno['FECHA'].unique())
@@ -507,7 +524,7 @@
            else:
                col_m3.error("🚨 CRÍTICO")

            # 5. ALERTA DE REPRESENTANTE (La función que pediste)
            # 5. ALERTA DE REPRESENTANTE
            if porcentaje_asistencia < 60:
                st.error(f"""
                🚨 **ALERTA DE DESERCIÓN ESCOLAR DETECTADA**
@@ -518,7 +535,7 @@

            st.markdown("---")

            # 6. HISTORIAL DE EVALUACIONES (Tus fichas desplegables, pero SOLO de este alumno)
            # 6. HISTORIAL DE EVALUACIONES (Tus fichas desplegables)
            st.markdown(f"### 📑 Historial de Evaluaciones de {alumno_sel}")

            # Pestañas para organizar la vista
@@ -528,23 +545,26 @@
                if datos_alumno.empty:
                    st.write("No hay registros.")
                else:
                    # Iteramos solo sobre los datos de este alumno, del más reciente al más antiguo
                    # Iteramos solo sobre los datos de este alumno
                    for idx, row in datos_alumno.iloc[::-1].iterrows():
                        fecha = row['FECHA']
                        actividad = row['ACTIVIDAD']
                        # Emoji según resultado (si existiera columna nota, por ahora genérico)

                        with st.expander(f"📅 {fecha} | {actividad}"):
                            st.markdown(f"**📝 Observación Docente:**")
                            st.info(f"_{row['ANECDOTA']}_")

                            st.markdown(f"**🤖 Análisis Técnico (Legado Maestro):**")
                            st.success(row['EVALUACION_IA'])
                            
                            # Aquí podríamos poner un botón de borrar evaluación específica en el futuro
                            # Casilla verde destacada
                            st.markdown(f'<div class="eval-box">{row["EVALUACION_IA"]}</div>', unsafe_allow_html=True)

            with tab_ia:
                st.info("La IA analizará todo el historial de arriba para crear un informe de lapso.")
                
                # CLAVE ÚNICA PARA GUARDAR EL INFORME DE ESTE ALUMNO ESPECÍFICO
                key_informe = f"informe_guardado_{alumno_sel}"
                
                # Botón para generar (o regenerar)
                if st.button(f"⚡ Generar Informe de Progreso para {alumno_sel}"):
                    with st.spinner("Leyendo todas las evaluaciones del estudiante..."):
                        # Recopilamos todo el texto de las IAs previas
@@ -568,15 +588,24 @@
                        5. **Recomendación Final:**
                        """

                        informe_final = generar_respuesta([
                        # Guardamos el resultado en la memoria de sesión
                        st.session_state[key_informe] = generar_respuesta([
                            {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                            {"role": "user", "content": prompt_informe}
                        ], temperatura=0.6)
                        
                        st.markdown(f'<div class="plan-box"><h3>📄 Informe de Progreso: {alumno_sel}</h3>{informe_final}</div>', unsafe_allow_html=True)
                
                # MOSTRAR EL INFORME SI EXISTE EN MEMORIA (Así no se borra al recargar)
                if key_informe in st.session_state:
                    st.markdown(f'<div class="plan-box"><h3>📄 Informe de Progreso: {alumno_sel}</h3>{st.session_state[key_informe]}</div>', unsafe_allow_html=True)
                    
                    # Botón opcional para limpiar
                    if st.button("Limpiar Informe", key=f"clean_{alumno_sel}"):
                        del st.session_state[key_informe]
                        st.rerun()

    except Exception as e:
        st.error(f"⚠️ Error conectando con la base de datos. Detalle: {e}")

# =========================================================
# 4. MI ARCHIVO PEDAGÓGICO (UI EXPANDER + BORRADO SEGURO)
# =========================================================
@@ -682,4 +711,4 @@

# --- PIE DE PÁGINA ---
st.markdown("---")
st.caption("Desarrollado por Luis Atencio | Versión: 2.2 (Corrección Registro)")
st.caption("Desarrollado por Luis Atencio | Versión: 2.3 (Sistema Blindado Anti-Trampa)")
