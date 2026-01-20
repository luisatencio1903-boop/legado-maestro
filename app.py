import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"⚠️ Error de configuración: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Legado Maestro", page_icon="🍎")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Legado Maestro")
    st.info("💡 Apoyo Docente")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente - Taller Laboral")
    st.write("---")

# --- 3. LÓGICA DE LA APLICACIÓN ---
st.title("🍎 Asistente Educativo - Zulia")
st.subheader("Planificador Semanal Profesional")

# Cuadros de entrada de datos
rango_fecha = st.text_input("Ingresa el lapso de la semana:", placeholder="Ej: del 19 al 23 de enero de 2026")
grado = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")

st.markdown("### 📝 Cronograma de Actividades")
st.info("Escribe el día y tus actividades. El profesor Luis se encargará de darle el formato profesional a cada una.")

notas_docente = st.text_area(
    "Escribir notas (Lunes: actividad, Martes: actividad...)",
    height=200,
    placeholder="Lunes: [Actividades...]\nMartes: [Actividades...]"
)

if st.button("🚀 Generar Planificación Estructurada"):
    if rango_fecha and notas_docente:
        with st.spinner('Luis, estructurando la planificación con terminología técnica...'):
            try:
                # PROMPT ACTUALIZADO CON "REFLEXIÓN"
                prompt = f"""
                Actúa como Luis Atencio, Bachiller Docente en el Taller Laboral 'Elena Rosa Aranguibel'.
                Tu tarea es organizar estas notas en una planificación técnica y concisa para Educación Especial.

                LAPSO: {rango_fecha}
                AULA: {grado}
                NOTAS DEL DOCENTE: {notas_docente}

                FORMATO TÉCNICO POR DÍA:
                1. Día y Fecha: (Asignar fecha exacta según el lapso {rango_fecha}).
                2. Título: (Breve y profesional).
                3. Competencia: (Redacción técnica en tercera persona).
                4. Exploración: (Actividad inicial directa, sin coloquialismos).
                5. Desarrollo: (Pasos prácticos en viñetas concisas).
                6. REFLEXIÓN: (Describir la actividad de evaluación, análisis de lo aprendido y la rutina de aseo personal de forma resumida).
                7. Mantenimiento: (Tarea técnica de orden y limpieza del taller).

                REGLAS ESTRICTAS:
                - Usa un lenguaje técnico y profesional. Elimina cualquier saludo informal o referencia religiosa.
                - Sé breve y usa viñetas. No escribas párrafos largos.
                - Firma al final: Luis Atencio, Bachiller Docente.
                """
                
                respuesta = model.generate_content(prompt)
                st.success("¡Planificación generada con éxito!")
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
    else:
        st.warning("Luis, por favor completa el lapso de fecha y las actividades.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b> para el Taller Laboral.</div>", unsafe_allow_html=True)
