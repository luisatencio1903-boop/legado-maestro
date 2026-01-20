import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURACIÓN DE SEGURIDAD (Con limpieza total) ---
try:
    # El .strip() elimina cualquier espacio que se haya colado dentro de las comillas
    api_key = st.secrets["GOOGLE_API_KEY"].strip()
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error en Secrets: {e}")
    st.stop()

# --- 2. DISEÑO DE LUIS ATENCIO ---
st.set_page_config(page_title="Legado Maestro", page_icon="🍎")

with st.sidebar:
    st.title("Legado Maestro")
    st.caption("👨‍🏫 **Prof. Luis Atencio**")
    st.write("---")
    
    # BOTÓN DE DIAGNÓSTICO: Si le das clic, sabremos si la llave funciona
    if st.button("🔍 Probar mi Llave API"):
        try:
            modelos = [m.name for m in genai.list_models()]
            st.success("¡Llave conectada!")
            st.write("Modelos disponibles:", modelos)
        except Exception as e:
            st.error(f"La llave no tiene permisos: {e}")

st.title("🍎 Asistente Educativo - Zulia")

# --- 3. LÓGICA DE PLANIFICACIÓN ---
tema = st.text_input("¿Qué tema trabajaremos?")
if st.button("✨ Generar Plan"):
    if tema:
        with st.spinner('Consultando al cerebro de la IA...'):
            try:
                # Intentamos usar el nombre más simple del modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                respuesta = model.generate_content(f"Plan de clase para {tema} en Educación Especial.")
                st.markdown(respuesta.text)
            except Exception as e:
                # Si sale 404, aquí nos dirá el motivo exacto
                st.error(f"Error 404: El modelo no responde. Detalle: {e}")

st.markdown("---")
st.markdown("<center>Desarrollado por <b>Luis Atencio</b></center>", unsafe_allow_html=True)
