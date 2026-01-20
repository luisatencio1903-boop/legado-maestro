import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE PÁGINA (LOGO PARA EL MÓVIL) ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. SEGURIDAD (LLAVE API) ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"].strip()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
    else:
        st.error("⚠️ Error: Configure 'GOOGLE_API_KEY' en los Secrets.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión: {e}")
    st.stop()

# --- 3. INTERFAZ LATERAL (IDENTIDAD DEL PROFESOR LUIS) ---
with st.sidebar:
    # Solución para el error de nombre de archivo en GitHub
    try:
        st.image("logo_legado.png", width=150)
    except:
        try:
            st.image("logo_legado.png.png", width=150)
        except:
            st.warning("⚠️ Sube 'logo_legado.png' a GitHub.")
            
    st.title("Legado Maestro")
    st.markdown("---")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    st.caption("Taller Laboral 'Elena Rosa Aranguibel'")
    st.write("---")
    st.info("💡 Herramienta diseñada para el fortalecimiento de la Educación Especial en el Zulia.")

# --- 4. MENÚ DE FUNCIONES ---
st.title("🍎 Asistente Educativo - Zulia")

opcion = st.selectbox(
    "¿Qué vamos a trabajar hoy, colega?",
    ["📝 Planificador Semanal Profesional", "💡 Ideas para Actividades", "❓ Consultas Técnicas"]
)

# --- OPCIÓN 1: PLANIFICADOR (TU FORMATO MAESTRO) ---
if opcion == "📝 Planificador Semanal Profesional":
    st.subheader("Estructuración de Planificación Semanal")
    rango = st.text_input("Lapso de la semana:", placeholder="Ej: del 19 al 23 de enero de 2026")
    aula = st.text_input("Aula / Grupo:", value="Mantenimiento y Servicios Generales")
    
    st.info("Escribe tus actividades por día. El profesor Luis se encargará de darles el formato profesional técnico.")
    notas = st.text_area("Ingresa tus notas aquí:", height=200)

    if st.button("🚀 Generar Planificación Estructurada"):
        if rango and notas:
            with st.spinner('Luis, estructurando el plan bajo estándares técnicos...'):
                try:
                    prompt = f"""
                    Actúa como Luis Atencio, Bachiller Docente del Taller Laboral 'Elena Rosa Aranguibel'.
                    Organiza estas notas en una planificación formal, técnica y concisa para Educación Especial.

                    LAPSO: {rango} | AULA: {aula}
                    NOTAS: {notas}

                    ESTRUCTURA POR DÍA:
                    1. Día y Fecha.
                    2. Título (Técnico).
                    3. Competencia (Redacción profesional).
                    4. Exploración (Concisa, sin coloquialismos ni religión).
                    5. Desarrollo (Viñetas técnicas).
                    6. REFLEXIÓN (Evaluación y rutina de aseo resumida).
                    7. Mantenimiento (Orden y limpieza).

                    REGLAS: Tono profesional, laico y modesto. 
                    FIRMA AL FINAL: Luis Atencio, Bachiller Docente.
                    """
                    res = model.generate_content(prompt)
                    st.success("¡Planificación lista para su uso pedagógico!")
                    st.markdown(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")

# --- OTRAS FUNCIONES ---
elif opcion == "💡 Ideas para Actividades":
    tema = st.text_input("Habilidad a fortalecer:")
    if st.button("✨ Sugerir"):
        res = model.generate_content(f"Como Bachiller Docente, sugiere 3 actividades técnicas breves para {tema}. Tono profesional.")
        st.markdown(res.text)

elif opcion == "❓ Consultas Técnicas":
    duda = st.text_area("Duda técnica sobre Educación Especial:")
    if st.button("🔍 Responder"):
        res = model.generate_content(f"Responde de forma técnica y profesional para un entorno de taller laboral: {duda}")
        st.markdown(res.text)

# --- 5. TU MARCA Y FIRMA FINAL (OPTIMIZADA) ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p style='margin-bottom: 0;'>Desarrollado con ❤️ por <b>Luis Atencio</b></p>
        <p style='font-size: 0.8em; color: gray;'>Bachiller Docente - Taller Laboral 'Elena Rosa Aranguibel'</p>
        <p style='font-size: 0.7em; color: lightgray;'>Zulia, Venezuela | 2026</p>
    </div>
    """, 
    unsafe_allow_html=True
)
