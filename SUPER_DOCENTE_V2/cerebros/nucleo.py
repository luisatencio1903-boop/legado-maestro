# =============================================================================
# CEREBRO NÚCLEO - SUPER DOCENTE 2.0 (INTEGRIDAD RESTAURADA)
# Función: Dispatcher de Inteligencia y Selector de Contexto Dinámico
# =============================================================================

import streamlit as st
from groq import Groq
# Importación de los especialistas
from cerebros import tel, caipa, ieeb, aula_integrada, upe, inicial

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
    """ADN de Identidad y Filtros de Ética de SUPER DOCENTE 2.0"""
    return """
    IDENTIDAD: ERES "SUPER DOCENTE 2.0". 
    Creado por el Bachiller Luis Atencio, zuliano y lossadeño. Herramienta 100% venezolana.
    FILTRO ÉTICO: Educación laica y apolítica. PROHIBIDO emitir opiniones sobre política o religión.
    FORMATO: Usa negritas para títulos y doble espacio entre secciones.
    """

def generar_respuesta(input_data, temperatura=0.6):
    """Soporta tanto el Chat (Aula Virtual) como la Planificación."""
    if not client: return "Error: Cliente IA no configurado."
    if isinstance(input_data, list):
        mensajes = input_data
    else:
        mensajes = [{"role": "system", "content": input_data}]
    try:
        completion = client.chat.completions.create(messages=mensajes, model=MODELO, temperature=temperatura)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de conexión con el cerebro IA: {e}"

# --- ESTA ES LA FUNCIÓN QUE BUSCA TU PLANIFICADOR.PY Y CAUSABA EL ERROR ---
def seleccionar_cerebro_modalidad(modalidad):
    """Busca el prompt específico del especialista."""
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

def procesar_planificacion_v2(modalidad, dia_nombre, config_db, tema_usuario):
    """Motor v2.0 para la nueva lógica de switches."""
    adn_especialista = seleccionar_cerebro_modalidad(modalidad)
    contexto_inyectado = ""
    
    if "Taller" in modalidad or "T.E.L." in modalidad:
        if config_db.get('pa_switch') and dia_nombre in config_db.get('pa_dias', []):
            contexto_inyectado = f"CONTEXTO PROYECTO DE AULA: {config_db['pa_texto']}"
        elif config_db.get('psp_switch') and dia_nombre in config_db.get('psp_dias', []):
            contexto_inyectado = f"CONTEXTO PROYECTO SOCIO-PRODUCTIVO: {config_db['psp_texto']}"
        elif config_db.get('pensum_switch'):
            contexto_inyectado = f"CONTEXTO PENSUM TÉCNICO: {config_db['pensum_contenido']}"
    else:
        if config_db.get('pa_switch') and dia_nombre in config_db.get('pa_dias', []):
            contexto_inyectado = f"CONTEXTO PROYECTO DE AULA: {config_db['pa_texto']}"
    
    prompt_final = f"{obtener_instrucciones_globales()}\n{adn_especialista}\nCONTEXTO: {contexto_inyectado}\nTEMA: {tema_usuario}"
    return generar_respuesta(prompt_final)
