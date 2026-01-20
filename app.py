import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. WAKE-UP LOGIC (EVITA EL ERROR 500 AL INICIAR) ---
if "started" not in st.session_state:
    with st.spinner("Conectando con el Taller Laboral..."):
        time.sleep(3) # Aumentamos a 3 segundos para asegurar estabilidad
    st.session_state.started = True

# --- 3. CONEXIÓN CON LA IA (GOOGLE FLASH 2.5) ---
try:
    # Usamos st.secrets para máxima seguridad en la nube
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"⚠️ Error de servidor: {e}")
    st.info("Verifique que 'GOOGLE_API_KEY' esté bien configurada en los Secrets de Streamlit.")
    st.stop()

# --- 4. IDENTIDAD INSTITUCIONAL ---
with st.sidebar:
    st.image("logo_legado.png", width=150)
    st.title("Legado Maestro")
    st.caption("👨‍🏫 **Luis Atencio** | Bachiller Docente")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")

# --- 5. FUNCIONES DE LA APP ---
st.title("🍎 Asistente Educativo - Zulia")

# Menú simplificado para móvil
opcion = st.selectbox(
    "Seleccione una herramienta:",
    ["📝 Planificador Semanal", "💡 Ideas de Actividades", "❓ Consultas Técnicas"]
)

if opcion == "📝 Planificador Semanal":
    st.subheader("Planificación Técnica Profesional")
    rango = st.text_input("Lapso de la semana:", placeholder="Ej: 19 al 23 de enero 2026")
    aula = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")
    notas = st.text_area("Notas del cronograma:", height=200)

    if st.button("🚀 Generar"):
        if rango and notas:
            with st.spinner('Procesando datos...'):
                try:
                    prompt = f"Actúa como Luis Atencio, Bachiller Docente. Organiza estas notas en una planificación técnica para Educación Especial. Lapso: {rango} | Aula: {aula} | Notas: {notas}. Formato: Día, Título, Competencia, Exploración, Desarrollo, REFLEXIÓN, Mantenimiento. Tono profesional y laico. Firma: Luis Atencio, Bachiller Docente."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Error técnico: {e}")

elif opcion == "💡 Ideas de Actividades":
    tema = st.text_input("Habilidad a trabajar:")
    if st.button("✨ Sugerir"):
        res = model.generate_content(f"Como Bachiller Docente, sugiere 3 actividades técnicas breves para {tema}. Tono profesional.")
        st.markdown(res.text)

elif opcion == "❓ Consultas Técnicas":
    pregunta = st.text_area("Duda pedagógica:")
    if st.button("🔍 Responder"):
        res = model.generate_content(f"Respuesta técnica sobre educación especial: {pregunta}")
        st.markdown(res.text)

# --- 6. FIRMA PROFESIONAL ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'><small>Desarrollado por <b>Luis Atencio</b><br>Zulia, Venezuela | 2026</small></div>", 
    unsafe_allow_html=True
)
