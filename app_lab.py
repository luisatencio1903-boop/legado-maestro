## ---------------------------------------------------------
# PROYECTO: LEGADO MAESTRO
# VERSIÓN: 4.0 (SIN BARRA LATERAL - TODO EN BARRAS PRINCIPALES)
# FECHA: Enero 2026
# AUTOR: Luis Atencio
# ---------------------------------------------------------

import streamlit as st
import os
import time
from datetime import datetime, timedelta
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered",
    initial_sidebar_state="collapsed"
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

# --- SISTEMA DE PLANIFICACIÓN ACTIVA ---
def obtener_plan_activa_usuario(usuario_nombre):
    """Obtiene la planificación activa actual del usuario desde la nube"""
    try:
        df_activa = conn.read(spreadsheet=URL_HOJA, worksheet="PLAN_ACTIVA", ttl=5)
        plan_activa = df_activa[
            (df_activa['USUARIO'] == usuario_nombre) & 
            (df_activa['ACTIVO'] == True)
        ]
        
        if not plan_activa.empty:
            # Retornar la más reciente
            return plan_activa.sort_values('FECHA_ACTIVACION', ascending=False).iloc[0].to_dict()
        return None
    except Exception as e:
        return None

def establecer_plan_activa(usuario_nombre, id_plan, contenido, rango, aula):
    """Establece una planificación como la activa para el usuario"""
    try:
        try:
            df_activa = conn.read(spreadsheet=URL_HOJA, worksheet="PLAN_ACTIVA", ttl=0)
        except:
            df_activa = pd.DataFrame(columns=[
                "USUARIO", "FECHA_ACTIVACION", "ID_PLAN", 
                "CONTENIDO_PLAN", "RANGO", "AULA", "ACTIVO"
            ])
        
        mask_usuario = df_activa['USUARIO'] == usuario_nombre
        if not df_activa[mask_usuario].empty:
            df_activa.loc[mask_usuario, 'ACTIVO'] = False
        
        nueva_activa = pd.DataFrame([{
            "USUARIO": usuario_nombre,
            "FECHA_ACTIVACION": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ID_PLAN": id_plan,
            "CONTENIDO_PLAN": contenido,
            "RANGO": rango,
            "AULA": aula,
            "ACTIVO": True
        }])
        
        df_actualizado = pd.concat([df_activa, nueva_activa], ignore_index=True)
        conn.update(spreadsheet=URL_HOJA, worksheet="PLAN_ACTIVA", data=df_actualizado)
        return True
    except Exception as e:
        st.error(f"Error al establecer plan activa: {e}")
        return False

def desactivar_plan_activa(usuario_nombre):
    """Desactiva cualquier planificación activa del usuario"""
    try:
        df_activa = conn.read(spreadsheet=URL_HOJA, worksheet="PLAN_ACTIVA", ttl=0)
        mask_usuario = df_activa['USUARIO'] == usuario_nombre
        if not df_activa[mask_usuario].empty:
            df_activa.loc[mask_usuario, 'ACTIVO'] = False
            conn.update(spreadsheet=URL_HOJA, worksheet="PLAN_ACTIVA", data=df_activa)
        return True
    except:
        return False

# --- FUNCIÓN PARA EXTRAER DESCRIPCIÓN DETALLADA DE PLANIFICACIÓN ---
def extraer_descripcion_dias(contenido_planificacion):
    """Extrae una descripción resumida de los días de la planificación"""
    try:
        dias_info = []
        lineas = contenido_planificacion.split('\n')
        
        for i, linea in enumerate(lineas):
            linea = linea.strip()
            if linea.startswith('###') or linea.startswith('##'):
                dia_keywords = ['LUNES', 'MARTES', 'MIÉRCOLES', 'MIERCOLES', 'JUEVES', 'VIERNES']
                for keyword in dia_keywords:
                    if keyword in linea.upper():
                        for j in range(i+1, min(i+10, len(lineas))):
                            if 'TÍTULO:' in lineas[j].upper() or 'TITULO:' in lineas[j].upper():
                                titulo = lineas[j].split(':', 1)[-1].strip()
                                titulo = titulo.replace('**', '').replace('*', '').strip()
                                if titulo:
                                    dia = keyword.capitalize()
                                    if keyword == 'MIERCOLES':
                                        dia = 'Miércoles'
                                    dias_info.append(f"{dia}: {titulo}")
                                break
                        break
        
        if dias_info:
            return " | ".join(dias_info[:5])
        else:
            import re
            patron = r'\*\*TÍTULO:\*\*\s*(.+?)(?:\n|$)'
            titulos = re.findall(patron, contenido_planificacion, re.IGNORECASE)
            if titulos:
                dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
                resultado = []
                for i, titulo in enumerate(titulos[:5]):
                    titulo_limpio = titulo.strip().replace('**', '').replace('*', '')
                    resultado.append(f"{dias[i]}: {titulo_limpio}")
                return " | ".join(resultado)
            
            return "Descripción no disponible"
    except Exception as e:
        return "Error extrayendo descripción"

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
                    st.query_params["u"] = cedula_limpia
                    st.success("¡Bienvenido!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Credenciales inválidas.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    st.stop()

# --- 2. CONEXIÓN CON GROQ ---
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

# --- 3. FUNCIÓN GENERADORA GENÉRICA ---
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

# --- 🧠 CEREBRO TÉCNICO ---
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

# --- 4. ESTILOS CSS MEJORADOS ---
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* RESPONSIVE PARA CELULARES */
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    .stButton > button {
        min-height: 44px !important;
        font-size: 16px !important;
        padding: 10px 15px !important;
        margin: 5px 0 !important;
    }
    
    .stTextInput input, .stTextArea textarea {
        font-size: 16px !important;
        min-height: 44px !important;
    }
    
    .stSelectbox > div > div {
        font-size: 16px !important;
        min-height: 44px !important;
    }
    
    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 18px !important; }
    p, li, span, div { font-size: 16px !important; }
    
    .stHorizontalBlock > div {
        flex-direction: column !important;
    }
    
    .stColumn {
        width: 100% !important;
        margin-bottom: 15px !important;
    }
    
    .streamlit-expanderHeader {
        font-size: 16px !important;
        padding: 12px !important;
    }
}

