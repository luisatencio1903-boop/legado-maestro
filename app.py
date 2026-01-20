import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE PÁGINA (Para el logo al instalar) ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. CONFIGURACIÓN DE SEGURIDAD ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"].strip()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("⚠️ Error: Configure 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.stop()

# --- 3. INTERFAZ LATERAL (Identidad) ---
with st.sidebar:
    st.image("logo_legado.png", width=150)
    st.title("Legado Maestro")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")

# --- 4. CUERPO PRINCIPAL ---
st.image("logo_legado.png", width=100)
st.title("Asistente Educativo - Zulia")

# RESTAURACIÓN DEL MENÚ DE OPCIONES
opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    [
        "📝 Planificador Semanal Profesional", 
        "💡 Ideas para Actividades Laborales", 
        "❓ Consultas Pedagógicas (Educación Especial)"
    ]
)

# --- OPCIÓN 1: PLANIFICADOR ESTRUCTURADO ---
if opcion == "📝 Planificador Semanal Profesional":
    st.subheader("Planificación Técnica por Actividades")
    rango_fecha = st.text_input("Lapso de la semana:", placeholder="Ej: del 19 al 23 de enero de 2026")
    grado = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")
    
    st.info("Escribe el día y tus actividades. El profesor Luis se encargará de darle el formato profesional a cada una.")
    notas_docente = st.text_area("Ingresa tus notas aquí:", height=200)

    if st.button("🚀 Generar Planificación"):
        if rango_fecha and notas_docente:
            with st.spinner('Estructurando planificación técnica...'):
                try:
                    prompt = f"""
                    Actúa como Luis Atencio, Bachiller Docente del Taller Laboral 'Elena Rosa Aranguibel'.
                    Organiza estas notas en una planificación técnica y concisa para Educación Especial.

                    LAPSO: {rango_fecha} | AULA: {grado}
                    NOTAS: {notas_docente}

                    ESTRUCTURA POR DÍA:
                    1. Día y Fecha.
                    2. Título (Profesional).
                    3. Competencia (Técnica).
                    4. Exploración (Breve, sin coloquialismos ni religión).
                    5. Desarrollo (Viñetas técnicas paso a paso).
                    6. REFLEXIÓN (Evaluación y rutina de aseo resumida).
                    7. Mantenimiento (Orden y limpieza).

                    REGLAS: Tono formal, laico y profesional. Firma: Luis Atencio, Bachiller Docente.
                    """
                    respuesta = model.generate_content(prompt)
                    st.markdown(respuesta.text)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- OPCIÓN 2: IDEAS PARA ACTIVIDADES ---
elif opcion == "💡 Ideas para Actividades Laborales":
    st.subheader("Generador de Ideas Prácticas")
    habilidad = st.text_input("¿Qué habilidad quieres fortalecer? (Ej: Motricidad fina, uso de lija)")
    
    if st.button("✨ Sugerir Actividades"):
        with st.spinner('Buscando estrategias pedagógicas...'):
            prompt = f"Como Bachiller Docente en el Zulia, sugiere 3 actividades técnicas y breves para trabajar {habilidad} en un taller laboral de educación especial. Tono profesional y laico."
            respuesta = model.generate_content(prompt)
            st.markdown(respuesta.text)

# --- OPCIÓN 3: CONSULTAS PEDAGÓGICAS ---
elif opcion == "❓ Consultas Pedagógicas (Educación Especial)":
    st.subheader("Consultoría Docente")
    pregunta = st.text_area("Ingresa tu duda técnica o pedagógica:")
    
    if st.button("🔍 Consultar"):
        with st.spinner('Analizando respuesta técnica...'):
            prompt = f"Actúa como asistente pedagógico para Luis Atencio. Responde de forma técnica, breve y profesional la siguiente duda sobre educación especial: {pregunta}"
            respuesta = model.generate_content(prompt)
            st.markdown(respuesta.text)

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado por <b>Luis Atencio</b> para el Taller Laboral.</div>", unsafe_allow_html=True)
