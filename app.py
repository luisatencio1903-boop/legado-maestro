import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    genai.configure(api_key=api_key)
    # Mantener el modelo Gemini 2.5 Flash confirmado en tu diagnóstico
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

# SECCIÓN DE CRONOGRAMA CON TU CAMBIO SOLICITADO
st.markdown("### 📝 Cronograma de la Semana")
# Cambio realizado aquí: de "La IA se encargará" a "El profesor Luis se encargará"
st.info("Escribe el día y tus actividades. El profesor Luis se encargará de darle el formato profesional a cada una.")

notas_docente = st.text_area(
    "Escribe aquí (Ej: Lunes: Higiene personal. Martes: Mantenimiento general...)",
    height=200,
    placeholder="Lunes: [Actividades...]\nMartes: [Actividades...]\nMiércoles: [Actividades...]"
)

if st.button("🚀 Generar Planificación Estructurada"):
    if rango_fecha and notas_docente:
        with st.spinner('Luis, estoy organizando tus actividades bajo tu formato profesional...'):
            try:
                # El prompt se mantiene enfocado en tu identidad de Bachiller Docente
                prompt = f"""
                Actúa como Luis Atencio, bachiller docente del Taller Laboral 'Elena Rosa Aranguibel'.
                Tu tarea es organizar estas actividades en una planificación profesional y modesta.

                LAPSO: {rango_fecha}
                AULA: {grado}

                NOTAS DEL DOCENTE:
                {notas_docente}

                FORMATO POR DÍA DETECTADO:
                1. Día y Fecha: (Asigna la fecha exacta según el lapso {rango_fecha}).
                2. Título: (Acorde a la actividad).
                3. Competencia: (Redacción técnica y sencilla).
                4. Exploración: (Charla o dinámica inicial).
                5. Desarrollo: (Explicación detallada de las actividades anotadas).
                6. Cierre: (Reflexión y rutina de aseo personal).
                7. Mantenimiento: (Tarea técnica de orden y limpieza).

                REGLAS:
                - Usa un tono motivador y zuliano ("¡Epale mi gente!").
                - Firma como: Luis Atencio, Bachiller Docente.
                """
                
                respuesta = model.generate_content(prompt)
                st.success("¡Planificación organizada con éxito!")
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
    else:
        st.warning("Luis, por favor ingresa el lapso de fecha y tus actividades.")

# --- PIE DE PÁGINA ---
st.markdown("---")
st.markdown("<div style='text-align: center'>Desarrollado con ❤️ por <b>Luis Atencio</b> para el Taller Laboral.</div>", unsafe_allow_html=True)