/* ESTILOS GENERALES */
.plan-box {
    background-color: #f0f2f6 !important;
    color: #000000 !important; 
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #0068c9;
    margin-bottom: 15px;
    font-family: sans-serif;
}

.eval-box {
    background-color: #e8f5e9 !important;
    color: #000000 !important;
    padding: 12px;
    border-radius: 6px;
    border-left: 5px solid #2e7d32;
    margin-top: 10px;
    margin-bottom: 10px;
}

.consultor-box {
    background-color: #e8f4f8 !important;
    color: #000000 !important;
    padding: 12px;
    border-radius: 6px;
    border: 1px solid #b3d7ff;
    margin-top: 10px;
}

.tarjeta-activa-simple {
    background-color: #f0f9f0 !important;
    border-radius: 6px;
    padding: 10px;
    border: 1px solid #2e7d32;
    margin-bottom: 15px;
}

/* ELIMINAR ELEMENTOS INNECESARIOS */
.planificacion-seleccionada-header {
    display: none !important;
}

.barra-verde-superior {
    display: none !important;
}

/* BOTÓN DE EMERGENCIA */
.btn-emergencia {
    background-color: #ff6b6b !important;
    color: white !important;
    border: none !important;
    font-weight: bold !important;
}

/* ESTILO PARA PLANIFICACIÓN MINISTERIAL */
.ministerial-box {
    background-color: #fff3e0 !important;
    border-left: 5px solid #ff9800 !important;
}

