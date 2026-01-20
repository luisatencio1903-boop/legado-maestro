import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN DEL CEREBRO (IA) ---
# Aquí es donde pegas tu llave mágica. Borra lo que está entre comillas y pon la tuya.
genai.configure(api_key="AIzaSyBXN7qqo7H1QrOzRSujrJNg8m0Z6YdVnqo")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Legado Maestro", page_icon="🍎")

# --- BARRA LATERAL (TU FIRMA DE AUTOR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Legado Maestro")
    st.write("---")
    st.info("💡 Herramienta de Apoyo Docente")
    # AQUÍ ESTÁ TU FIRMA / EASTER EGG
    st.caption("👨‍🏫 **Creado por el Prof. Luis Atencio**")
    st.caption("Para el Taller Laboral, mis amigos y estudiantes.")
    st.write("---")

# --- TÍTULO PRINCIPAL ---
st.title("🍎 Asistente Educativo")
st.subheader("Taller de Educación Laboral 'Elena Rosa Aranguibel'")

# --- MENÚ DE OPCIONES ---
opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    ["📝 Crear Plan de Clase", "🔧 Consultar Mantenimiento", "💡 Idea para Actividad"]
)

# --- LÓGICA DE LA APLICACIÓN ---
if opcion == "📝 Crear Plan de Clase":
    st.markdown("### Generador de Planificaciones")
    tema = st.text_input("¿Qué tema quieres enseñar? (Ej: Higiene, Herramientas, Valores)")
    grado = st.text_input("¿Para qué grupo es? (Ej: Grupo de Mantenimiento)")
    
    if st.button("✨ Generar Plan"):
        if tema and grado:
            with st.spinner('El Prof. Luis ha entrenado a esta IA para pensar...'):
                prompt = f"""
                Actúa como un docente experto de Educación Especial en Venezuela.
                Crea un plan de clase detallado para el Taller Laboral.
                Tema: {tema}
                Grupo: {grado}
                
                Incluye:
                1. Inicio (Dinámica de bienvenida)
                2. Desarrollo (Explicación sencilla y práctica)
                3. Cierre (Evaluación o reflexión)
                4. Recursos necesarios.
                """
                respuesta = model.generate_content(prompt)
                st.success("¡Planificación lista!")
                st.markdown(respuesta.text)
        else:
            st.warning("Por favor, escribe el tema y el grupo.")

elif opcion == "🔧 Consultar Mantenimiento":
    st.markdown("### Guía de Mantenimiento y Servicios")
    duda = st.text_area("¿Qué duda tienes sobre limpieza o mantenimiento?")
    
    if st.button("🔍 Consultar"):
        if duda:
            prompt = f"Actúa como supervisor de Mantenimiento y Servicios Generales. Responde esta duda técnica de forma educativa: {duda}"
            respuesta = model.generate_content(prompt)
            st.info(respuesta.text)

elif opcion == "💡 Idea para Actividad":
    st.markdown("### Dinámicas para el Aula")
    if st.button("🎲 Dame una idea sorpresa"):
        prompt = "Dame una idea de juego o dinámica rápida para estudiantes de educación laboral que fomente el compañerismo."
        respuesta = model.generate_content(prompt)
        st.balloons() # ¡Efecto especial de globos!
        st.write(respuesta.text)

# --- PIE DE PÁGINA (TU SELLO) ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b> para el futuro de la educación.</div>", unsafe_allow_html=True)
