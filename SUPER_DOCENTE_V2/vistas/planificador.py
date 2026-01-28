import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils.comunes import ahora_ve
from cerebros.nucleo import generar_respuesta

def render_planificador(conn):
    st.title("🧠 Planificador Inteligente")
    st.info("Genera tu planificación semanal o de proyecto y actívala para el Aula Virtual.")

    # --- 1. CONFIGURACIÓN DEL PLAN ---
    with st.expander("🛠️ Configuración de la Planificación", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            tipo_plan = st.selectbox("Tipo de Plan:", ["Proyecto de Aprendizaje (P.A.)", "Plan Semanal", "P.E.I. (Individual)"])
            nivel = st.selectbox("Nivel / Modalidad:", ["Educación Especial (General)", "Taller Laboral (T.E.L.)", "Inicial", "Caipa / Autismo"])
        with col2:
            fecha_ini = st.date_input("Fecha Inicio:")
            fecha_fin = st.date_input("Fecha Cierre:")
    
    st.divider()
    
    # --- 2. DATOS ESPECÍFICOS ---
    nombre_proyecto = st.text_input("Nombre del Proyecto o Tema Generador:", placeholder="Ej: Las plantas medicinales de mi comunidad...")
    
    col_a, col_b = st.columns(2)
    with col_a:
        areas = st.multiselect("Áreas de Aprendizaje:", ["Lenguaje y Comunicación", "Matemática", "Ciencias Naturales", "Identidad y Soberanía", "Educación Física"])
    with col_b:
        estrategias_extra = st.text_input("Estrategias o Recursos específicos (Opcional):", placeholder="Ej: Uso de canaimitas, Huerto escolar...")

    # --- 3. GENERACIÓN CON IA ---
    if st.button("✨ GENERAR PLANIFICACIÓN (IA)", type="primary", use_container_width=True):
        if not nombre_proyecto:
            st.error("⚠️ Debes escribir un nombre para el proyecto.")
        else:
            with st.spinner("⏳ La IA está redactando tu plan paso a paso..."):
                # Construcción del Prompt Modular
                prompt = f"""
                ACTÚA COMO UN EXPERTO DOCENTE. REDACTA UNA PLANIFICACIÓN TIPO: {tipo_plan}.
                PARA LA MODALIDAD: {nivel}.
                TEMA/PROYECTO: {nombre_proyecto}.
                ÁREAS: {', '.join(areas)}.
                EXTRAS: {estrategias_extra}.
                FECHAS: Del {fecha_ini} al {fecha_fin}.
                
                ESTRUCTURA OBLIGATORIA DE LA RESPUESTA:
                1. IDENTIFICACIÓN Y DIAGNÓSTICO (Breve).
                2. PROPÓSITO GENERAL.
                3. ESTRATEGIAS POR DÍA (LUNES A VIERNES) CON INICIO, DESARROLLO Y CIERRE.
                4. INDICADORES DE EVALUACIÓN.
                
                REGLA DE ORO: Usa terminología venezolana (Participantes, P.A., Material de provecho).
                """
                
                # Llamada al núcleo (cerebro)
                respuesta_ia = generar_respuesta([{"role": "user", "content": prompt}], temperatura=0.7)
                
                # Guardamos en sesión para no perderlo si la pantalla recarga
                st.session_state.plan_generado_temp = respuesta_ia
                st.success("✅ Planificación generada.")

    # --- 4. VISUALIZACIÓN Y GUARDADO ---
    if 'plan_generado_temp' in st.session_state:
        st.markdown("### 📝 Revisa y Edita tu Plan")
        plan_final = st.text_area("Contenido del Plan:", value=st.session_state.plan_generado_temp, height=400)
        
        col_g1, col_g2 = st.columns([1, 2])
        
        with col_g1:
            if st.button("💾 GUARDAR Y ACTIVAR", type="primary"):
                try:
                    # 1. Desactivar planes anteriores del usuario (Para que no se crucen)
                    # NOTA: Esto es lógica V1 simplificada. Idealmente haríamos un update masivo.
                    
                    # 2. Guardar el nuevo
                    nuevo_plan = pd.DataFrame([{
                        "FECHA": f"{fecha_ini} al {fecha_fin}",
                        "USUARIO": st.session_state.u['NOMBRE'],
                        "TIPO": tipo_plan,
                        "TITULO": nombre_proyecto,
                        "CONTENIDO": plan_final,
                        "ESTADO": "ACTIVO", # Importante para que el Aula Virtual lo vea
                        "CREADO_EL": ahora_ve().strftime("%d/%m/%Y %H:%M")
                    }])
                    
                    url = st.secrets["GSHEETS_URL"]
                    # Leemos hoja actual
                    df_actual = conn.read(spreadsheet=url, worksheet="Hoja1", ttl=0)
                    
                    # Marcamos como INACTIVO todo lo anterior de este usuario (Pandas logic)
                    if not df_actual.empty:
                        df_actual.loc[df_actual['USUARIO'] == st.session_state.u['NOMBRE'], 'ESTADO'] = "INACTIVO"
                    
                    # Concatenamos
                    df_final = pd.concat([df_actual, nuevo_plan], ignore_index=True)
                    
                    # Subimos a Google Sheets
                    conn.update(spreadsheet=url, worksheet="Hoja1", data=df_final)
                    
                    st.balloons()
                    st.success("✅ ¡Planificación Activada! Ya aparecerá en tu Aula Virtual.")
                    # Limpiamos temporal
                    del st.session_state.plan_generado_temp
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error guardando: {e}")