.ministerial-badge {
    background-color: #ff9800 !important;
    color: white !important;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7em;
    font-weight: bold;
    margin-left: 5px;
}
</style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- FUNCIÓN AUXILIAR PARA CONTENIDO DEL EXPANDER ---
def contenido_expander(index, row, es_activa, rango_display, df):
    """Contenido del expander para planificaciones en Mi Archivo Pedagógico"""
    if es_activa:
        st.success("✅ **ESTA ES TU PLANIFICACIÓN ACTIVA PARA LA SEMANA**")
        st.markdown("El sistema de evaluación buscará actividades **solo en esta planificación**.")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"**Rango:** {rango_display}")
        if 'AULA' in row and pd.notna(row['AULA']):
            st.caption(f"**Aula:** {row['AULA']}")
    
    with col_info2:
        st.caption(f"**Creada:** {row['FECHA']}")
        st.caption(f"**Estado:** {row['ESTADO']}")
    
    descripcion = extraer_descripcion_dias(row['CONTENIDO'])
    st.info(f"**📝 Descripción de la semana:** {descripcion}")
    
    with st.expander("📄 Ver contenido completo de la planificación", expanded=False):
        st.markdown(f'<div class="plan-box" style="padding:10px; font-size:0.9em;">{row["CONTENIDO"]}</div>', unsafe_allow_html=True)
    
    col_acciones = st.columns([2, 1, 1])
    
    with col_acciones[0]:
        with st.expander("🤖 Consultar sobre este plan", expanded=False):
            pregunta = st.text_input("Tu duda:", key=f"preg_{index}", placeholder="Ej: ¿Cómo evalúo esto?")
            if st.button("Consultar", key=f"btn_{index}"):
                if pregunta:
                    with st.spinner("Analizando..."):
                        prompt_contextual = f"""
                        ACTÚA COMO ASESOR PEDAGÓGICO. CONTEXTO: {row['CONTENIDO']}. PREGUNTA: "{pregunta}".
                        Responde directo y útil.
                        """
                        respuesta = generar_respuesta([
                            {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                            {"role": "user", "content": prompt_contextual}
                        ], temperatura=0.5)
                        st.markdown(f'<div class="consultor-box">💡 **Respuesta:**<br>{respuesta}</div>', unsafe_allow_html=True)
    
    with col_acciones[1]:
        if not es_activa:
            st.write("")
            if st.button("⭐ Usar Esta Semana", key=f"activar_{index}", 
                       help="Establece esta planificación como la oficial para evaluar esta semana",
                       type="secondary"):
                
                contenido = row['CONTENIDO']
                rango = rango_display
                aula = row['AULA'] if 'AULA' in row and pd.notna(row['AULA']) else "Taller Laboral"
                
                if establecer_plan_activa(
                    usuario_nombre=st.session_state.u['NOMBRE'],
                    id_plan=str(index),
                    contenido=contenido,
                    rango=rango,
                    aula=aula
                ):
                    st.success("✅ ¡Planificación establecida como ACTIVA!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
    
    with col_acciones[2]:
        esta_borrando = st.session_state.get(f"confirm_del_{index}", False)
        
        if not esta_borrando:
            st.write("")
            if st.button("🗑️", key=f"del_init_{index}", help="Eliminar esta planificación"):
                st.session_state[f"confirm_del_{index}"] = True
                st.rerun()
        else:
            st.error("⚠️ ¿Eliminar esta planificación?")
            col_conf1, col_conf2 = st.columns(2)
            with col_conf1:
                if st.button("✅ Sí, eliminar", key=f"confirm_{index}"):
                    if es_activa:
                        desactivar_plan_activa(st.session_state.u['NOMBRE'])
                    
                    df_actualizado = df.drop(index)
                    conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_actualizado)
                    
                    st.success("🗑️ Planificación eliminada.")
                    time.sleep(1)
                    st.rerun()
            
            with col_conf2:
                if st.button("❌ No, conservar", key=f"cancel_{index}"):
                    st.session_state[f"confirm_del_{index}"] = False
                    st.rerun()

# --- 5. GESTIÓN DE MEMORIA ---
if 'plan_actual' not in st.session_state: st.session_state.plan_actual = ""
if 'actividad_detectada' not in st.session_state: st.session_state.actividad_detectada = ""
if 'selected_option' not in st.session_state: 
    st.session_state.selected_option = "📝 Planificador Inteligente"
if 'conversion_ministerial' not in st.session_state:
    st.session_state.conversion_ministerial = None
if 'planificacion_ministerial_original' not in st.session_state:
    st.session_state.planificacion_ministerial_original = None

# --- 6. ENCABEZADO PRINCIPAL CON INFORMACIÓN DE PLANIFICACIÓN ACTIVA ---
st.title("🍎 Legado Maestro - Asistente Educativo")

# Mostrar información de planificación activa en la parte superior
plan_activa = obtener_plan_activa_usuario(st.session_state.u['NOMBRE'])

if plan_activa:
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f'<div class="tarjeta-activa-simple">', unsafe_allow_html=True)
        st.markdown(f"**🟢 PLANIFICACIÓN ACTIVA:** {plan_activa['RANGO']}")
        
        descripcion_detallada = extraer_descripcion_dias(plan_activa['CONTENIDO_PLAN'])
        with st.expander("📋 Ver detalles", expanded=False):
            st.caption(f"**🏫 Aula:** {plan_activa['AULA']}")
            st.caption(f"**⏰ Activada:** {plan_activa['FECHA_ACTIVACION']}")
            st.info(f"**📝 Descripción:** {descripcion_detallada}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_btn:
        st.write("")
        st.write("")
        if st.button("❌ Desactivar", key="desactivar_superior"):
            if desactivar_plan_activa(st.session_state.u['NOMBRE']):
                st.success("✅ Planificación desactivada")
                time.sleep(1)
                st.rerun()
else:
    st.warning("⚠️ **NO TIENES PLANIFICACIÓN ACTIVA**")
    st.caption("Ve a 'Mi Archivo Pedagógico' para activar una planificación para esta semana.")

st.markdown("---")

# --- 7. SISTEMA DE NAVEGACIÓN CON 2 BARRAS PRINCIPALES ---

# PRIMERA BARRA DE HERRAMIENTAS PRINCIPALES
st.markdown("### 🛠️ **HERRAMIENTAS PRINCIPALES**")
opciones_principales = [
    "📝 Planificador Inteligente",
    "📋 Planificaciones Ministeriales",
    "👨‍🎓 Evaluar Alumno",
    "📊 Registro de Evaluaciones",
    "📁 Mi Archivo Pedagógico"
]

opcion_principal = st.selectbox(
    "Selecciona una herramienta principal:",
    opciones_principales,
    index=opciones_principales.index(st.session_state.selected_option) if st.session_state.selected_option in opciones_principales else 0,
    key="selector_principal",
    label_visibility="collapsed"
)

# SEGUNDA BARRA DE HERRAMIENTAS SECUNDARIAS
st.markdown("---")
st.markdown("### 🔧 **HERRAMIENTAS ADICIONALES**")
opciones_secundarias = [
    "💡 Ideas de Actividades",
    "❓ Consultas Técnicas",
    "🌟 Mensajes Motivacionales"
]

# Mostrar las herramientas secundarias como botones
col_sec1, col_sec2, col_sec3 = st.columns(3)
with col_sec1:
    if st.button("💡 Ideas", use_container_width=True):
        st.session_state.selected_option = "💡 Ideas de Actividades"
        st.rerun()
with col_sec2:
    if st.button("❓ Consultas", use_container_width=True):
        st.session_state.selected_option = "❓ Consultas Técnicas"
        st.rerun()
with col_sec3:
    if st.button("🌟 Motivación", use_container_width=True):
        st.session_state.selected_option = "🌟 Mensajes Motivacionales"
        st.rerun()

# Actualizar estado según selección principal
if opcion_principal != st.session_state.selected_option:
    st.session_state.selected_option = opcion_principal
    st.rerun()

st.markdown("---")

# =========================================================
# 1. PLANIFICADOR INTELIGENTE
# =========================================================
if st.session_state.selected_option == "📝 Planificador Inteligente":
    st.subheader("📝 Planificador Inteligente")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio = st.text_input("Fecha inicio:", placeholder="Ej: 19/01/26")
    with col2:
        fecha_fin = st.text_input("Fecha fin:", placeholder="Ej: 23/01/26")
    with col3:
        aula = st.text_input("Aula/Taller:", value="Mantenimiento y Servicios Generales")
    
    if fecha_inicio and fecha_fin:
        rango = f"{fecha_inicio} al {fecha_fin}"
        st.info(f"📅 **Rango de planificación:** {rango}")
    else:
        rango = ""
    
    notas = st.text_area("Tema/Contenido principal:", height=150, placeholder="Describe el tema principal de la semana...")

    if st.button("🚀 Generar Planificación con IA", type="primary"):
        if fecha_inicio and fecha_fin and notas:
            with st.spinner('Creando planificación inteligente...'):
                st.session_state.temp_rango = rango
                st.session_state.temp_tema = notas
                st.session_state.temp_fecha_inicio = fecha_inicio
                st.session_state.temp_fecha_fin = fecha_fin
                
                prompt_inicial = f"""
                Actúa como Luis Atencio, experto en Educación Especial (Taller Laboral) en Venezuela.
                Planificación para: {rango}. Aula: {aula}. Tema: {notas}.

                ⚠️ IMPORTANTE: INCLUYE SIEMPRE EL RANGO DE FECHAS EN LA PRIMERA LÍNEA:
                "📅 **Rango:** {rango} | 🏫 **Aula:** {aula}"
                
                ⚠️ PASO 0: INTRODUCCIÓN OBLIGATORIA Y CERTIFICADA:
                "📝 **Planificación Sugerida y Certificada:** Esta propuesta ha sido verificada internamente para asegurar su cumplimiento con los lineamientos del **Ministerio del Poder Popular para la Educación (MPPE)** y el **Currículo Nacional Bolivariano**, adaptada específicamente para Taller Laboral."

                ⚠️ PASO 1: ESTRUCTURA DIARIA:

                ### [DÍA - FECHA ESPECÍFICA]

                1. **TÍTULO:** [Creativo y específico]
                2. **COMPETENCIA:** [Redacta la habilidad técnica específica]
                3. **EXPLORACIÓN:** [Párrafo humano]
                4. **DESARROLLO:** [Párrafo práctico]
                5. **REFLEXIÓN:** [Párrafo de cierre]
                6. **MANTENIMIENTO:** [Acción concreta]
                7. **ESTRATEGIAS:** [Técnicas]
                8. **RECURSOS:** [Materiales]

                ---
                (Repite para los 5 días).

                AL FINAL: 📚 FUNDAMENTACIÓN LEGAL
                """
                
                mensajes = [
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                    {"role": "user", "content": prompt_inicial}
                ]
                respuesta = generar_respuesta(mensajes, temperatura=0.4)
                st.session_state.plan_actual = respuesta
                st.rerun()
        else:
            st.warning("⚠️ Completa las fechas y el tema para generar la planificación.")

    if st.session_state.plan_actual:
        st.markdown("---")
        st.info("👀 **BORRADOR GENERADO:**")
        st.markdown(f'<div class="plan-box">{st.session_state.plan_actual}</div>', unsafe_allow_html=True)
        
        col_save_1, col_save_2 = st.columns([2,1])
        with col_save_1:
            if st.button("💾 GUARDAR PLANIFICACIÓN", type="primary"):
                try:
                    with st.spinner("Guardando en tu archivo..."):
                        df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                        tema_guardar = st.session_state.get('temp_tema', notas)
                        fecha_inicio_guardar = st.session_state.get('temp_fecha_inicio', fecha_inicio)
                        fecha_fin_guardar = st.session_state.get('temp_fecha_fin', fecha_fin)
                        rango_completo = f"{fecha_inicio_guardar} al {fecha_fin_guardar}"
                        
                        nueva_fila = pd.DataFrame([{
                            "FECHA": datetime.now().strftime("%d/%m/%Y"),
                            "FECHA_INICIO": fecha_inicio_guardar,
                            "FECHA_FIN": fecha_fin_guardar,
                            "RANGO": rango_completo,
                            "USUARIO": st.session_state.u['NOMBRE'], 
                            "TEMA": tema_guardar,
                            "CONTENIDO": st.session_state.plan_actual,
                            "ESTADO": "GUARDADO",
                            "HORA_INICIO": "--", 
                            "HORA_FIN": "--",
                            "AULA": aula
                        }])
                        
                        datos_actualizados = pd.concat([df_act, nueva_fila], ignore_index=True)
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=datos_actualizados)
                        st.success("✅ ¡Planificación guardada en tu archivo!")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

