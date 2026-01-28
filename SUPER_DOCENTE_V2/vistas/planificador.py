import streamlit as st
import pandas as pd
import time
from utils.comunes import ahora_ve
from cerebros.nucleo import generar_respuesta, seleccionar_cerebro_modalidad

def render_planificador(conn):
    try:
        URL_HOJA = st.secrets["GSHEETS_URL"]
    except:
        st.error("Error de configuración (Secrets).")
        return

    st.markdown("**Generación de Planificación Pedagógica Especializada**")
    
    # -------------------------------------------------------------------------
    # 1. INTERFAZ DE USUARIO (LIMPIA, COMO LA V1)
    # -------------------------------------------------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        rango = st.text_input("Lapso (Fechas):", placeholder="Ej: 26 al 30 de Enero")
    
    with col2:
        modalidad = st.selectbox("Modalidad / Servicio:", [
            "Taller de Educación Laboral (T.E.L.)",
            "Instituto de Educación Especial (I.E.E.B.)",
            "Centro de Atención Integral para Personas con Autismo (C.A.I.P.A.)",
            "Aula Integrada (Escuela Regular)",
            "Unidad Psico-Educativa (U.P.E.)",
            "Educación Inicial (Preescolar)"
        ])
    
    # Inputs condicionales
    aula_especifica = ""
    if "Taller" in modalidad:
        aula_especifica = st.text_input("Especifique el Taller / Aula:", placeholder="Ej: Carpintería, Cocina...")
    
    is_pei = st.checkbox("🎯 ¿Planificación Individualizada (P.E.I.)?")
    
    perfil_alumno = ""
    if is_pei:
        perfil_alumno = st.text_area("Perfil del Alumno (Potencialidades y Necesidades):", placeholder="Describa al estudiante...")
    
    notas = st.text_area("Tema Generador / Referente Ético / Notas:", height=100)

    # -------------------------------------------------------------------------
    # 2. LÓGICA DE DETECCIÓN AUTOMÁTICA (EL CEREBRO BUSCA LOS ACTIVOS)
    # -------------------------------------------------------------------------
    if st.button("🚀 Generar Planificación Estructurada", type="primary"):
        
        if not rango or not notas:
            st.error("⚠️ Por favor ingrese el Lapso y el Tema.")
        elif is_pei and not perfil_alumno:
            st.error("⚠️ Para P.E.I. debe describir el perfil del alumno.")
        elif "Taller" in modalidad and not aula_especifica:
            st.error("⚠️ Especifique el área del Taller.")
        else:
            with st.spinner('Detectando Proyectos y Pensums activos en tu cuenta...'):
                
                # --- A. DETECCIÓN DE PROYECTOS (P.A. / P.S.P.) Y DÍAS ---
                texto_proyectos = "Usa el Tema Generador como eje central."
                try:
                    df_p = conn.read(spreadsheet=URL_HOJA, worksheet="CONFIG_PROYECTO", ttl=0)
                    user_p = df_p[df_p['USUARIO'] == st.session_state.u['NOMBRE']]
                    
                    if not user_p.empty:
                        fila = user_p.iloc[0]
                        # Aquí está la magia: Lee los días que configuraste
                        pa = fila.get('TITULO_PA', 'Sin definir')
                        psp = fila.get('TITULO_PSP', 'Sin definir')
                        dias_pa = str(fila.get('DIAS_PA', 'No asignado'))
                        dias_psp = str(fila.get('DIAS_PSP', 'No asignado'))
                        estado_p = fila.get('ESTADO', 'INACTIVO')

                        if estado_p == 'ACTIVO':
                            texto_proyectos = f"""
                            🚨 **INSTRUCCIÓN DE INTEGRACIÓN OBLIGATORIA (PROYECTOS ACTIVOS):**
                            
                            1. **PROYECTO DE APRENDIZAJE (P.A.):** "{pa}"
                               - DÍAS DE EJECUCIÓN: {dias_pa}.
                               - INSTRUCCIÓN: En estos días específicos, las actividades deben girar en torno a este P.A.
                            
                            2. **PROYECTO SOCIO-PRODUCTIVO (P.S.P.):** "{psp}"
                               - DÍAS DE EJECUCIÓN: {dias_psp}.
                               - INSTRUCCIÓN: En estos días, la actividad debe ser PRÁCTICA/LABORAL relacionada con este P.S.P.
                            """
                            st.toast(f"✅ Proyectos detectados: PA ({dias_pa}) / PSP ({dias_psp})")
                except: pass

                # --- B. DETECCIÓN DE PENSUM ACTIVO (BLOQUE TEMÁTICO) ---
                texto_pensum = ""
                try:
                    df_bib = conn.read(spreadsheet=URL_HOJA, worksheet="BIBLIOTECA_PENSUMS", ttl=0)
                    # Filtra solo el que tenga ESTADO = ACTIVO
                    pensum_act = df_bib[(df_bib['USUARIO'] == st.session_state.u['NOMBRE']) & (df_bib['ESTADO'] == "ACTIVO")]
                    
                    if not pensum_act.empty:
                        fila_pen = pensum_act.iloc[0]
                        nombre_bloque = fila_pen.get('BLOQUE_ACTUAL', "General")
                        full_txt = fila_pen['CONTENIDO_FULL']
                        
                        # Extraer contenido del bloque
                        inicio = full_txt.find(nombre_bloque)
                        if inicio != -1:
                            fin = full_txt.find("BLOQUE:", inicio + 20)
                            contenido_bloque = full_txt[inicio:fin] if fin != -1 else full_txt[inicio:]
                            
                            texto_pensum = f"""
                            💎 **INSUMO TÉCNICO (PENSUM ACTIVO DETECTADO):**
                            BLOQUE ACTIVO: "{nombre_bloque}"
                            CONTENIDO CURRICULAR:
                            {contenido_bloque}
                            
                            INSTRUCCIÓN: Usa este contenido técnico para redactar las "Competencias Técnicas" y el desarrollo de las clases.
                            """
                            st.toast(f"✅ Pensum detectado: {nombre_bloque}")
                except: pass

                # --- C. CONSTRUCCIÓN DEL PROMPT FINAL ---
                
                # 1. Llamar al Cerebro Especialista (TEL, CAIPA, etc.)
                instrucciones_sistema = seleccionar_cerebro_modalidad(modalidad)
                
                # 2. Armar el Prompt con toda la data automática
                prompt_usuario = f"""
                CONTEXTO: {modalidad} {aula_especifica}.
                LAPSO: {rango}.
                TEMA: {notas}.
                ALUMNO: {perfil_alumno if is_pei else "Grupo General"}.
                
                {texto_proyectos}
                
                {texto_pensum}
                
                GENERA UNA PLANIFICACIÓN SEMANAL (Lunes a Viernes).
                
                REGLAS DE REDACCIÓN OBLIGATORIAS:
                1. COMPETENCIA TÉCNICA: Verbo (Infinitivo) + Objeto + Condición.
                2. ESTRATEGIAS: Solo menciona el nombre (Ej: Lluvia de ideas). NO expliques.
                3. INICIOS: No repitas el mismo verbo dos días seguidos.
                4. FORMATO: Usa Negritas y saltos de línea.
                
                ESTRUCTURA DE SALIDA (Repetir para cada día):
                ### [DÍA Y FECHA]
                **1. TÍTULO DE LA ACTIVIDAD:** (Corto y motivador)
                **2. COMPETENCIA TÉCNICA:** (Verbo Infinitivo + Qué + Para qué)
                **3. EXPLORACIÓN (Inicio):** [Verbo 1ra persona plural + Actividad]
                **4. DESARROLLO (Proceso):** [Actividad Vivencial Práctica]
                **5. REFLEXIÓN (Cierre):** [Sistematización]
                **6. ESTRATEGIAS:** [LISTADO CONCRETO SIN EXPLICACIÓN]
                **7. RECURSOS:** [Materiales]
                _______________________
                """
                
                # 3. Generar
                respuesta_raw = generar_respuesta([
                    {"role": "system", "content": instrucciones_sistema},
                    {"role": "user", "content": prompt_usuario}
                ], 0.7)
                
                # Formateo
                st.session_state.plan_actual = respuesta_raw \
                    .replace("**1.", "\n\n**1.") \
                    .replace("**2.", "\n\n**2.") \
                    .replace("**3.", "\n\n**3.") \
                    .replace("**4.", "\n\n**4.") \
                    .replace("**5.", "\n\n**5.") \
                    .replace("**6.", "\n\n**6.") \
                    .replace("**7.", "\n\n**7.") \
                    .replace("### ", "\n\n\n### ")
                
                st.rerun()

    # -------------------------------------------------------------------------
    # 3. VISUALIZACIÓN Y GUARDADO
    # -------------------------------------------------------------------------
    if 'plan_actual' in st.session_state and st.session_state.plan_actual:
        st.divider()
        st.success("✅ **Planificación Generada Exitosamente**")
        
        st.markdown(f"""
        <div style="border: 1px solid #ddd; padding: 25px; border-radius: 10px; background-color: #fcfcfc; line-height: 1.8;">
            {st.session_state.plan_actual}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        col_guardar, col_borrar = st.columns([1, 1])
        with col_guardar:
            if st.button("💾 Guardar en Mi Archivo", key="btn_guardar_final"):
                try:
                    with st.spinner("Guardando..."):
                        df_historia = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                        tema_guardar = st.session_state.get('temp_tema', notas)
                        nuevo_registro = pd.DataFrame([{
                            "FECHA": ahora_ve().strftime("%d/%m/%Y"), 
                            "USUARIO": st.session_state.u['NOMBRE'], 
                            "TEMA": tema_guardar[:50] + "...", 
                            "CONTENIDO": st.session_state.plan_actual, 
                            "ESTADO": "GUARDADO", 
                            "HORA_INICIO": "--", "HORA_FIN": "--"
                        }])
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=pd.concat([df_historia, nuevo_registro], ignore_index=True))
                        st.success("¡Guardado!")
                        time.sleep(1.5)
                        st.session_state.plan_actual = ""
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

        with col_borrar:
            if st.button("🗑️ Descartar", type="secondary", key="btn_descartar"):
                st.session_state.plan_actual = ""
                st.rerun()
