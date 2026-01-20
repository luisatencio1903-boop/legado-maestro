import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
try:
    # Limpieza total de la clave de tus Secrets
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    genai.configure(api_key=api_key)
    
    # ACTUALIZACIÓN 2026: Usamos el modelo que apareció en tu diagnóstico
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"⚠️ Error en la configuración: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN DE LA PÁGINA (Sello Prof. Luis Atencio) ---
st.set_page_config(page_title="Legado Maestro", page_icon="🍎")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Legado Maestro")
    st.info("💡 Herramienta de Apoyo Docente")
    st.caption("👨‍🏫 **Creado por el Prof. Luis Atencio**")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")

# --- 3. LÓGICA DE LA APLICACIÓN ---
st.title("🍎 Asistente Educativo - Zulia")
st.subheader("Planificación para Educación Especial")

opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    ["📝 Crear Plan de Clase", "🔧 Consultar Mantenimiento", "💡 Idea para Actividad"]
)

if opcion == "📝 Crear Plan de Clase":
    tema = st.text_input("¿Qué tema quieres enseñar? (Ej: Higiene, Herramientas)")
    grado = st.text_input("¿Para qué grupo es?", value="Mantenimiento y Servicios Generales")
    
    if st.button("✨ Generar Plan"):
        if tema and grado:
            with st.spinner('El Prof. Luis está procesando la información...'):
                try:
                    prompt = f"""
                    Actúa como docente experto de Educación Especial en el Zulia.
                    Crea un plan de clase para el Taller Laboral sobre {tema} para el grupo {grado}.
                    Incluye Inicio, Desarrollo y Cierre.
                    """
                    respuesta = model.generate_content(prompt)
                    st.success("¡Planificación lista!")
                    st.markdown(respuesta.text)
                except Exception as e:
                    st.error(f"Error al generar contenido: {e}")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<center>Desarrollado con ❤️ por <b>Luis Atencio</b></center>", unsafe_allow_html=True)