# =========================================================
# 2. PLANIFICACIONES MINISTERIALES (NUEVO - CONVERSOR)
# =========================================================
elif st.session_state.selected_option == "📋 Planificaciones Ministeriales":
    st.subheader("📋 Planificaciones Ministeriales")
    st.markdown("Convierte planificaciones del **Ministerio de Educación (MPPE)** al formato de **Legado Maestro**.")
    
    st.markdown("---")
    
    # Instrucciones claras
    st.info("""
    **📋 INSTRUCCIONES:**
    1. Copia la planificación enviada por el Ministerio (generalmente viene por WhatsApp/PDF)
    2. Pega en el cuadro de abajo
    3. Haz clic en **"🔄 Convertir con IA"**
    4. Revisa la planificación convertida
    5. **Guárdala** para usarla cuando corresponda
    """)
    
    # Cuadro principal para pegar planificación ministerial
    planificacion_ministerial = st.text_area(
        "**📥 PEGA AQUÍ LA PLANIFICACIÓN DEL MINISTERIO:**",
        height=200,
        placeholder="""Ejemplo de formato esperado:
LUNES: Limpieza de frutas
MARTES: Limpieza de verduras
MIÉRCOLES: Uso de jabones adecuados
JUEVES: Clasificación de materiales
VIERNES: Evaluación práctica

O también puede venir así:
- Lunes: Conociendo herramientas básicas
- Martes: Uso de productos de limpieza
- Miércoles: Práctica en superficies""",
        key="textarea_ministerial_principal"
    )
    
    # Botones de acción
    col_conv, col_limp = st.columns(2)
    with col_conv:
        if st.button("🔄 CONVERTIR CON IA", 
                    key="convertir_ministerial_principal",
                    disabled=not planificacion_ministerial,
                    type="primary",
                    use_container_width=True):
            if planificacion_ministerial:
                with st.spinner("🔄 Adaptando formato ministerial..."):
                    # Calcular fechas de esta semana
                    hoy = datetime.now()
                    inicio_semana = hoy - timedelta(days=hoy.weekday())
                    fin_semana = inicio_semana + timedelta(days=4)
                    rango_semana = f"{inicio_semana.strftime('%d/%m/%y')} al {fin_semana.strftime('%d/%m/%y')}"
                    
                    prompt_conversion = f"""
                    ERES LEGADO MAESTRO - CONVERSOR MINISTERIAL OFICIAL
                    
                    TEXTO ORIGINAL DEL MINISTERIO DE EDUCACIÓN (MPPE):
                    {planificacion_ministerial}
                    
                    TU MISIÓN: Convertir esta planificación ministerial en una planificación completa de 5 días para Taller Laboral.
                    
                    FECHA DE ESTA SEMANA: {rango_semana}
                    
                    FORMATO EXACTO REQUERIDO:
                    
                    📅 **Rango:** {rango_semana}
                    🏫 **Aula:** Taller Laboral
                    
                    📝 **Planificación Sugerida y Certificada:** Esta propuesta ha sido verificada internamente para asegurar su cumplimiento con los lineamientos del **Ministerio del Poder Popular para la Educación (MPPE)** y el **Currículo Nacional Bolivariano**, adaptada específicamente para Taller Laboral.
                    
                    ### LUNES - {inicio_semana.strftime('%d/%m/%Y')}
                    1. **TÍTULO:** [Título exacto del Ministerio para Lunes]
                    2. **COMPETENCIA:** [Competencia específica y medible]
                    3. **EXPLORACIÓN:** [Párrafo humano y natural de inicio]
                    4. **DESARROLLO:** [Párrafo práctico y concreto]
                    5. **REFLEXIÓN:** [Párrafo de cierre y aprendizaje]
                    6. **MANTENIMIENTO:** [Acción concreta de mantenimiento]
                    7. **ESTRATEGIAS:** [Técnicas pedagógicas aplicables]
                    8. **RECURSOS:** [Materiales realistas disponibles]
                    
                    ### MARTES - {(inicio_semana + timedelta(days=1)).strftime('%d/%m/%Y')}
                    [Misma estructura para Martes]
                    
                    ### MIÉRCOLES - {(inicio_semana + timedelta(days=2)).strftime('%d/%m/%Y')}
                    [Misma estructura para Miércoles]
                    
                    ### JUEVES - {(inicio_semana + timedelta(days=3)).strftime('%d/%m/%Y')}
                    [Misma estructura para Jueves]
                    
                    ### VIERNES - {fin_semana.strftime('%d/%m/%Y')}
                    [Misma estructura para Viernes]
                    
                    📚 **FUNDAMENTACIÓN LEGAL:** 
                    Esta planificación se fundamenta en el Artículo 6 de la Ley Orgánica de Educación (2009) y los lineamientos del Currículo Nacional Bolivariano para Educación Especial.
                    
                    🔹 **ORIGEN:** MINISTERIO DE EDUCACIÓN (MPPE) - Adaptado por LEGADO MAESTRO
                    """
                    
                    conversion = generar_respuesta([
                        {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                        {"role": "user", "content": prompt_conversion}
                    ], temperatura=0.5)
                    
                    st.session_state.conversion_ministerial = conversion
                    st.session_state.planificacion_ministerial_original = planificacion_ministerial
                    st.rerun()
    
    with col_limp:
        if st.button("🧹 LIMPIAR", 
                    key="limpiar_ministerial_principal",
                    type="secondary",
                    use_container_width=True):
            st.session_state.conversion_ministerial = None
            st.session_state.planificacion_ministerial_original = None
            st.rerun()
    
    # Mostrar conversión si existe
    if st.session_state.conversion_ministerial:
        st.markdown("---")
        st.success("✅ **PLANIFICACIÓN CONVERTIDA**")
        st.markdown('<span class="ministerial-badge">MINISTERIO</span>', unsafe_allow_html=True)
        
        with st.expander("📋 Ver planificación adaptada", expanded=True):
            st.markdown(f'<div class="plan-box ministerial-box">{st.session_state.conversion_ministerial}</div>', unsafe_allow_html=True)
        
        # Botones para guardar
        st.markdown("---")
        st.markdown("### 💾 **GUARDAR PLANIFICACIÓN**")
        
        col_guardar, col_descartar, col_activar = st.columns(3)
        
        with col_guardar:
            if st.button("💾 GUARDAR EN ARCHIVO", 
                        type="primary",
                        key="guardar_ministerial_principal",
                        use_container_width=True):
                
                try:
                    with st.spinner("Guardando planificación ministerial..."):
                        df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                        
                        # Calcular fechas
                        hoy = datetime.now()
                        inicio_semana = hoy - timedelta(days=hoy.weekday())
                        fin_semana = inicio_semana + timedelta(days=4)
                        
                        nueva_fila = pd.DataFrame([{
                            "FECHA": datetime.now().strftime("%d/%m/%Y"),
                            "FECHA_INICIO": inicio_semana.strftime("%d/%m/%y"),
                            "FECHA_FIN": fin_semana.strftime("%d/%m/%y"),
                            "RANGO": f"{inicio_semana.strftime('%d/%m/%y')} al {fin_semana.strftime('%d/%m/%y')}",
                            "USUARIO": st.session_state.u['NOMBRE'], 
                            "TEMA": "Planificación Ministerial Adaptada",
                            "CONTENIDO": st.session_state.conversion_ministerial,
                            "ESTADO": "GUARDADO",
                            "HORA_INICIO": "--", 
                            "HORA_FIN": "--",
                            "AULA": "Taller Laboral",
                            "ORIGEN": "MINISTERIO",
                            "NOTAS": "Convertida desde formato ministerial"
                        }])
                        
                        datos_actualizados = pd.concat([df_act, nueva_fila], ignore_index=True)
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=datos_actualizados)
                        
                        del st.session_state.conversion_ministerial
                        del st.session_state.planificacion_ministerial_original
                        
                        st.success("✅ ¡Planificación ministerial guardada!")
                        st.info("Ahora ve a 'Mi Archivo Pedagógico' para activarla cuando corresponda.")
                        time.sleep(3)
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
        
        with col_descartar:
            if st.button("🗑️ DEScartar", 
                        type="secondary",
                        key="descartar_ministerial_principal",
                        use_container_width=True):
                del st.session_state.conversion_ministerial
                del st.session_state.planificacion_ministerial_original
                st.rerun()
        
        with col_activar:
            if st.button("⭐ ACTIVAR AHORA", 
                        help="Guardar y activar inmediatamente",
                        key="activar_ministerial_principal",
                        use_container_width=True):
                
                try:
                    with st.spinner("Activando planificación ministerial..."):
                        # Primero guardar
                        df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                        
                        hoy = datetime.now()
                        inicio_semana = hoy - timedelta(days=hoy.weekday())
                        fin_semana = inicio_semana + timedelta(days=4)
                        rango = f"{inicio_semana.strftime('%d/%m/%y')} al {fin_semana.strftime('%d/%m/%y')}"
                        
                        nueva_fila = pd.DataFrame([{
                            "FECHA": datetime.now().strftime("%d/%m/%Y"),
                            "FECHA_INICIO": inicio_semana.strftime("%d/%m/%y"),
                            "FECHA_FIN": fin_semana.strftime("%d/%m/%y"),
                            "RANGO": rango,
                            "USUARIO": st.session_state.u['NOMBRE'], 
                            "TEMA": "Planificación Ministerial Adaptada",
                            "CONTENIDO": st.session_state.conversion_ministerial,
                            "ESTADO": "GUARDADO",
                            "HORA_INICIO": "--", 
                            "HORA_FIN": "--",
                            "AULA": "Taller Laboral",
                            "ORIGEN": "MINISTERIO"
                        }])
                        
                        datos_actualizados = pd.concat([df_act, nueva_fila], ignore_index=True)
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=datos_actualizados)
                        
                        # Ahora activar
                        if establecer_plan_activa(
                            usuario_nombre=st.session_state.u['NOMBRE'],
                            id_plan=str(len(datos_actualizados) - 1),
                            contenido=st.session_state.conversion_ministerial,
                            rango=rango,
                            aula="Taller Laboral"
                        ):
                            del st.session_state.conversion_ministerial
                            del st.session_state.planificacion_ministerial_original
                            
                            st.success("✅ ¡Planificación ministerial guardada y ACTIVADA!")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        
                except Exception as e:
                    st.error(f"Error: {e}")

