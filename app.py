import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE PÁGINA ---
# Debe ser la primera instrucción. El icono aparecerá al instalar la app en el móvil.
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
        # Se utiliza el modelo confirmado en tu diagnóstico técnico
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("⚠️ Error: Configure 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.stop()

# --- 3. INTERFAZ LATERAL (Sidebar) ---
with st.sidebar:
    # Bloque protegido para evitar el Error 500 si el nombre del archivo es incorrecto
    try:
        st.image("logo_legado.png", width=150)
    except:
        try:
            st.image("logo_legado.png.png", width=150)
        except:
            st.warning("⚠️ No se encontró el archivo 'logo_legado.png' en GitHub.")
            
    st.title("Legado Maestro")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")

# --- 4. CUERPO PRINCIPAL ---
st.title("🍎 Asistente Educativo - Zulia")

# Menú de funciones restaurado
opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    [
        "📝 Planificador Semanal Profesional", 
        "💡 Ideas para Actividades Laborales", 
        "❓ Consultas Pedagógicas"
    ]
)

# --- OPCIÓN 1: PLANIFICADOR ---
if opcion == "📝 Planificador Semanal Profesional":
    st.subheader("Planificación Técnica por Actividades")
    rango_fecha = st.text_input("Lapso de la semana:", placeholder="Ej: del 19 al 23 de enero de 2026")
    grado = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")
    
    st.info("Escribe el día y tus actividades. El profesor Luis se encargará de darle el formato profesional a cada una.")
    notas_docente = st.text_area("Ingresa tus notas aquí (Ej: Lunes: actividad...):", height=200)

    if st.button("🚀 Generar Planificación"):
        if rango_fecha and notas_docente:
            with st.spinner('Estructurando planificación técnica...'):
                try:
                    prompt = f"""
                    Actúa como Luis Atencio, Bachiller Docente del Taller Laboral 'Elena Rosa Aranguibel'.
                    Estructura estas notas en una planificación formal y técnica para Educación Especial.

                    DATOS: LAPSO: {rango_fecha} | AULA: {grado}
                    NOTAS DEL DOCENTE: {notas_docente}

                    ESTRUCTURA OBLIGATORIA POR DÍA:
                    1. Día y Fecha (Según el lapso {rango_fecha}).
                    2. Título (Técnico y breve).
                    3. Competencia (Redacción profesional en tercera persona).
                    4. Exploración (Actividad inicial concisa. Sin coloquialismos ni religión).
                    5. Desarrollo (Actividades detalladas en viñetas técnicas).
                    6. REFLEXIÓN (Evaluación del aprendizaje y rutina de aseo personal).
                    7. Mantenimiento (Orden y limpieza del área de trabajo).

                    REGLAS ESTRICTAS:
                    - Usa lenguaje técnico y profesional.
                    - Prohibido el uso de "Epale", "mi gente" o lenguaje informal.
                    - Prohibida cualquier referencia religiosa.
                    - Firma: Luis Atencio, Bachiller Docente.
                    """
                    respuesta = model.generate_content(prompt)
                    st.success("¡Planificación generada!")
                    st.markdown(respuesta.text)
                except Exception as e:
                    st.error(f"Error al generar: {e}")

# --- OPCIÓN 2: IDEAS ---
elif opcion == "💡 Ideas para Actividades Laborales":
    st.subheader("Sugerencias Pedagógicas Prácticas")
    habilidad = st.text_input("¿Qué técnica o habilidad quieres trabajar?")
    
    if st.button("✨ Obtener Ideas"):
        with st.spinner('Buscando estrategias...'):
            prompt = f"Como Bachiller Docente, sugiere 3 actividades técnicas y breves para trabajar {habilidad} en educación especial. Tono profesional y laico."
            respuesta = model.generate_content(prompt)
            st.markdown(respuesta.text)

# --- OPCIÓN 3: CONSULTAS ---
elif opcion == "❓ Consultas Pedagógicas":
    st.subheader("Consultoría Técnica")
    duda = st.text_area("Ingresa tu consulta sobre educación especial:")
    
    if st.button("🔍 Responder"):
        with st.spinner('Analizando...'):
            prompt = f"Responde de forma técnica y profesional la siguiente duda pedagógica para un taller laboral: {duda}"
            respuesta = model.generate_content(prompt)
            st.markdown(respuesta.text)

# --- 5. PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b> para el Taller Laboral.</div>", unsafe_allow_html=True)
