import streamlit as st
import google.generativeai as genai
import time
import random

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. ESTILOS CSS (Texto Negro y Diseño Limpio) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QSob {display: none !important;}
            
            /* FUERZA EL TEXTO A NEGRO Y TAMAÑO LEGIBLE */
            .mensaje-texto {
                color: #000000 !important;
                font-family: 'Helvetica', sans-serif;
                font-size: 1.2em; /* Un poco más grande para impacto */
                font-weight: 500;
                line-height: 1.4;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. URL DEL LOGO ---
LOGO_URL = "https://raw.githubusercontent.com/luisatencio1903-boop/legado-maestro/main/logo_legado.png"

# --- 4. ARRANQUE SEGURO ---
if "ready" not in st.session_state:
    st.session_state.ready = True

# --- 5. CONEXIÓN CON IA ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("⚠️ Falta API Key.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.stop()

# --- 6. BARRA LATERAL ---
with st.sidebar:
    st.image(LOGO_URL, width=150)
    st.title("Legado Maestro")
    st.markdown("---")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    st.caption("T.E.L E.R.A.C")

# --- 7. CUERPO DE LA APP ---
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
            with st.spinner('Procesando datos...'):
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
                    st.error(f"Error: {e}")

# --- OPCIÓN 2: MENSAJE MOTIVACIONAL (VERSIÓN CORTA Y DIRECTA ⚡) ---
elif opcion == "🌟 Mensaje Motivacional":
    st.subheader("Dosis de Ánimo Express ⚡")
    
    if st.button("❤️ Mensaje Corto para Compartir"):
        with st.spinner('Buscando frase perfecta...'):
            try:
                # TEMAS VARIADOS PERO ESTRICTAMENTE CORTOS
                temas = [
                    # Opción 1: Bíblico Flash
                    """Dame solo UNA frase bíblica poderosa sobre la enseñanza o el amor, y una mini aplicación de 5 palabras.
                    Ejemplo: 'Instruye al niño en su camino. Tu huella es eterna.' 
                    Nada más.""",
                    
                    # Opción 2: Frase de Impacto
                    """Una frase célebre corta sobre educación (tipo Hellen Keller o Mandela) y un 'Tú puedes' final.
                    Máximo 20 palabras en total.""",
                    
                    # Opción 3: Realidad Venezuela (Corto)
                    """Una frase de aliento guerrero para el docente venezolano. 
                    Ejemplo: 'En tiempos difíciles, tu aula es un refugio de luz. Gracias por resistir.'
                    Corto y contundente.""",
                    
                    # Opción 4: Vocación Pura
                    """Un recordatorio flash de por qué educamos.
                    Ejemplo: 'Ese pequeño avance de hoy valió todo el esfuerzo. Estás cambiando vidas.'"""
                ]
                
                # ELEGIR TEMA AL AZAR
                tema_elegido = random.choice(temas)
                
                # CONFIGURACIÓN DE CREATIVIDAD MEDIA (Para que sea coherente pero variado)
                config_creativa = genai.types.GenerationConfig(temperature=0.9)

                prompt_final = f"""
                {tema_elegido}
                
                REGLAS OBLIGATORIAS DE LONGITUD:
                1. MÁXIMO 2 ORACIONES.
                2. MÁXIMO 25 PALABRAS.
                3. Tiene que ser fácil de leer en un segundo.
                4. CIERRE OBLIGATORIO: "Ánimos. Att: Profesor Luis Atencio"
                """
                
                # Generamos
                res = model.generate_content(prompt_final, generation_config=config_creativa)
                
                # MUESTRA EL MENSAJE
                st.markdown(f"""
                <div style="background-color: #ffffff; padding: 20px; border-radius: 15px; border: 2px solid #eee; border-left: 8px solid #ff4b4b; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                    <div class="mensaje-texto">
                        {res.text}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error("Error al conectar con la inspiración.")

# --- OPCIÓN 3: IDEAS ---
elif opcion == "💡 Ideas de Actividades":
    tema = st.text_input("Tema a trabajar:")
    if st.button("✨ Sugerir"):
        res = model.generate_content(f"Sugiere 3 actividades técnicas, creativas y breves para {tema} en Taller Laboral.")
        st.markdown(res.text)

# --- OPCIÓN 4: CONSULTAS ---
elif opcion == "❓ Consultas Técnicas":
    duda = st.text_area("Consulta:")
    if st.button("🔍 Responder"):
        res = model.generate_content(f"Respuesta técnica profesional y breve: {duda}")
        st.markdown(res.text)

# --- 8. PIE DE PÁGINA ---
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center;'>
        <img src='{LOGO_URL}' width='50'><br>
        <p style='margin-bottom: 5px;'>Desarrollado con ❤️ por <b>Luis Atencio</b></p>
        <p style='font-size: 0.85em; color: #555;'>para sus amigos y participantes del <b>T.E.L E.R.A.C</b></p>
        <p style='font-size: 0.75em; color: silver;'>Zulia, Venezuela | 2026</p>
    </div>
    """, 
    unsafe_allow_html=True
)