# =========================================================
# 3. EVALUAR ALUMNO
# =========================================================
elif st.session_state.selected_option == "👨‍🎓 Evaluar Alumno":
    st.subheader("👨‍🎓 Evaluar Alumno")
    
    fecha_segura_ve = datetime.utcnow() - timedelta(hours=4)
    fecha_hoy_str = fecha_segura_ve.strftime("%d/%m/%Y")
    
    plan_activa = obtener_plan_activa_usuario(st.session_state.u['NOMBRE'])
    
    if not plan_activa:
        st.error("""
        🚨 **NO TIENES PLANIFICACIÓN ACTIVA**
        
        Para evaluar, primero activa una planificación en **'Mi Archivo Pedagógico'**.
        """)
        if st.button("📁 Ir a Mi Archivo Pedagógico"):
            st.session_state.selected_option = "📁 Mi Archivo Pedagógico"
            st.rerun()
        st.stop()
    
    with st.container():
        st.markdown('<div class="tarjeta-activa-simple">', unsafe_allow_html=True)
        st.success(f"**📌 EVALUANDO CONTRA:** {plan_activa['RANGO']}")
        
        descripcion_detallada = extraer_descripcion_dias(plan_activa['CONTENIDO_PLAN'])
        with st.expander("📋 Ver planificación activa", expanded=False):
            st.caption(f"**🏫 Aula:** {plan_activa['AULA']}")
            st.caption(f"**📝 Descripción:** {descripcion_detallada}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    if st.button("🔍 Buscar Actividad de HOY", type="primary"):
        try:
            with st.spinner("Buscando actividad para hoy..."):
                contenido_planificacion = plan_activa['CONTENIDO_PLAN']
                
                prompt_busqueda = f"""
                Eres un asistente pedagógico especializado en analizar planificaciones.
                
                **PLANIFICACIÓN OFICIAL DE LA SEMANA:**
                {contenido_planificacion[:8000]}
                
                **INSTRUCCIÓN:** Hoy es {fecha_hoy_str}. 
                
                **TU TAREA:** 
                1. Revisa la planificación anterior
                2. Identifica EXACTAMENTE qué actividad está programada para HOY
                3. Si encuentras una actividad para hoy, responde SOLO con el NOMBRE/TÍTULO de esa actividad
                4. Si NO hay actividad programada para hoy, responde: "NO_HAY_ACTIVIDAD_PARA_HOY"
                """
                
                resultado = generar_respuesta([
                    {"role": "system", "content": "Eres un analista de planificaciones preciso."},
                    {"role": "user", "content": prompt_busqueda}
                ], temperatura=0.1)
                
                resultado_limpio = resultado.strip().replace('"', '').replace("'", "")
                
                if "NO_HAY_ACTIVIDAD" in resultado_limpio.upper() or len(resultado_limpio) < 5:
                    st.session_state.actividad_detectada = "NO HAY ACTIVIDAD PROGRAMADA PARA HOY"
                    st.error("❌ No hay actividades programadas para hoy.")
                else:
                    st.session_state.actividad_detectada = resultado_limpio
                    st.success(f"✅ **Actividad encontrada:** {resultado_limpio}")
                    
        except Exception as e:
            st.error(f"Error en la búsqueda: {e}")
    
    st.markdown("---")
    st.subheader("Registro de Evaluación")
    
    actividad_final = st.text_input(
        "**Actividad Programada:**",
        value=st.session_state.get('actividad_detectada', ''),
        disabled=True
    )
    
    estudiante = st.text_input("**Nombre del Estudiante:**", placeholder="Ej: Juan Pérez")
    anecdota = st.text_area("**Observación del Desempeño:**", 
                           height=100, 
                           placeholder="Describe específicamente qué hizo el estudiante hoy...")
    
    if st.button("⚡ Generar Evaluación", type="primary"):
        if not estudiante or not anecdota:
            st.warning("⚠️ Completa todos los campos.")
        elif "NO HAY ACTIVIDAD" in actividad_final:
            st.error("❌ No puedes evaluar sin actividad programada.")
        else:
            with st.spinner("Generando evaluación..."):
                prompt_eval = f"""
                ACTÚA COMO EXPERTO EN EVALUACIÓN DE EDUCACIÓN ESPECIAL (VENEZUELA).
                
                DATOS DE EVALUACIÓN:
                - Fecha: {fecha_hoy_str}
                - Estudiante: {estudiante}
                - Actividad Programada: {actividad_final}
                - Observación del Docente: "{anecdota}"
                
                GENERA UNA EVALUACIÓN TÉCNICA que incluya:
                1. **Análisis del Desempeño:** Basado en la observación
                2. **Nivel de Logro:** (Consolidado / En Proceso / Iniciado)
                3. **Recomendación Pedagógica:** Breve sugerencia para seguir trabajando
                """
                
                evaluacion_generada = generar_respuesta([
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                    {"role": "user", "content": prompt_eval}
                ], temperatura=0.5)
                
                st.session_state.eval_resultado = evaluacion_generada
                st.session_state.estudiante_evaluado = estudiante
                st.session_state.anecdota_guardada = anecdota
    
    if 'eval_resultado' in st.session_state:
        st.markdown("---")
        st.subheader("📋 Evaluación Generada")
        st.markdown(f'<div class="eval-box">{st.session_state.eval_resultado}</div>', unsafe_allow_html=True)
        
        if st.button("💾 GUARDAR EVALUACIÓN", type="secondary"):
            try:
                df_evals = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                
                nueva_eval = pd.DataFrame([{
                    "FECHA": fecha_hoy_str,
                    "USUARIO": st.session_state.u['NOMBRE'],
                    "ESTUDIANTE": st.session_state.estudiante_evaluado,
                    "ACTIVIDAD": actividad_final,
                    "ANECDOTA": st.session_state.anecdota_guardada,
                    "EVALUACION_IA": st.session_state.eval_resultado,
                    "PLANIFICACION_ACTIVA": plan_activa['RANGO'],
                    "RESULTADO": "Registrado"
                }])
                
                df_actualizado = pd.concat([df_evals, nueva_eval], ignore_index=True)
                conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=df_actualizado)
                
                st.success(f"✅ Evaluación de {st.session_state.estudiante_evaluado} guardada.")
                
                del st.session_state.eval_resultado
                del st.session_state.estudiante_evaluado
                del st.session_state.anecdota_guardada
                
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al guardar: {e}")

