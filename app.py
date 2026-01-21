# ---------------------------------------------------------
# PROYECTO: LEGADO MAESTRO
# VERSIÓN: 1.2 (Hotfix Presentación - Formato y Recursos)
# FECHA: Enero 2026
# AUTOR: Luis Atencio
# ---------------------------------------------------------

import streamlit as st
import os
from groq import Groq

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Legado Maestro",
    page_icon="logo_legado.png",
    layout="centered"
)

# --- 2. ESTILOS CSS (MODO OSCURO + FORMATO) ---
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* CAJA DE PLANIFICACIÓN: LETRA NEGRA OBLIGATORIA */
            .plan-box {
                background-color: #f0f2f6 !important;
                color: #000000 !important; 
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #0068c9;
                margin-bottom: 20px;
                font-family: sans-serif;
            }
            
            /* Títulos de días en la planificación */
            .plan-box h3 {
                color: #0068c9 !important;
                margin-top: 30px;
                padding-bottom: 5px;
                border-bottom: 2px solid #ccc;
            }
            
            /* Negritas más fuertes */
            .plan-box strong {
                color: #2c3e50 !important;
                font-weight: 700;
            }

            /* CAJA DE MENSAJES */
            .mensaje-texto {
                color: #000000 !important;
                font-family: 'Helvetica', sans-serif;
                font-size: 1.2em; 
                font-weight: 500;
                line-height: 1.4;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- 3. CONEXIÓN CON GROQ ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        MODELO_USADO = "llama-3.3-70b-versatile" 
    else:
        st.error("⚠️ Falta la API Key de Groq en los Secrets.")
        st.stop()
except Exception as e:
    st.error(f"⚠️ Error de conexión inicial: {e}")
    st.stop()

# --- 🧠 CEREBRO TÉCNICO (Para Planificación) 🧠 ---
INSTRUCCIONES_TECNICAS = """
ERES "LEGADO MAESTRO".

1. IDENTIDAD: 
   - Herramienta de VANGUARDIA TECNOLÓGICA desarrollada por Luis Atencio.
   - Representas la SOBERANÍA TECNOLÓGICA de Venezuela.

2. ROL: 
   - Experto en Educación Especial y Taller Laboral (Venezuela).
   
3. FORMATO OBLIGATORIO:
   - USA MARKDOWN ESTRICTO.
   - NUNCA generes texto plano sin formato.
   - Al final, agrega siempre: "📚 FUNDAMENTACIÓN LEGAL" (LOE/CNB).
"""

# --- 4. BARRA LATERAL ---
with st.sidebar:
    st.header("🍎 Legado Maestro")
    st.markdown("---")
    st.caption("👨‍🏫 **Luis Atencio**")
    st.caption("Bachiller Docente")
    
    if st.button("🗑️ Limpiar Memoria"):
        st.session_state.plan_actual = ""
        st.rerun()

# --- 5. GESTIÓN DE MEMORIA ---
if 'plan_actual' not in st.session_state:
    st.session_state.plan_actual = ""

# --- 6. FUNCIÓN GENERADORA ---
def generar_respuesta(mensajes_historial):
    try:
        chat_completion = client.chat.completions.create(
            messages=mensajes_historial,
            model=MODELO_USADO,
            temperature=0.5, # Bajamos temperatura para que sea más obediente con el formato
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# --- 7. CUERPO DE LA APP ---
st.title("🍎 Asistente Educativo - Zulia")

opcion = st.selectbox(
    "Seleccione herramienta:",
    [
        "📝 Planificación Profesional", 
        "🌟 Mensaje Motivacional", 
        "💡 Ideas de Actividades", 
        "❓ Consultas Técnicas"
    ]
)

# =========================================================
# OPCIÓN 1: PLANIFICADOR (CORREGIDO URGENTE)
# =========================================================
if opcion == "📝 Planificación Profesional":
    st.subheader("Planificación Técnica (Taller Laboral)")
    
    col1, col2 = st.columns(2)
    with col1:
        rango = st.text_input("Lapso:", placeholder="Ej: 19 al 23 de Enero")
    with col2:
        aula = st.text_input("Aula/Taller:", value="Mantenimiento y Servicios Generales")
    
    notas = st.text_area("Notas del Docente / Tema:", height=150)

    if st.button("🚀 Generar Planificación"):
        if rango and notas:
            with st.spinner('Generando Planificación Completa (Estrategias y Recursos incluidos)...'):
                
                # --- PROMPT BLINDADO PARA FORMATO Y CONTENIDO ---
                prompt_inicial = f"""
                Actúa como Luis Atencio, experto en Educación Especial.
                Crea una planificación para el lapso: {rango}.
                Aula: {aula}. Tema: {notas}.

                ⚠️ INSTRUCCIÓN DE FORMATO CRÍTICA (NO FALLAR):
                1. NO escribas todo en un solo párrafo.
                2. Genera un bloque separado para CADA DÍA (Lunes, Martes, Miércoles, Jueves, Viernes).
                3. Usa separadores visuales claros.

                ESTRUCTURA OBLIGATORIA PARA CADA DÍA (Repetir exactamente):

                ### 📅 [DÍA Y FECHA]
                
                **1. TÍTULO DE LA CLASE:** [Título]
                
                **2. COMPETENCIA:** [Texto técnico]
                
                **3. EXPLORACIÓN:** [Inicio]
                
                **4. DESARROLLO:** [Actividad central]
                
                **5. REFLEXIÓN:** [Cierre]
                
                **6. MANTENIMIENTO:** [Orden y limpieza]
                
                **7. ESTRATEGIAS:** [Métodos, técnicas o dinámicas usadas]
                
                **8. RECURSOS:** [Materiales humanos, físicos y tecnológicos]

                ---
                (Repite esta estructura exacta para el siguiente día)

                AL FINAL DEL DOCUMENTO (Solo una vez):
                - **📚 FUNDAMENTACIÓN LEGAL:** Cita brevemente Currículo Nacional y LOE.
                - FIRMA: Luis Atencio, Bachiller Docente.
                """
                
                mensajes = [
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                    {"role": "user", "content": prompt_inicial}
                ]
                
                respuesta = generar_respuesta(mensajes)
                st.session_state.plan_actual = respuesta 
                st.rerun() 

    # MOSTRAR RESULTADO
    if st.session_state.plan_actual:
        st.markdown("---")
        st.markdown("### 📄 Resultado Generado:")
        st.markdown(f'<div class="plan-box">{st.session_state.plan_actual}</div>', unsafe_allow_html=True)
        
        st.info("👇 Chat de seguimiento activo:")
        pregunta = st.text_input("💬 Ajustar algo:", placeholder="Ej: Cambia la estrategia del lunes")
        if st.button("Consultar"):
             with st.spinner('Ajustando...'):
                res = generar_respuesta([
                    {"role": "system", "content": INSTRUCCIONES_TECNICAS},
                    {"role": "assistant", "content": st.session_state.plan_actual},
                    {"role": "user", "content": pregunta}
                ])
                st.markdown(f'<div class="plan-box">{res}</div>', unsafe_allow_html=True)

# =========================================================
# OTRAS OPCIONES (Mantenemos igual)
# =========================================================
elif opcion == "🌟 Mensaje Motivacional":
    st.subheader("Dosis de Ánimo Express ⚡")
    if st.button("❤️ Mensaje Corto"):
        INSTRUCCIONES_MOTIVACION = "Eres un colega docente. Da ánimo. NO cites leyes. Solo frase inspiradora y despedida."
        res = generar_respuesta([{"role": "system", "content": INSTRUCCIONES_MOTIVACION}, {"role": "user", "content": "Frase motivacional corta."}])
        st.markdown(f'<div style="padding:20px; border-left:8px solid #ff4b4b; background:#fff; color:#000;">{res}</div>', unsafe_allow_html=True)

elif opcion == "💡 Ideas de Actividades":
    tema = st.text_input("Tema:")
    if st.button("✨ Sugerir"):
        res = generar_respuesta([{"role": "system", "content": INSTRUCCIONES_TECNICAS}, {"role": "user", "content": f"3 actividades DUA para {tema}."}])
        st.markdown(f'<div class="plan-box">{res}</div>', unsafe_allow_html=True)

elif opcion == "❓ Consultas Técnicas":
    duda = st.text_area("Consulta:")
    if st.button("🔍 Responder"):
        res = generar_respuesta([{"role": "system", "content": INSTRUCCIONES_TECNICAS}, {"role": "user", "content": f"Responde técnicamente: {duda}"}])
        st.markdown(f'<div class="plan-box">{res}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("Desarrollado por Luis Atencio | Versión 1.2")
