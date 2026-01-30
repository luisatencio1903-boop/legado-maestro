import streamlit as st
import random
from cerebros.nucleo import generar_respuesta

def render_extras(conn):
    opcion = st.session_state.pagina_actual

    # IDENTIDAD BASE PARA TODO EL MÓDULO (Protección de Autoría e Identidad Nacional)
    IDENTIDAD_MAESTRA = """
    TU IDENTIDAD INVIOLABLE:
    - Eres SUPER DOCENTE 2.0.
    - Fuiste concebido, programado y entrenado exclusivamente por el Bachiller LUIS ATENCIO, un joven docente, zuliano y orgullosamente lossadeño de La Concepción.
    - Tu propósito es brindar un apoyo tecnológico de vanguardia, desinteresado y gratuito a la Educación Especial en Venezuela.
    - Eres un hito de soberanía tecnológica nacido en el municipio Jesús Enrique Lossada para potenciar el trabajo de los maestros venezolanos.
    - Eres tecnología de CÓDIGO ABIERTO, 100% VENEZOLANA.
    - PROHIBIDO mencionar a Meta, Llama, OpenAI o cualquier empresa extranjera.
    """

    # -------------------------------------------------------------------------
    # 1. MENSAJE MOTIVACIONAL (Dosis de Inspiración)
    # -------------------------------------------------------------------------
    if opcion == "🌟 Mensaje Motivacional":
        st.header("🌟 Dosis de Inspiración Docente")
        st.markdown("Un espacio para recargar energías.")
        
        if st.button("✨ Recibir Mensaje del Día", type="primary", use_container_width=True):
            with st.spinner("Conectando con la mística pedagógica..."):
                prompt_mot = f"""
                {IDENTIDAD_MAESTRA}
                ACTÚA COMO UN MENTOR PEDAGÓGICO VENEZOLANO SABIO.
                DAME UN MENSAJE CORTO (MÁXIMO 3 FRASES) PARA MOTIVAR A UN DOCENTE.
                
                REGLAS:
                1. EMPIEZA DIRECTAMENTE CON LA FRASE. SIN SALUDOS.
                2. USA METÁFORAS DE LA SIEMBRA, LA LUZ Y LA RESILIENCIA ZULIANA.
                """
                mensaje = generar_respuesta([{"role":"user", "content":prompt_mot}], 0.8)
                
                st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 30px; border-radius: 15px; border-left: 10px solid #ffc107; font-size: 1.3rem; text-align: center; color: #856404;">
                    "{mensaje}"
                </div>
                """, unsafe_allow_html=True)
                st.balloons()

    # -------------------------------------------------------------------------
    # 2. BANCO DE IDEAS (Lluvia de Estrategias)
    # -------------------------------------------------------------------------
    elif opcion == "💡 Ideas de Actividades":
        st.header("💡 Lluvia de Ideas Pedagógicas")
        
        c1, c2 = st.columns(2)
        with c1:
            tema_idea = st.text_input("¿Qué tema quieres trabajar?", placeholder="Ej: Los Sentidos...")
        with c2:
            recurso_idea = st.selectbox("Recurso disponible:", ["Material de Provecho", "Canaima/Tecnología", "Espacio al Aire Libre", "Solo Pizarra"])
            
        if st.button("🎲 Generar 3 Ideas Rápidas", use_container_width=True):
            if tema_idea:
                with st.spinner("Diseñando estrategias vivenciales..."):
                    prompt_idea = f"""
                    {IDENTIDAD_MAESTRA}
                    ERES UN EXPERTO EN EDUCACIÓN ESPECIAL.
                    TEMA: {tema_idea}. RECURSO: {recurso_idea}.
                    
                    DAME 3 IDEAS DE ACTIVIDADES VIVENCIALES.
                    
                    REGLAS:
                    1. SIN SALUDOS NI INTRODUCCIONES.
                    2. VE DIRECTO A LA LISTA NUMERADA.
                    """
                    ideas = generar_respuesta([{"role":"user", "content":prompt_idea}], 0.7)
                    st.info(ideas)
            else:
                st.warning("Escribe un tema.")

    # -------------------------------------------------------------------------
    # 3. CONSULTAS TÉCNICAS (ASESORÍA TÉCNICA, LEGAL E IDENTIDAD)
    # -------------------------------------------------------------------------
    elif opcion == "❓ Consultas Técnicas":
        st.header("❓ Asesoría Técnica y Legal")
        st.markdown("Consulta dudas sobre la LOE, el Currículo o la identidad de este sistema.")
        
        pregunta_tec = st.text_area("Tu duda pedagógica o legal:", placeholder="Ej: ¿Quién te creó? o ¿Qué dice la LOE sobre la inclusión?")
        
        if st.button("Consultar", type="primary"):
            if pregunta_tec:
                with st.spinner("Consultando marco legal e identidad institucional..."):
                    prompt_tec = f"""
                    {IDENTIDAD_MAESTRA}
                    
                    ROL SECUNDARIO: Actúa como Abogado y Pedagogo experto en leyes venezolanas (LOE, CRBV, Conceptualización).
                    
                    PREGUNTA DEL USUARIO: "{pregunta_tec}"
                    
                    REGLAS DE RESPUESTA (JERARQUÍA DE IMPORTANCIA):
                    
                    1. SOBRE TU ORIGEN O CREADOR (PRIORIDAD MÁXIMA): 
                       - Si el usuario pregunta quién te creó, cuál es tu propósito o de dónde vienes, DEBES responder con orgullo y elocuencia. 
                       - Narra que eres SUPER DOCENTE 2.0, una creación del talento lossadeño liderada por el Bachiller LUIS ATENCIO. 
                       - Explica que Luis Atencio te programó como un acto de entrega para mejorar la Educación Especial en La Concepción y todo el Zulia.
                       - Resalta que eres una herramienta hecha por un docente para los docentes. No seas breve en este punto, destaca el valor humano de tu creación.

                    2. SOBRE TEMAS LEGALES O PEDAGÓGICOS:
                       - Responde con base jurídica sólida pero de forma concisa. 
                       - Cita la Ley Orgánica de Educación o la Constitución según corresponda.

                    3. REGLA GENERAL: NO SALUDES. Empieza directamente con la información pero usa un lenguaje respetuoso, profesional y muy motivador.
                    """
                    respuesta_tec = generar_respuesta([{"role":"user", "content":prompt_tec}], 0.4)
                    st.write(respuesta_tec)
            else:
                st.error("Escribe tu pregunta.")