# =========================================================
# 4. REGISTRO DE EVALUACIONES
# =========================================================
elif st.session_state.selected_option == "📊 Registro de Evaluaciones":
    st.subheader("📊 Registro de Evaluaciones")
    
    try:
        df_e = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
        mis_evals = df_e[df_e['USUARIO'] == st.session_state.u['NOMBRE']]
        
        if mis_evals.empty:
            st.info("📭 Aún no has registrado evaluaciones.")
        else:
            lista_alumnos = sorted(mis_evals['ESTUDIANTE'].unique().tolist())
            alumno_sel = st.selectbox("📂 Seleccionar Estudiante:", lista_alumnos, key="selector_alumno")
            
            datos_alumno = mis_evals[mis_evals['ESTUDIANTE'] == alumno_sel]
            
            st.markdown(f"### 📑 Historial de {alumno_sel}")
            
            for idx, row in datos_alumno.iloc[::-1].iterrows():
                with st.expander(f"📅 {row['FECHA']} | {row['ACTIVIDAD']}"):
                    st.markdown(f"**📝 Observación:**")
                    st.info(f"_{row['ANECDOTA']}_")
                    
                    st.markdown(f"**🤖 Análisis Técnico:**")
                    st.markdown(f'<div class="eval-box">{row["EVALUACION_IA"]}</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error: {e}")

# =========================================================
# 5. MI ARCHIVO PEDAGÓGICO
# =========================================================
elif st.session_state.selected_option == "📁 Mi Archivo Pedagógico":
    st.subheader(f"📁 Mi Archivo Pedagógico")
    
    plan_activa_actual = obtener_plan_activa_usuario(st.session_state.u['NOMBRE'])
    
    if plan_activa_actual:
        st.markdown("### 🟢 **PLANIFICACIÓN ACTIVA ACTUAL**")
        st.markdown(f"**📅 Rango:** {plan_activa_actual['RANGO']}")
        st.markdown(f"**🏫 Aula:** {plan_activa_actual['AULA']}")
        
        if st.button("❌ Desactivar Esta Planificación", key="desactivar_archivo"):
            if desactivar_plan_activa(st.session_state.u['NOMBRE']):
                st.success("✅ Planificación desactivada.")
                time.sleep(1)
                st.rerun()
    else:
        st.warning("⚠️ No tienes planificación activa.")
    
    st.markdown("---")
    st.info("📌 **Tus planificaciones guardadas:**")
    
    try:
        df = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
        mis_planes = df[df['USUARIO'] == st.session_state.u['NOMBRE']]
        
        if mis_planes.empty:
            st.warning("Aún no tienes planificaciones guardadas.")
        else:
            contenido_activo_actual = plan_activa_actual['CONTENIDO_PLAN'] if plan_activa_actual else None
            
            for index, row in mis_planes.iloc[::-1].iterrows():
                es_activa = (contenido_activo_actual == row['CONTENIDO'])
                
                if 'RANGO' in row and pd.notna(row['RANGO']):
                    rango_display = row['RANGO']
                elif 'FECHA_INICIO' in row and 'FECHA_FIN' in row and pd.notna(row['FECHA_INICIO']) and pd.notna(row['FECHA_FIN']):
                    rango_display = f"{row['FECHA_INICIO']} al {row['FECHA_FIN']}"
                else:
                    rango_display = f"Creada: {row['FECHA']}"
                
                tema_corto = str(row['TEMA'])[:40] + "..." if len(str(row['TEMA'])) > 40 else str(row['TEMA'])
                
                if es_activa:
                    etiqueta = f"🟢 **ACTIVA** | 📅 {rango_display} | 📌 {tema_corto}"
                else:
                    etiqueta = f"📅 {rango_display} | 📌 {tema_corto}"
                
                with st.expander(etiqueta, expanded=es_activa):
                    contenido_expander(index, row, es_activa, rango_display, df)

    except Exception as e:
        st.error(f"Error: {e}")

# =========================================================
# 6. IDEAS DE ACTIVIDADES
# =========================================================
elif st.session_state.selected_option == "💡 Ideas de Actividades":
    st.subheader("💡 Ideas de Actividades")
    
    tema = st.text_input("Tema a trabajar:", placeholder="Ej: Herramientas de limpieza")
    if st.button("✨ Sugerir Actividades"):
        if tema:
            res = generar_respuesta([
                {"role": "system", "content": INSTRUCCIONES_TECNICAS}, 
                {"role": "user", "content": f"3 actividades DUA para {tema} en Taller Laboral. Formato: 1) Título, 2) Materiales, 3) Instrucciones paso a paso."}
            ], temperatura=0.7)
            st.markdown(f'<div class="plan-box">{res}</div>', unsafe_allow_html=True)
        else:
            st.warning("Ingresa un tema primero.")

# =========================================================
# 7. CONSULTAS TÉCNICAS
# =========================================================
elif st.session_state.selected_option == "❓ Consultas Técnicas":
    st.subheader("❓ Consultas Técnicas")
    
    duda = st.text_area("Consulta Legal/Técnica:", 
                       placeholder="Ej: ¿Qué artículo de la LOE respalda la evaluación cualitativa en Educación Especial?",
                       height=150)
    if st.button("🔍 Buscar Respuesta"):
        if duda:
            res = generar_respuesta([
                {"role": "system", "content": INSTRUCCIONES_TECNICAS}, 
                {"role": "user", "content": f"Responde técnicamente y cita la ley o currículo: {duda}"}
            ], temperatura=0.5)
            st.markdown(f'<div class="plan-box">{res}</div>', unsafe_allow_html=True)
        else:
            st.warning("Ingresa tu consulta primero.")

# =========================================================
# 8. MENSAJES MOTIVACIONALES
# =========================================================
elif st.session_state.selected_option == "🌟 Mensajes Motivacionales":
    st.subheader("🌟 Mensajes Motivacionales")
    
    if st.button("❤️ Recibir Dosis de Ánimo", use_container_width=True):
        estilos_posibles = [
            {"rol": "El Colega Realista", "instruccion": "Dile algo crudo pero esperanzador sobre enseñar. Humor venezolano. NO SALUDES."},
            {"rol": "El Sabio Espiritual", "instruccion": "Cita bíblica de fortaleza y frase docente. NO SALUDES."},
            {"rol": "El Motivador Directo", "instruccion": "Orden cariñosa para no rendirse. NO SALUDES."}
        ]
        estilo = random.choice(estilos_posibles)
        prompt = "Dame el mensaje."
        with st.spinner(f"Modo {estilo['rol']}..."):
            res = generar_respuesta([{"role": "system", "content": f"ERES LEGADO MAESTRO. ROL: {estilo['rol']}. TAREA: {estilo['instruccion']}"}, {"role": "user", "content": prompt}], 1.0)
            st.markdown(f'<div class="plan-box" style="border-left: 5px solid #ff4b4b;"><h3>❤️ {estilo["rol"]}</h3><div class="mensaje-texto">"{res}"</div></div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)
with col_footer1:
    if st.button("🗑️ Limpiar Memoria", use_container_width=True):
        st.session_state.plan_actual = ""
        st.session_state.actividad_detectada = ""
        st.rerun()
with col_footer2:
    if st.button("🔄 Recargar Página", use_container_width=True):
        st.rerun()
with col_footer3:
    if st.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state.auth = False
        st.session_state.u = None
        st.query_params.clear()
        st.rerun()

st.caption("Desarrollado por Luis Atencio | Versión: 4.0 (Sin Barra Lateral) | 🍎 Legado Maestro")
