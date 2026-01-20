import streamlit as st
import google.generativeai as genai
import time
import random
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. ESTILOS CSS ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QSob {display: none !important;}
            
            /* FUERZA EL TEXTO A NEGRO */
            .mensaje-texto {
                color: #000000 !important;
                font-family: 'Helvetica', sans-serif;
                font-size: 1.2em; 
                font-weight: 500;
                line-height: 1.4;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. ARRANQUE SEGURO ---
if "ready" not in st.session_state:
    st.session_state.ready = True

# --- 4. CONEXIÓN CON IA (MODELO RÁPIDO 1.5) ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())
        
        # Usamos el modelo rápido (1.5 Flash)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
    else:
        st.error("⚠️ Falta API Key en los Secrets.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ ERROR DE CONEXIÓN INICIAL: {e}")
    st.stop()

# --- 5. BARRA LATERAL ---
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

# --- 6. CUERPO DE LA APP ---
st.title("🍎 Asistente Educativo - Zulia")

opcion = st.selectbox(
    "Seleccione herramienta:",
    [
        "📝 Planificación Profesional", 
        "🌟 Mensaje Motivacional", 
        "💡 Ideas de Actividades", 
        "❓ Consultas Técnicas"
    ]
)

# --- OPCIÓN 1: PLANIFICADOR ---
if opcion == "📝 Planificación Profesional":
    st.subheader("Planificación Técnica")
    rango = st.text_input("Lapso:", placeholder="Ej: 19 al 23 de enero 2026")
    aula = st.text_input("Aula:", value="Mantenimiento y Servicios Generales")
    notas = st.text_area("Notas diarias:", height=200)

    if st.button("🚀 Generar Planificación"):
        if rango and notas:
            with st.spinner('Redactando documento...'):
                try:
                    prompt = f"""
                    Actúa como Luis Atencio, Bachiller Docente. 
                    Estructura estas notas en una planificación técnica para Educación Especial.
                    Lapso: {rango} | Aula: {aula} | Notas: {notas}
                    ESTRUCTURA: Día, Título, Competencia, Exploración, Desarrollo, REFLEXIÓN, Mantenimiento.
                    FIRMA OBLIGATORIA: Luis Atencio, Bachiller Docente.
                    """
                    res = model.generate_content(prompt)
                    st.success("¡Planificación Generada!")
                    st.markdown(res.text)
                except Exception as e:
                    # AQUÍ MUESTRA EL ERROR REAL
                    st.error(f"⚠️ ERROR TÉCNICO (Mándame foto de esto): {e}")

# --- OPCIÓN 2: MENSAJE MOTIVACIONAL ---
elif opcion == "🌟 Mensaje Motivacional":
    st.subheader("Dosis de Ánimo Express ⚡")
    
    if st.button("❤️ Mensaje Corto para Compartir"):
        with st.spinner('Conectando...'):
            try:
                temas = [
                    "Una frase bíblica corta sobre enseñar y servir.",
                    "Una frase célebre corta de motivación educativa.",
                    "Una frase de aliento guerrero para el docente venezolano.",
                    "Recordatorio breve de la vocación docente."
                ]
                
                tema_elegido = random.choice(temas)
                config_creativa = genai.types.GenerationConfig(temperature=0.9)

                prompt_final = f"""
                {tema_elegido}
                REGLAS: MÁXIMO 25 PALABRAS.
                CIERRE OBLIGATORIO: "Ánimos. Att: Profesor Luis Atencio"
                """
                
                res = model.generate_content(prompt_final, generation_config=config_creativa)
                
                st.
