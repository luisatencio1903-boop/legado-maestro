import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. MODO "APP NATIVA" (Ocultar marcas) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .viewerBadge_container__1QSob {display: none !important;}
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

# --- OPCIÓN 2: MENSAJE MOTIVACIONAL (CORREGIDO DE COLOR 🎨) ---
elif opcion == "🌟 Mensaje Motivacional":
    st.subheader("Ánimo, Colega Venezolano 🇻🇪")
    st.info("Un espacio para recargar energías.")
    
    if st.button("❤️ Generar Mensaje de Hoy"):
        with st.spinner('Redactando mensaje de aliento...'):
            try:
                prompt = """
                Genera un mensaje motivacional corto, emotivo y muy humano dirigido a un docente de educación especial en Venezuela.
                Reconoce la dura situación país pero resalta la grandeza de su labor.
                Tono de compañero a compañero.
                CIERRE OBLIGATORIO: "Ánimos. Att: Profesor Luis Atencio"
                """
                res = model.generate_content(prompt)
                
                # AQUÍ ESTÁ LA CORRECCIÓN: color: #000000 (Negro puro)
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
                    <h4 style="color: #000000;">🌟 Para ti, compañero de lucha:</h4>
                    <p style="font-size: 1.1em; color: #000000; font-weight: 500;">{res.text}</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error("Error al conectar con la inspiración.")

# --- OPCIÓN 3: IDEAS ---
elif opcion == "💡 Ideas de Actividades":
    tema = st.text_input("Tema a trabajar:")
    if st.button("✨ Sugerir"):
        res = model.generate_content(f"Sugiere 3 actividades técnicas breves para {tema} en Taller Laboral.")
        st.markdown(res.text)

# --- OPCIÓN 4: CONSULTAS ---
elif opcion == "❓ Consultas Técnicas":
    duda = st.text_area("Consulta:")
    if st.button("🔍 Responder"):
        res = model.generate_content(f"Respuesta técnica breve: {duda}")
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
