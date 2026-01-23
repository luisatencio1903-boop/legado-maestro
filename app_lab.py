## ---------------------------------------------------------
# PROYECTO: LEGADO MAESTRO
# VERSIÓN: 5.0 (INTERFAZ PROFESIONAL REDISEÑADA)
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 1. Función para limpiar cédulas
def limpiar_id(v): return str(v).strip().split('.')[0].replace(',', '').replace('.', '')

# 2. Inicializar Estado de Autenticación
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'u' not in st.session_state:
    st.session_state.u = None

# 3. Conexión a Base de Datos
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

# --- FUNCIÓN PARA EXTRAER DESCRIPCIÓN DETALLADA ---
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

# --- AUTO-LOGIN ---
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
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    .login-logo {
        text-align: center;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # Logo
            st.markdown('<div class="login-logo">', unsafe_allow_html=True)
            if os.path.exists("logo_legado.png"):
                st.image("logo_legado.png", width=120)
            else:
                st.markdown("""
                <div style="text-align: center; margin: 20px 0;">
                    <span style="font-size: 50px;">🍎</span>
                    <h1>Legado Maestro</h1>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Formulario
            st.markdown("### Acceso al Sistema")
            
            c_in = st.text_input("**Cédula de Identidad:**", key="login_c")
            p_in = st.text_input("**Contraseña:**", type="password", key="login_p")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔐 **Iniciar Sesión**", use_container_width=True, type="primary"):
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
            
            with col_btn2:
                if st.button("🔄 **Limpiar**", use_container_width=True):
                    st.rerun()
            
            st.markdown("""
            <div style="text-align: center; margin-top: 30px; color: #666; font-size: 0.9em;">
                <p>Desarrollado por Luis Atencio | Bachiller Docente</p>
                <p>T.E.L E.R.A.C - Venezuela</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- CONEXIÓN CON GROQ ---
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

# --- FUNCIÓN GENERADORA GENÉRICA ---
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

# --- INSTRUCCIONES TÉCNICAS ---
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

# --- CSS PROFESIONAL ---
st.markdown("""
<style>
/* RESET Y BASE */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* OCULTAR ELEMENTOS STREAMLIT */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* CONTENEDOR PRINCIPAL */
.main {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
    padding: 20px;
}

/* HEADER */
.app-header {
    background: white;
    border-radius: 15px;
    padding: 20px 30px;
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
}

.logo-container img {
    width: 60px;
    height: 60px;
    border-radius: 10px;
}

.app-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
    margin: 0;
}

.app-subtitle {
    font-size: 1rem;
    color: #7f8c8d;
    margin: 0;
}

.user-info {
    text-align: right;
}

.user-name {
    font-weight: 600;
    color: #2c3e50;
}

.user-role {
    font-size: 0.9rem;
    color: #7f8c8d;
}

/* TARJETAS DE HERRAMIENTAS */
.tools-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 25px;
    margin-bottom: 40px;
}

.tool-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    height: 100%;
    display: flex;
    flex-direction: column;
}

.tool-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    border-color: #3498db;
}

.tool-card.primary {
    background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
    color: white;
}

.tool-card.secondary {
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
    color: white;
}

.tool-icon {
    font-size: 2.5rem;
    margin-bottom: 15px;
}

.tool-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin-bottom: 10px;
}

.tool-description {
    font-size: 0.95rem;
    color: inherit;
    opacity: 0.9;
    line-height: 1.5;
    flex-grow: 1;
}

.tool-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    margin-top: 10px;
}

/* PÁGINAS DE HERRAMIENTAS */
.page-container {
    background: white;
    border-radius: 15px;
    padding: 30px;
    margin-top: 20px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #f1f1f1;
}

.page-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 10px;
}

.back-button {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
}

.back-button:hover {
    background: #2980b9;
    transform: translateX(-3px);
}

/* FORMULARIOS */
.form-container {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 25px;
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 20px;
}

.form-label {
    display: block;
    margin-bottom: 8px;
    font-weight: 600;
    color: #2c3e50;
}

.form-input, .form-textarea {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
    outline: none;
}

.form-textarea {
    min-height: 120px;
    resize: vertical;
}

/* BOTONES */
.btn {
    padding: 12px 25px;
    border-radius: 8px;
    border: none;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}

.btn-primary {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
    background: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background: #7f8c8d;
}

.btn-success {
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
    color: white;
}

.btn-success:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
}

.btn-danger {
    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    color: white;
}

/* CAJAS DE CONTENIDO */
.content-box {
    background: white;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    border-left: 4px solid #3498db;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

.content-box.success {
    border-left-color: #2ecc71;
    background: #f0f9f0;
}

.content-box.warning {
    border-left-color: #f39c12;
    background: #fef9e7;
}

.content-box.info {
    border-left-color: #3498db;
    background: #e8f4fc;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .app-header {
        flex-direction: column;
        text-align: center;
        gap: 15px;
    }
    
    .user-info {
        text-align: center;
    }
    
    .tools-container {
        grid-template-columns: 1fr;
    }
    
    .page-container {
        padding: 20px;
    }
    
    .page-header {
        flex-direction: column;
        gap: 15px;
        text-align: center;
    }
}

/* INDICADOR DE PLANIFICACIÓN ACTIVA */
.plan-activa-indicator {
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.plan-activa-text {
    font-weight: 600;
    font-size: 1.1rem;
}

.plan-activa-date {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* FOOTER */
.app-footer {
    text-align: center;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    color: #7f8c8d;
    font-size: 0.9rem;
}

/* UTILIDADES */
.text-center { text-align: center; }
.mt-20 { margin-top: 20px; }
.mb-20 { margin-bottom: 20px; }
.mb-30 { margin-bottom: 30px; }
.p-20 { padding: 20px; }
.w-100 { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

if 'plan_actual' not in st.session_state:
    st.session_state.plan_actual = ""

if 'actividad_detectada' not in st.session_state:
    st.session_state.actividad_detectada = ""

if 'conversion_ministerial' not in st.session_state:
    st.session_state.conversion_ministerial = None

# --- FUNCIONES DE NAVEGACIÓN ---
def go_to_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

def go_home():
    st.session_state.current_page = 'home'
    st.rerun()

# --- HEADER COMÚN ---
def render_header():
    plan_activa = obtener_plan_activa_usuario(st.session_state.u['NOMBRE'])
    
    col1, col2, col3 = st.columns([2, 4, 2])
    
    with col1:
        if os.path.exists("logo_legado.png"):
            st.image("logo_legado.png", width=50)
        else:
            st.markdown('<div style="font-size: 2rem;">🍎</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<h1 class="app-title">Legado Maestro</h1>', unsafe_allow_html=True)
        st.markdown(f'<p class="app-subtitle">Asistente Educativo - Taller Laboral</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="user-info">', unsafe_allow_html=True)
        st.markdown(f'<div class="user-name">{st.session_state.u["NOMBRE"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-role">Docente Especialista</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Indicador de planificación activa (solo en páginas relevantes)
    if plan_activa and st.session_state.current_page not in ['home', 'archivo']:
        st.markdown(f'''
        <div class="plan-activa-indicator">
            <div>
                <div class="plan-activa-text">📌 Planificación Activa</div>
                <div class="plan-activa-date">{plan_activa['RANGO']} | {plan_activa['AULA']}</div>
            </div>
            <button class="btn btn-secondary" onclick="window.location.href='?page=archivo'">Cambiar</button>
        </div>
        ''', unsafe_allow_html=True)

# --- PÁGINA PRINCIPAL (HOME) ---
def render_home():
    render_header()
    
    st.markdown("""
    <div class="text-center mb-30">
        <h2>🛠️ Panel de Herramientas Docentes</h2>
        <p class="app-subtitle">Selecciona una herramienta para comenzar</p>
    </div>
    """, unsafe_allow_html=True)
    
    # HERRAMIENTAS PRINCIPALES
    st.markdown('<h3 class="mb-20">📋 Herramientas Principales</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="tool-card primary" onclick="window.location.href='?page=planificador'">
            <div class="tool-icon">📝</div>
            <div class="tool-title">Planificador Inteligente</div>
            <div class="tool-description">Crea planificaciones semanales personalizadas para Taller Laboral con IA</div>
            <div class="tool-badge">Herramienta Principal</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="tool-card" onclick="window.location.href='?page=ministerial'">
            <div class="tool-icon">📋</div>
            <div class="tool-title">Planificaciones Ministeriales</div>
            <div class="tool-description">Convierte planificaciones del MPPE al formato de Taller Laboral</div>
            <div class="tool-badge">Adaptador IA</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="tool-card" onclick="window.location.href='?page=evaluar'">
            <div class="tool-icon">👨‍🎓</div>
            <div class="tool-title">Evaluar Alumno</div>
            <div class="tool-description">Registra y analiza el desempeño diario de estudiantes</div>
            <div class="tool-badge">Evaluación</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tool-card" onclick="window.location.href='?page=registros'">
            <div class="tool-icon">📊</div>
            <div class="tool-title">Registro de Evaluaciones</div>
            <div class="tool-description">Consulta el historial y genera informes de progreso</div>
            <div class="tool-badge">Seguimiento</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="tool-card secondary" onclick="window.location.href='?page=archivo'">
            <div class="tool-icon">📁</div>
            <div class="tool-title">Mi Archivo Pedagógico</div>
            <div class="tool-description">Gestiona todas tus planificaciones guardadas y activa</div>
            <div class="tool-badge">Archivo</div>
        </div>
        """, unsafe_allow_html=True)
    
    # HERRAMIENTAS ADICIONALES
    st.markdown('<h3 class="mt-20 mb-20">✨ Herramientas Adicionales</h3>', unsafe_allow_html=True)
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        if st.button("💡 Ideas de Actividades", use_container_width=True, type="secondary"):
            go_to_page('ideas')
    
    with col_a2:
        if st.button("❓ Consultas Técnicas", use_container_width=True, type="secondary"):
            go_to_page('consultas')
    
    with col_a3:
        if st.button("🌟 Mensajes Motivacionales", use_container_width=True, type="secondary"):
            go_to_page('motivacion')
    
    # FOOTER
    st.markdown("""
    <div class="app-footer">
        <p>Desarrollado por Luis Atencio | Bachiller Docente | T.E.L E.R.A.C</p>
        <p>Versión 5.0 | Sistema Legado Maestro</p>
    </div>
    """, unsafe_allow_html=True)

# --- PÁGINA: PLANIFICADOR INTELIGENTE ---
def render_planificador():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    # HEADER DE PÁGINA
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">📝 Planificador Inteligente</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    # FORMULARIO
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_inicio = st.text_input("**Fecha de inicio:**", placeholder="Ej: 19/01/26", key="fecha_inicio_plan")
    with col2:
        fecha_fin = st.text_input("**Fecha de finalización:**", placeholder="Ej: 23/01/26", key="fecha_fin_plan")
    with col3:
        aula = st.text_input("**Aula/Taller:**", value="Mantenimiento y Servicios Generales", key="aula_plan")
    
    if fecha_inicio and fecha_fin:
        rango = f"{fecha_inicio} al {fecha_fin}"
        st.info(f"📅 **Rango de planificación:** {rango}")
    
    notas = st.text_area("**Tema/Contenido principal de la semana:**", 
                        height=120, 
                        placeholder="Describe el tema principal que desarrollarás esta semana...",
                        key="notas_plan")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # BOTÓN GENERAR
    col_gen, col_clear = st.columns([3, 1])
    with col_gen:
        if st.button("🚀 Generar Planificación con IA", type="primary", use_container_width=True):
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
    
    with col_clear:
        if st.button("🧹 Limpiar", use_container_width=True, type="secondary"):
            st.session_state.plan_actual = ""
            st.rerun()
    
    # MOSTRAR RESULTADO
    if st.session_state.plan_actual:
        st.markdown("---")
        st.markdown("### 📋 Borrador Generado")
        st.markdown(f'<div class="content-box">{st.session_state.plan_actual}</div>', unsafe_allow_html=True)
        
        # BOTÓN GUARDAR
        if st.button("💾 Guardar Planificación en Mi Archivo", type="primary", use_container_width=True):
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
                    
                    st.success("✅ ¡Planificación guardada exitosamente!")
                    st.info("Puedes activarla desde 'Mi Archivo Pedagógico'")
                    time.sleep(2)
                    go_to_page('archivo')
                    
            except Exception as e:
                st.error(f"Error al guardar: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: PLANIFICACIONES MINISTERIALES ---
def render_ministerial():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    # HEADER DE PÁGINA
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">📋 Planificaciones Ministeriales</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    # INSTRUCCIONES
    st.markdown("""
    <div class="content-box info">
        <h4>📋 ¿Cómo usar esta herramienta?</h4>
        <ol>
            <li>Copia la planificación enviada por el Ministerio (WhatsApp/PDF)</li>
            <li>Pega en el cuadro de abajo</li>
            <li>Haz clic en <strong>"🔄 Convertir con IA"</strong></li>
            <li>Revisa la planificación convertida al formato de Taller Laboral</li>
            <li>Guárdala para usarla cuando corresponda</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # CUADRO PARA PEGAR
    planificacion_ministerial = st.text_area(
        "**📥 Pega aquí la planificación del Ministerio (MPPE):**",
        height=200,
        placeholder="""Ejemplo de formato esperado:
LUNES: Limpieza de frutas
MARTES: Limpieza de verduras
MIÉRCOLES: Uso de jabones adecuados
JUEVES: Clasificación de materiales
VIERNES: Evaluación práctica""",
        key="textarea_ministerial"
    )
    
    # BOTONES
    col_conv, col_limp = st.columns(2)
    with col_conv:
        if st.button("🔄 Convertir con IA", 
                    disabled=not planificacion_ministerial,
                    type="primary",
                    use_container_width=True):
            if planificacion_ministerial:
                with st.spinner("🔄 Adaptando formato ministerial..."):
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
                    
                    [Repetir para Martes, Miércoles, Jueves y Viernes]
                    
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
        if st.button("🧹 Limpiar", 
                    type="secondary",
                    use_container_width=True):
            st.session_state.conversion_ministerial = None
            st.session_state.planificacion_ministerial_original = None
            st.rerun()
    
    # MOSTRAR CONVERSIÓN
    if st.session_state.conversion_ministerial:
        st.markdown("---")
        st.markdown("### ✅ Planificación Convertida")
        
        with st.expander("📋 Ver planificación adaptada", expanded=True):
            st.markdown(f'<div class="content-box">{st.session_state.conversion_ministerial}</div>', unsafe_allow_html=True)
        
        # BOTONES DE ACCIÓN
        st.markdown("---")
        st.markdown("### 💾 Opciones de Guardado")
        
        col_save, col_act, col_desc = st.columns(3)
        
        with col_save:
            if st.button("💾 Guardar en Archivo", 
                        type="primary",
                        use_container_width=True):
                try:
                    with st.spinner("Guardando planificación ministerial..."):
                        df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                        
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
                        st.info("Ahora ve a 'Mi Archivo Pedagógico' para activarla.")
                        time.sleep(3)
                        go_to_page('archivo')
                        
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
        
        with col_act:
            if st.button("⭐ Guardar y Activar", 
                        help="Guardar y activar inmediatamente",
                        use_container_width=True):
                try:
                    with st.spinner("Activando planificación ministerial..."):
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
                        
                        # Activar
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
                            go_to_page('archivo')
                        
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col_desc:
            if st.button("🗑️ Descartar", 
                        type="secondary",
                        use_container_width=True):
                del st.session_state.conversion_ministerial
                del st.session_state.planificacion_ministerial_original
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: EVALUAR ALUMNO ---
def render_evaluar():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    # HEADER DE PÁGINA
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">👨‍🎓 Evaluar Alumno</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    # VERIFICAR PLANIFICACIÓN ACTIVA
    plan_activa = obtener_plan_activa_usuario(st.session_state.u['NOMBRE'])
    
    if not plan_activa:
        st.error("""
        <div class="content-box warning">
            <h4>🚨 No tienes planificación activa</h4>
            <p>Para evaluar, necesitas activar una planificación primero.</p>
            <p>Ve a <strong>Mi Archivo Pedagógico</strong> para seleccionar y activar una planificación.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📁 Ir a Mi Archivo Pedagógico", use_container_width=True):
            go_to_page('archivo')
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # INFORMACIÓN DE PLANIFICACIÓN ACTIVA
    st.markdown(f"""
    <div class="content-box success">
        <h4>📌 Evaluando contra planificación activa</h4>
        <p><strong>Rango:</strong> {plan_activa['RANGO']}</p>
        <p><strong>Aula:</strong> {plan_activa['AULA']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # BUSCAR ACTIVIDAD DE HOY
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    if st.button("🔍 Buscar actividad programada para hoy", type="primary", use_container_width=True):
        try:
            with st.spinner("Analizando planificación..."):
                contenido_planificacion = plan_activa['CONTENIDO_PLAN']
                
                prompt_busqueda = f"""
                Eres un asistente pedagógico especializado en analizar planificaciones.
                
                **PLANIFICACIÓN OFICIAL DE LA SEMANA:**
                {contenido_planificacion[:8000]}
                
                **INSTRUCCIÓN:** Hoy es {fecha_hoy}. 
                
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
    
    # FORMULARIO DE EVALUACIÓN
    st.markdown("### 📝 Registro de Evaluación")
    
    with st.form("form_evaluacion"):
        actividad = st.text_input(
            "**Actividad Programada:**",
            value=st.session_state.get('actividad_detectada', ''),
            disabled=True
        )
        
        estudiante = st.text_input("**Nombre del Estudiante:**", placeholder="Ej: Juan Pérez")
        
        anecdota = st.text_area("**Observación del Desempeño:**", 
                               height=100, 
                               placeholder="Describe específicamente qué hizo el estudiante hoy...")
        
        col_submit, col_clear = st.columns([3, 1])
        with col_submit:
            submitted = st.form_submit_button("⚡ Generar Evaluación", type="primary", use_container_width=True)
        with col_clear:
            clear = st.form_submit_button("🧹 Limpiar", type="secondary", use_container_width=True)
        
        if clear:
            st.session_state.actividad_detectada = ""
            st.rerun()
        
        if submitted:
            if not estudiante or not anecdota:
                st.warning("⚠️ Completa todos los campos.")
            elif "NO HAY ACTIVIDAD" in actividad:
                st.error("❌ No puedes evaluar sin actividad programada.")
            else:
                with st.spinner("Generando evaluación..."):
                    prompt_eval = f"""
                    ACTÚA COMO EXPERTO EN EVALUACIÓN DE EDUCACIÓN ESPECIAL (VENEZUELA).
                    
                    DATOS DE EVALUACIÓN:
                    - Fecha: {fecha_hoy}
                    - Estudiante: {estudiante}
                    - Actividad Programada: {actividad}
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
                    st.session_state.actividad_evaluada = actividad
                    st.rerun()
    
    # MOSTRAR Y GUARDAR RESULTADO
    if 'eval_resultado' in st.session_state:
        st.markdown("---")
        st.markdown("### 📋 Evaluación Generada")
        st.markdown(f'<div class="content-box success">{st.session_state.eval_resultado}</div>', unsafe_allow_html=True)
        
        if st.button("💾 Guardar Evaluación en Registro", type="primary", use_container_width=True):
            try:
                df_evals = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                
                nueva_eval = pd.DataFrame([{
                    "FECHA": fecha_hoy,
                    "USUARIO": st.session_state.u['NOMBRE'],
                    "ESTUDIANTE": st.session_state.estudiante_evaluado,
                    "ACTIVIDAD": st.session_state.actividad_evaluada,
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
                del st.session_state.actividad_evaluada
                
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al guardar: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: REGISTRO DE EVALUACIONES ---
def render_registros():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    # HEADER DE PÁGINA
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">📊 Registro de Evaluaciones</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    try:
        df_e = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
        mis_evals = df_e[df_e['USUARIO'] == st.session_state.u['NOMBRE']]
        
        if mis_evals.empty:
            st.info("""
            <div class="content-box info">
                <h4>📭 No hay evaluaciones registradas</h4>
                <p>Aún no has registrado evaluaciones. Ve a <strong>Evaluar Alumno</strong> para empezar.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("👨‍🎓 Ir a Evaluar Alumno", use_container_width=True):
                go_to_page('evaluar')
            
        else:
            # SELECTOR DE ALUMNO
            lista_alumnos = sorted(mis_evals['ESTUDIANTE'].unique().tolist())
            alumno_sel = st.selectbox("**Seleccionar estudiante:**", lista_alumnos, key="selector_alumno")
            
            datos_alumno = mis_evals[mis_evals['ESTUDIANTE'] == alumno_sel]
            
            # ESTADÍSTICAS
            total_evaluaciones = len(datos_alumno)
            primera_fecha = datos_alumno['FECHA'].min()
            ultima_fecha = datos_alumno['FECHA'].max()
            
            st.markdown(f"""
            <div class="content-box">
                <h4>📈 Estadísticas de {alumno_sel}</h4>
                <p><strong>Total de evaluaciones:</strong> {total_evaluaciones}</p>
                <p><strong>Primera evaluación:</strong> {primera_fecha}</p>
                <p><strong>Última evaluación:</strong> {ultima_fecha}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # HISTORIAL
            st.markdown("### 📋 Historial de Evaluaciones")
            
            for idx, row in datos_alumno.iloc[::-1].iterrows():
                with st.expander(f"📅 {row['FECHA']} | {row['ACTIVIDAD']}", expanded=False):
                    st.markdown("**📝 Observación del docente:**")
                    st.info(f"_{row['ANECDOTA']}_")
                    
                    st.markdown("**🤖 Análisis técnico:**")
                    st.markdown(f'<div class="content-box success">{row["EVALUACION_IA"]}</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: MI ARCHIVO PEDAGÓGICO ---
def render_archivo():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    # HEADER DE PÁGINA
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">📁 Mi Archivo Pedagógico</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    # PLANIFICACIÓN ACTIVA ACTUAL
    plan_activa_actual = obtener_plan_activa_usuario(st.session_state.u['NOMBRE'])
    
    if plan_activa_actual:
        st.markdown(f"""
        <div class="content-box success">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>🟢 Planificación Activa Actual</h4>
                    <p><strong>Rango:</strong> {plan_activa_actual['RANGO']}</p>
                    <p><strong>Aula:</strong> {plan_activa_actual['AULA']}</p>
                </div>
                <button class="btn btn-danger" onclick="window.location.href='?desactivar=true'">❌ Desactivar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón para desactivar (manejado por parámetro de URL)
        if st.query_params.get("desactivar", False):
            if desactivar_plan_activa(st.session_state.u['NOMBRE']):
                st.success("✅ Planificación desactivada.")
                time.sleep(1)
                st.query_params.clear()
                st.rerun()
    else:
        st.warning("""
        <div class="content-box warning">
            <h4>⚠️ No hay planificación activa</h4>
            <p>Activa una planificación para que el sistema de evaluación funcione correctamente.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # LISTA DE PLANIFICACIONES GUARDADAS
    st.markdown("### 📚 Planificaciones Guardadas")
    
    try:
        df = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
        mis_planes = df[df['USUARIO'] == st.session_state.u['NOMBRE']]
        
        if mis_planes.empty:
            st.info("""
            <div class="content-box info">
                <p>No tienes planificaciones guardadas aún.</p>
                <p>Ve a <strong>Planificador Inteligente</strong> o <strong>Planificaciones Ministeriales</strong> para crear una.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📝 Ir al Planificador", use_container_width=True):
                    go_to_page('planificador')
            with col2:
                if st.button("📋 Ir a Ministeriales", use_container_width=True):
                    go_to_page('ministerial')
            
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
                
                tema_corto = str(row['TEMA'])[:50] + "..." if len(str(row['TEMA'])) > 50 else str(row['TEMA'])
                
                # TARJETA DE PLANIFICACIÓN
                with st.container():
                    if es_activa:
                        st.markdown(f'<div class="content-box success">', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="content-box">', unsafe_allow_html=True)
                    
                    col_info, col_acc = st.columns([3, 1])
                    
                    with col_info:
                        if es_activa:
                            st.markdown(f"### 🟢 {tema_corto}")
                            st.markdown(f"**ACTIVA** | {rango_display}")
                        else:
                            st.markdown(f"### {tema_corto}")
                            st.markdown(f"{rango_display}")
                        
                        if 'ORIGEN' in row and pd.notna(row['ORIGEN']):
                            st.markdown(f"*Origen: {row['ORIGEN']}*")
                    
                    with col_acc:
                        if not es_activa:
                            if st.button("⭐ Activar", key=f"activar_{index}", use_container_width=True):
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
                                    st.success("✅ ¡Planificación activada!")
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.markdown("**🟢 ACTIVA**")
                    
                    # CONTENIDO EXPANDIBLE
                    with st.expander("Ver detalles"):
                        descripcion = extraer_descripcion_dias(row['CONTENIDO'])
                        st.markdown(f"**📝 Descripción:** {descripcion}")
                        
                        st.markdown("**Contenido completo:**")
                        st.markdown(f'<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 0.9em;">{row["CONTENIDO"]}</div>', unsafe_allow_html=True)
                        
                        # BOTONES DE ACCIÓN
                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            if st.button("🗑️ Eliminar", key=f"eliminar_{index}", type="secondary", use_container_width=True):
                                if st.checkbox(f"¿Confirmar eliminación de esta planificación?", key=f"confirm_{index}"):
                                    if es_activa:
                                        desactivar_plan_activa(st.session_state.u['NOMBRE'])
                                    
                                    df_actualizado = df.drop(index)
                                    conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_actualizado)
                                    
                                    st.success("Planificación eliminada.")
                                    time.sleep(1)
                                    st.rerun()
                        
                        with col_act2:
                            if st.button("📋 Ver completo", key=f"ver_{index}", use_container_width=True):
                                st.markdown(f'<div class="content-box">{row["CONTENIDO"]}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: IDEAS DE ACTIVIDADES ---
def render_ideas():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">💡 Ideas de Actividades</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    tema = st.text_input("**¿Sobre qué tema necesitas ideas?**", 
                        placeholder="Ej: Herramientas de limpieza, Clasificación de materiales, Uso de productos...",
                        key="tema_ideas")
    
    if st.button("✨ Generar Ideas", type="primary", use_container_width=True):
        if tema:
            with st.spinner("Creando ideas innovadoras..."):
                res = generar_respuesta([
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS}, 
                    {"role": "user", "content": f"Genera 3 actividades DUA innovadoras para el tema '{tema}' en Taller Laboral. Para cada actividad incluye: 1) Título creativo, 2) Materiales necesarios, 3) Instrucciones paso a paso claras, 4) Adaptaciones posibles para diferentes necesidades."}
                ], temperatura=0.7)
                st.markdown(f'<div class="content-box">{res}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Escribe un tema primero.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: CONSULTAS TÉCNICAS ---
def render_consultas():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">❓ Consultas Técnicas</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    duda = st.text_area("**Escribe tu consulta técnica o legal:**", 
                       placeholder="Ej: ¿Qué artículo de la LOE respalda la evaluación cualitativa en Educación Especial?\nEj: ¿Cómo adaptar una actividad para un estudiante con movilidad reducida?\nEj: ¿Qué recursos puedo usar para enseñar clasificación de materiales?",
                       height=150,
                       key="duda_consultas")
    
    if st.button("🔍 Buscar Respuesta", type="primary", use_container_width=True):
        if duda:
            with st.spinner("Buscando información técnica..."):
                res = generar_respuesta([
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS}, 
                    {"role": "user", "content": f"Responde técnicamente y cita la ley o currículo cuando sea relevante. Consulta: {duda}"}
                ], temperatura=0.5)
                st.markdown(f'<div class="content-box">{res}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Escribe tu consulta primero.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA: MENSAJES MOTIVACIONALES ---
def render_motivacion():
    render_header()
    
    st.markdown('<div class="page-container">', unsafe_allow_html=True)
    
    col_title, col_back = st.columns([4, 1])
    with col_title:
        st.markdown('<div class="page-title">🌟 Mensajes Motivacionales</div>', unsafe_allow_html=True)
    with col_back:
        if st.button("🏠 Volver al Menú", use_container_width=True):
            go_home()
    
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("💪 Dosis de Fuerza", use_container_width=True, type="primary"):
            with st.spinner("Preparando tu dosis..."):
                res = generar_respuesta([
                    {"role": "system", "content": "ERES LEGADO MAESTRO. Eres un colega docente venezolano realista pero esperanzador. Dame un mensaje corto y poderoso para un docente que está cansado pero sigue adelante. NO SALUDES."},
                    {"role": "user", "content": "Dame el mensaje."}
                ], temperatura=0.8)
                st.markdown(f'<div class="content-box">{res}</div>', unsafe_allow_html=True)
    
    with col_btn2:
        if st.button("🙏 Reflexión Espiritual", use_container_width=True, type="secondary"):
            with st.spinner("Buscando sabiduría..."):
                res = generar_respuesta([
                    {"role": "system", "content": "ERES LEGADO MAESTRO. Eres un sabio espiritual que combina citas bíblicas con reflexiones docentes. Dame un mensaje esperanzador basado en fe y vocación docente. NO SALUDES."},
                    {"role": "user", "content": "Dame el mensaje."}
                ], temperatura=0.8)
                st.markdown(f'<div class="content-box">{res}</div>', unsafe_allow_html=True)
    
    with col_btn3:
        if st.button("😊 Sonrisa Docente", use_container_width=True, type="secondary"):
            with st.spinner("Creando alegría..."):
                res = generar_respuesta([
                    {"role": "system", "content": "ERES LEGADO MAESTRO. Eres un motivador directo con humor venezolano. Dame un mensaje alegre y energizante para recordar por qué somos docentes. NO SALUDES."},
                    {"role": "user", "content": "Dame el mensaje."}
                ], temperatura=0.8)
                st.markdown(f'<div class="content-box">{res}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- RUTEO PRINCIPAL ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'

# Navegación basada en estado
if st.session_state.current_page == 'home':
    render_home()
elif st.session_state.current_page == 'planificador':
    render_planificador()
elif st.session_state.current_page == 'ministerial':
    render_ministerial()
elif st.session_state.current_page == 'evaluar':
    render_evaluar()
elif st.session_state.current_page == 'registros':
    render_registros()
elif st.session_state.current_page == 'archivo':
    render_archivo()
elif st.session_state.current_page == 'ideas':
    render_ideas()
elif st.session_state.current_page == 'consultas':
    render_consultas()
elif st.session_state.current_page == 'motivacion':
    render_motivacion()

# --- FOOTER GLOBAL ---
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 0.9rem;">
    <p>🍎 Legado Maestro | Versión 5.0 - Interfaz Profesional Rediseñada</p>
    <p>Desarrollado por Luis Atencio | Bachiller Docente | T.E.L E.R.A.C - Venezuela</p>
    <p style="margin-top: 10px;">
        <button onclick="window.location.href='?logout=true'" style="background: none; border: 1px solid #ddd; padding: 5px 15px; border-radius: 5px; cursor: pointer; color: #666;">
            🔒 Cerrar Sesión
        </button>
    </p>
</div>
""", unsafe_allow_html=True)

# Manejo de logout
if st.query_params.get("logout", False):
    st.session_state.auth = False
    st.session_state.u = None
    st.query_params.clear()
    st.rerun()
