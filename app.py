import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    genai.configure(api_key=api_key)
    # Mantenemos Gemini 2.5 Flash por su capacidad de seguir instrucciones precisas
    model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    st.error(f"⚠️ Error de configuración: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Legado Maestro", page_icon="🍎")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.title("Legado Maestro")
    st.info("💡 Herramienta de Apoyo Docente")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente - Taller Laboral")
    st.write("---")

# --- 3. LÓGICA DE LA APLICACIÓN ---
st.title("🍎 Asistente Educativo - Zulia")
st.subheader("Planificador Semanal por Actividades")

# Cuadro para el Lapso de Fecha
rango_fecha = st.text_input("Ingresa el lapso de la semana:", placeholder="Ej: del 19 de enero al 23 de enero del 2026")

# Cuadro para el Aula / Grupo
grado = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")

# SECCIÓN DE CRONOGRAMA
st.markdown("### 📝 Cronograma de la Semana")
st.info("Escribe el día y tus actividades. El profesor Luis se encargará de darle el formato profesional a cada una.")

notas_docente = st.text_area(
    "Escribe aquí (Ej: Lunes: Higiene personal. Martes: Mantenimiento general...)",
    height=200,
    placeholder="Lunes: [Actividades...]\nMartes: [Actividades...]\nMiércoles: [Actividades...]"
)

if st.button("🚀 Generar Planificación Estructurada"):
    if rango_fecha and notas_docente:
        with st.spinner('Generando planificación profesional y técnica...'):
            try:
                # PROMPT PROFESIONAL Y TÉCNICO:
                # Instrucciones estrictas para eliminar coloquialismos y ser conciso.
                prompt = f"""
                Actúa como Luis Atencio, Bachiller Docente del Taller Laboral 'Elena Rosa Aranguibel'.
                Tu tarea es estructurar las notas del docente en una planificación didáctica formal, técnica y concisa para Educación Especial.

                LAPSO: {rango_fecha}
                AULA: {grado}

                NOTAS DEL DOCENTE:
                {notas_docente}

                INSTRUCCIONES DE FORMATO ESTRICTO PARA CADA DÍA:
                1.  **Día y Fecha:** (Asignar fecha exacta según el lapso {rango_fecha}).
                2.  **Título:** (Breve y descriptivo de la actividad principal).
                3.  **Competencia:** (Redactar en tercera persona, usando verbos en presente indicativo y terminología pedagógica. Ej: "Identifica las herramientas...", "Ejecuta rutinas de...").
                4.  **Exploración:** (Describir la actividad inicial de forma breve y directa. Evitar saludos coloquiales o narraciones extensas. Usar viñetas para listar acciones puntuales).
                5.  **Desarrollo:** (Listar las actividades principales de forma secuencial, concisa y técnica, usando viñetas. Describir la acción y el recurso, sin explicaciones innecesarias).
                6.  **Cierre:** (Especificar la actividad de evaluación o reflexión y la rutina de aseo de forma directa y resumida).
                7.  **Mantenimiento:** (Describir la tarea técnica de orden y limpieza a realizar).

                REGLAS CRÍTICAS DE TONO Y CONTENIDO:
                -   **TONO PROFESIONAL:** Usar un lenguaje técnico, formal y objetivo, adecuado para una planificación docente. Evitar por completo coloquialismos como "Epale", "mi gente", "chévere".
                -   **LAICIDAD:** No incluir ninguna referencia religiosa (Dios, Virgen, santos). La planificación debe ser estrictamente pedagógica.
                -   **CONCISIÓN:** Las descripciones deben ser breves y directas, utilizando viñetas para facilitar la lectura rápida. Evitar párrafos largos o explicaciones redundantes.
                -   **FIRMA:** Finalizar el documento únicamente con: Luis Atencio, Bachiller Docente.
                """
                
                respuesta = model.generate_content(prompt)
                st.success("¡Planificación profesional generada con éxito!")
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
    else:
        st.warning("Por favor, ingresa el lapso de fecha y tus actividades para generar la planificación.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b> para el Taller Laboral.</div>", unsafe_allow_html=True)
