import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DE SEGURIDAD ---
try:
    # Llamamos a tu llave desde los Secrets de Streamlit
    raw_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=raw_key.strip())
    
    # CAMBIO CLAVE: Usamos solo el nombre del modelo sin prefijos
    # Esto soluciona el error 404 en la mayoría de las versiones
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ Error de configuración: {e}")
    st.stop()

# --- CONFIGURACIÓN DE LA PÁGINA (Tu esencia, Luis) ---
st.set_page_config(page_title="Legado Maestro", page_icon="🍎")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Legado Maestro")
    st.write("---")
    st.info("💡 Apoyo Docente")
    st.caption("👨‍🏫 **Prof. Luis Atencio**")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")

st.title("🍎 Asistente Educativo")
st.subheader("Planificación Pedagógica - Zulia")

opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    ["📝 Crear Plan de Clase", "🔧 Consultar Mantenimiento", "💡 Idea para Actividad"]
)

if opcion == "📝 Crear Plan de Clase":
    st.markdown("### Generador de Planificaciones")
    tema = st.text_input("Tema (Ej: Higiene, Herramientas, Valores)")
    grado = st.text_input("Grupo", value="Mantenimiento y Servicios Generales")
    
    if st.button("✨ Generar Plan"):
        if tema and grado:
            with st.spinner('Procesando orden del Prof. Luis...'):
                try:
                    # Instrucción optimizada para evitar errores de contenido
                    prompt = f"Actúa como docente de Educación Especial en el Zulia. Crea un plan sobre {tema} para el grupo {grado} (Semana 19-23 de enero 2026). Incluye Inicio, Desarrollo y Cierre."
                    respuesta = model.generate_content(prompt)
                    st.success("¡Planificación lista!")
                    st.markdown(respuesta.text)
                except Exception as e:
                    st.error(f"Error técnico al generar: {e}")
        else:
            st.warning("Por favor, completa los campos de tema y grupo.")

# --- TU SELLO AL PIE ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b> para el futuro de la educación.</div>", unsafe_allow_html=True)
# --- TU SELLO AL PIE ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b></div>", unsafe_allow_html=True)
