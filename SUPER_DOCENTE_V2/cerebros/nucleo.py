# =============================================================================
# CEREBRO NÚCLEO - SUPER DOCENTE 2.0 (REPARACIÓN DE RUTAS Y ESCUDO OFFLINE)
# =============================================================================

import streamlit as st

# --- ESCUDO DE IMPORTACIÓN v2.0 (EVITA EL BUCLE "PLEASE WAIT" EN MODO OFFLINE) ---
try:
    from groq import Groq
except ImportError:
    # Si la librería Groq no está disponible (Stlite Offline), creamos un sustituto
    class Groq:
        def __init__(self, api_key): pass
    client = None

# IMPORTACIÓN RELATIVA: El punto (.) significa "busca en esta misma carpeta"
# Esto evita el error de "ImportError" en sistemas modulares
try:
    from . import tel, caipa, ieeb, aula_integrada, upe, inicial
except ImportError:
    import tel, caipa, ieeb, aula_integrada, upe, inicial

# --- CLIENTE IA (GROQ) ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        MODELO = "llama-3.3-70b-versatile"
    else:
        client = None
except:
    client = None

def obtener_instrucciones_globales():
    return """
    IDENTIDAD: ERES "SUPER DOCENTE 2.0". 
    Creado por el Bachiller Luis Atencio, zuliano y lossadeño. Herramienta 100% venezolana.
    FILTRO ÉTICO: Educación laica y apolítica. PROHIBIDO emitir opiniones sobre política o religión.
    FORMATO: Usa negritas para títulos y doble espacio entre secciones.
    """

# --- FUNCIÓN 1: EXPORTADA PARA AULA_VIRTUAL.PY ---
def generar_respuesta(input_data, temperatura=0.6):
    """
    Soporta tanto el Chat como la Planificación. 
    En modo Offline, informa que la IA requiere conexión.
    """
    if not client: 
        return "⚠️ Modo Autónomo: La Inteligencia Artificial requiere conexión a internet para generar respuestas. Sus datos administrativos (Asistencia/Evaluación) siguen protegidos localmente."
    
    mensajes = input_data if isinstance(input_data, list) else [{"role": "system", "content": input_data}]
    try:
        completion = client.chat.completions.create(messages=mensajes, model=MODELO, temperature=temperatura)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de conexión con el cerebro IA: {e}"

# --- FUNCIÓN 2: EXPORTADA PARA PLANIFICADOR.PY ---
def seleccionar_cerebro_modalidad(modalidad):
    if "Taller" in modalidad or "T.E.L." in modalidad:
        return tel.obtener_prompt()
    elif "Instituto" in modalidad or "I.E.E.B." in modalidad:
        return ieeb.obtener_prompt()
    elif "Autismo" in modalidad or "C.A.I.P.A." in modalidad:
        return caipa.obtener_prompt()
    elif "Aula Integrada" in modalidad:
        return aula_integrada.obtener_prompt()
    elif "Unidad" in modalidad or "U.P.E." in modalidad:
        return upe.obtener_prompt()
    elif "Inicial" in modalidad:
        return inicial.obtener_prompt()
    return "ROL: DOCENTE DE EDUCACIÓN ESPECIAL."

# --- FUNCIÓN 3: EL MOTOR DE LA V2.0 ---
def procesar_planificacion_v2(modalidad, dia_nombre, config_db, tema_usuario):
    adn_especialista = seleccionar_cerebro_modalidad(modalidad)
    
    # Seleccionar las Reglas de Oro correctas para inyectar al final
    if "Taller" in modalidad: reglas = tel.REGLAS_DE_ORO
    elif "Instituto" in modalidad: reglas = ieeb.REGLAS_DE_ORO
    elif "Autismo" in modalidad: reglas = caipa.REGLAS_DE_ORO
    else: reglas = "Respeta el Currículo Nacional Bolivariano."

    prompt_final = f"{obtener_instrucciones_globales()}\n{adn_especialista}\nREGLAS DE ORO: {reglas}\nTEMA: {tema_usuario}"
    return generar_respuesta(prompt_final)
