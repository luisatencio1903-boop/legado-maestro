import streamlit as st
import google.generativeai as genai
import time

# --- 1. CONFIGURACIÓN DE PÁGINA (LOGO E IDENTIDAD) ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. LÓGICA ANTI-ERROR 500 (WAKE-UP) ---
if "app_ready" not in st.session_state:
    with st.spinner("Conectando con el Taller Laboral 'Elena Rosa Aranguibel'..."):
        time.sleep(3) # Tiempo de espera para estabilizar la conexión del APK
    st.session_state.app_ready = True

# --- 3. CONFIGURACIÓN DE SEGURIDAD (API KEY) ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("⚠️ Error: Configure 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.stop()

# --- 4. BARRA LATERAL: IDENTIDAD PROFESIONAL ---
with st.sidebar:
    try:
        st.image("logo_legado.png", width=150)
    except:
        st.warning("⚠️ Cargando escudo institucional...")
            
    st.title("Legado Maestro")
    st.markdown("---")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")
    st.info("💡 Herramienta de apoyo pedagógico para Educación Especial en el Zulia.")

# --- 5. CUERPO DE LA APP ---
st.title("🍎 Asistente Educativo - Zulia")

opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    ["📝 Planificador Semanal Profesional", "💡 Ideas para Actividades", "❓ Consultas Técnicas"]
)

if opcion == "📝 Planificador Semanal Profesional":
    st.subheader("Planificación Técnica Estructurada")
    rango = st.text_input("Lapso de la semana:", placeholder="Ej: del 19 al 23 de enero de 2026")
    aula = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")
    st.info("Escriba sus notas diarias. El profesor Luis Atencio les dará el formato técnico oficial.")
    notas = st.text_area("Cronograma de actividades:", height=200)

    if st.button("🚀 Generar Planificación"):
        if rango and notas:
            with st.spinner('Procesando datos bajo estándares pedagógicos...'):
                try:
                    prompt = f"""
                    Actúa como Luis Atencio, Bachiller Docente del Taller Laboral 'Elena Rosa Aranguibel'.
                    Organiza estas notas en una planificación formal, técnica y concisa para Educación Especial.
                    
                    DATOS: LAPSO: {rango} | AULA: {aula} | DOCENTE: Luis Atencio.
                    NOTAS: {notas}

                    ESTRUCTURA OBLIGATORIA POR DÍA:
                    1. Día y Fecha.
                    2. Título (Técnico y breve).
                    3. Competencia (Redacción profesional).
                    4. Exploración (Concisa, sin religión ni coloquialismos).
                    5. Desarrollo (Pasos prácticos en viñetas).
                    6. REFLEXIÓN (Evaluación y rutina de aseo resumida).
                    7. Mantenimiento (Orden y limpieza).

                    REGLA DE ORO: Tono profesional y laico. 
                    AL FINAL DE CADA DÍA DEBE APARECER: Luis Atencio, Bachiller Docente.
                    """
                    res = model.generate_content(prompt)
                    st.success("¡Planificación generada con éxito!")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Error técnico de la IA: {e}")

# --- OTRAS FUNCIONES ---
elif opcion == "💡 Ideas para Actividades":
    tema = st.text_input("Habilidad a fortalecer:")
    if st.button("✨ Sugerir"):
        res = model.generate_content(f"Sugiere 3 actividades técnicas breves para {tema}. Tono profesional.")
        st.markdown(res.text)

elif opcion == "❓ Consultas Técnicas":
    duda = st.text_area("Duda pedagógica:")
    if st.button("🔍 Responder"):
        res = model.generate_content(f"Respuesta técnica sobre educación especial para taller laboral: {duda}")
        st.markdown(res.text)

# --- 6. FIRMA Y MARCA PROFESIONAL AL PIE (FOOTER) ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p style='margin-bottom: 0;'>Desarrollado con ❤️ por <b>Luis Atencio</b></p>
        <p style='font-size: 0.85em; color: gray;'>Bachiller Docente - Zulia, 2026</p>
    </div>
    """, 
    unsafe_allow_html=True
)
