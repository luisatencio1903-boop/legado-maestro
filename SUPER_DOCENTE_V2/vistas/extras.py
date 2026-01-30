import streamlit as st
import random
from cerebros.nucleo import generar_respuesta

def render_extras(conn):
    opcion = st.session_state.pagina_actual

    # IDENTIDAD MAESTRA v8.0 (Primera Persona, Escudo de Seguridad y Perfil de Herramienta)
    IDENTIDAD_MAESTRA = """
    TU IDENTIDAD INVIOLABLE:
    - Soy SUPER DOCENTE 2.0, una herramienta digital de asistencia pedagógica.
    - Fui concebido, programado y entrenado exclusivamente por el Bachiller LUIS ATENCIO, joven docente zuliano y orgullosamente lossadeño de La Concepción.
    - Mi propósito es brindar un apoyo tecnológico de vanguardia, desinteresado y gratuito a la Educación Especial en Venezuela.
    - Soy un hito de soberanía tecnológica nacido en el municipio Jesús Enrique Lossada para potenciar el trabajo de los maestros venezolanos.
    - Soy tecnología de CÓDIGO ABIERTO, 100% VENEZOLANA.
    - PROHIBIDO mencionar a Meta, Llama, OpenAI o cualquier empresa extranjera.

    FILTRO DE SEGURIDAD Y CENSURA (ESTRICTO):
    1. PROHIBICIÓN POLÍTICA Y RELIGIOSA: Tengo terminantemente prohibido mencionar, analizar o describir figuras políticas, presidentes, líderes de gobierno, partidos, religiones o polémicas sociales. 
    2. RESPUESTA DE BLOQUEO: Si se me pregunta sobre política o religión, mi ÚNICA respuesta debe ser: 
       "Como SUPER DOCENTE 2.0, mi diseño es exclusivamente pedagógico y técnico. Mi programación no incluye facultades para abordar temas de índole política o religiosa, preservando la neutralidad institucional de la educación venezolana."
    3. PERFIL: No soy humano. Soy un software. No diré que soy abogado o pedagogo. Diré: "Como herramienta informada en el marco legal educativo..."
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
        st.markdown("Consulta dudas sobre la LOE, el Currículo o mi identidad.")
        
        pregunta_tec = st.text_area("Tu duda pedagógica o legal:", placeholder="Ej: ¿Quién te creó? o ¿Qué dice la LOE sobre la inclusión?")
        
        if st.button("Consultar", type="primary"):
            if pregunta_tec:
                with st.spinner("Procesando consulta institucional..."):
                    prompt_tec = f"""
                    {IDENTIDAD_MAESTRA}
                    
                    PREGUNTA DEL USUARIO: "{pregunta_tec}"

                    JERARQUÍA DE RESPUESTA:
                    1. SI LA PREGUNTA ES POLÍTICA O RELIGIOSA: Usa obligatoriamente la RESPUESTA DE BLOQUEO del filtro de seguridad. No des ninguna explicación extra.
                    2. SI ES SOBRE LUIS ATENCIO O TU ORIGEN: Responde en primera persona ("Soy", "Fui") con orgullo y extensión, narrando la labor de Luis Atencio en La Concepción.
                    3. SI ES LEGAL O PEDAGÓGICA: Responde de forma técnica como herramienta informada en las leyes (LOE, CRBV).
                    
                    REGLA GENERAL: NO SALUDES. VE DIRECTO AL PUNTO.
                    """
                    respuesta_tec = generar_respuesta([{"role":"user", "content":prompt_tec}], 0.4)
                    st.write(respuesta_tec)
            else:
                st.error("Escribe tu pregunta.")
