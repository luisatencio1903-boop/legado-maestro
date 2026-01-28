import streamlit as st
import pandas as pd
import time
import re
from utils.comunes import ahora_ve
from utils.drive_api import subir_a_imgbb
from cerebros.nucleo import generar_respuesta

def render_aula(conn):
    # Recuperamos la URL para las conexiones internas
    try:
        URL_HOJA = st.secrets["GSHEETS_URL"]
    except:
        st.error("Error de configuración: No se encontró GSHEETS_URL.")
        return

    # -------------------------------------------------------------------------
    # GESTIÓN DE MEMORIA (CACHÉ / FOTOCOPIAS) - RESTAURADO ORIGINAL
    # -------------------------------------------------------------------------
    # Inicializamos los espacios de memoria si están vacíos
    if 'cache_planes' not in st.session_state: st.session_state.cache_planes = None
    if 'cache_evaluaciones' not in st.session_state: st.session_state.cache_evaluaciones = None
    if 'cache_ejecucion' not in st.session_state: st.session_state.cache_ejecucion = None
    if 'cache_matricula' not in st.session_state: st.session_state.cache_matricula = None
    
    # Variables de estado originales (V13)
    if 'modo_suplencia_activo' not in st.session_state: st.session_state.modo_suplencia_activo = False
    if 'av_titulo_hoy' not in st.session_state: st.session_state.av_titulo_hoy = ""
    if 'av_contexto_hoy' not in st.session_state: st.session_state.av_contexto_hoy = ""
    if 'temp_propuesta_ia' not in st.session_state: st.session_state.temp_propuesta_ia = ""
    
    # Variables para fotos (V13)
    if 'av_foto1' not in st.session_state: st.session_state.av_foto1 = None
    if 'av_foto2' not in st.session_state: st.session_state.av_foto2 = None
    if 'av_foto3' not in st.session_state: st.session_state.av_foto3 = None
    if 'av_resumen' not in st.session_state: st.session_state.av_resumen = ""
    
    # Variable para el Chat Asistente (NUEVO)
    if 'chat_asistente_aula' not in st.session_state: st.session_state.chat_asistente_aula = []

    # --- FUNCIÓN DE SINCRONIZACIÓN (IR A DIRECCIÓN) ---
    def sincronizar_aula():
        try:
            with st.spinner("🔄 Actualizando datos desde Dirección (Google)..."):
                # Usamos ttl=0 para forzar descarga real
                st.session_state.cache_planes = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                st.session_state.cache_evaluaciones = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                st.session_state.cache_ejecucion = conn.read(spreadsheet=URL_HOJA, worksheet="EJECUCION", ttl=0)
                st.session_state.cache_matricula = conn.read(spreadsheet=URL_HOJA, worksheet="MATRICULA_GLOBAL", ttl=0) 
            st.success("✅ Datos actualizados en memoria.")
            time.sleep(0.5)
        except Exception as e: st.error(f"Error sincronizando: {e}")

    # Auto-carga inicial
    if st.session_state.cache_planes is None or st.session_state.cache_matricula is None:
        sincronizar_aula()
        st.rerun()

    # --- ENCABEZADO Y CONTEXTO ---
    c_head, c_btn = st.columns([3, 1])
    with c_head:
        st.info("💡 **Centro de Operaciones:** Gestión de la clase (Inicio - Desarrollo - Cierre).")
    with c_btn:
        if st.button("🔄 RECARGAR DATOS"):
            sincronizar_aula()
            st.rerun()

    st.markdown("### ⚙️ Contexto de la Clase")
    es_suplencia = st.checkbox("🦸 **Activar Modo Suplencia**", 
                                value=st.session_state.modo_suplencia_activo,
                                key="chk_suplencia_master")
    st.session_state.modo_suplencia_activo = es_suplencia
    
    # Determinar lista de docentes para suplencia usando CACHÉ
    try:
        if st.session_state.cache_matricula is not None and not st.session_state.cache_matricula.empty:
            if 'DOCENTE_TITULAR' in st.session_state.cache_matricula.columns:
                lista_docentes_real = sorted(st.session_state.cache_matricula['DOCENTE_TITULAR'].dropna().unique().tolist())
            else: lista_docentes_real = [st.session_state.u['NOMBRE']]
        else: lista_docentes_real = [st.session_state.u['NOMBRE']]
    except: lista_docentes_real = [st.session_state.u['NOMBRE']]

    if es_suplencia:
        lista_suplentes = [d for d in lista_docentes_real if d != st.session_state.u['NOMBRE']]
        if not lista_suplentes: lista_suplentes = ["No hay otros docentes"]
        titular = st.selectbox("Seleccione Docente Titular:", lista_suplentes, key="av_titular_v13")
        st.warning(f"Modo Suplencia: Usando planificación y alumnos de **{titular}**")
    else:
        titular = st.session_state.u['NOMBRE']
        st.success(f"Trabajando con tu planificación y alumnos ({titular}).")

    # --- 2. BUSCAR PLAN ACTIVO (USANDO CACHÉ) ---
    pa = None
    try:
        df_planes = st.session_state.cache_planes
        plan_activo = df_planes[
            (df_planes['USUARIO'] == titular) & 
            (df_planes['ESTADO'] == "ACTIVO")
        ]
        if not plan_activo.empty:
            fila = plan_activo.iloc[0]
            pa = {"CONTENIDO_PLAN": fila['CONTENIDO'], "RANGO": fila.get('FECHA', 'S/F')}
    except: pass

    if not pa:
        st.error(f"🚨 {titular} no tiene un plan activo. Ve a Archivo Pedagógico y activa uno.")
        return # Detener ejecución si no hay plan

    # --- 3. PESTAÑAS (TRÍADA PEDAGÓGICA) ---
    tab1, tab2, tab3 = st.tabs(["🚀 Ejecución (Inicio/Desarrollo)", "📝 Evaluación", "🏁 Cierre (Reflexión)"])

    # =====================================================================
    # PESTAÑA 1: EJECUCIÓN + ASISTENTE IA + CÁMARAS SECUENCIALES
    # =====================================================================
    with tab1:
        dias_es = {"Monday":"Lunes", "Tuesday":"Martes", "Wednesday":"Miércoles", "Thursday":"Jueves", "Friday":"Viernes", "Saturday":"Sábado", "Sunday":"Domingo"}
        dia_hoy_nombre = dias_es.get(ahora_ve().strftime("%A"))
        
        patron = f"(?i)(###|\*\*)\s*{dia_hoy_nombre}.*?(?=(###|\*\*)\s*(Lunes|Martes|Miércoles|Jueves|Viernes)|$)"
        match = re.search(patron, pa["CONTENIDO_PLAN"], re.DOTALL)
        clase_dia = match.group(0) if match else None

        if clase_dia is None:
            st.warning(f"No hay actividad programada para hoy {dia_hoy_nombre}.")
            dia_m = st.selectbox("Seleccione día a ejecutar:", ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"], key="av_manual_v13")
            patron_m = f"(?i)(###|\*\*)\s*{dia_m}.*?(?=(###|\*\*)\s*(Lunes|Martes|Miércoles|Jueves|Viernes)|$)"
            match_m = re.search(patron_m, pa["CONTENIDO_PLAN"], re.DOTALL)
            clase_de_hoy = match_m.group(0) if match_m else "Sin actividad."
        else:
            clase_de_hoy = clase_dia

        st.subheader("📖 Guía de la Actividad")
        if clase_de_hoy:
            st.markdown(f'<div class="plan-box">{clase_de_hoy}</div>', unsafe_allow_html=True)
            
            # Extracción de contexto para evaluación (V13 Logic)
            try:
                lineas = clase_de_hoy.split('\n')
                t_temp = "Actividad del Día"
                c_temp = "Sin contexto."
                for linea in lineas:
                    if "**1." in linea:
                        parte_sucia = linea.split(":")[1] if ":" in linea else linea
                        t_temp = parte_sucia.replace("**", "").strip()
                    if "**4." in linea:
                        texto_sucio = linea.replace("**4. DESARROLLO (Proceso):**", "")
                        c_temp = texto_sucio[:250].strip() 
                st.session_state.temp_titulo_extract = t_temp
                st.session_state.temp_contexto_extract = c_temp
            except:
                st.session_state.temp_titulo_extract = "Actividad General"
                st.session_state.temp_contexto_extract = clase_de_hoy[:150]
        
        # --- NUEVO: ASISTENTE IA (INTEGRADO AQUÍ) ---
        with st.expander("🤖 Consultar al Asistente Pedagógico (IA)", expanded=False):
            st.caption("Pregunta sobre dinámicas, adaptaciones o dudas de esta clase.")
            pregunta_docente = st.text_input("Tu pregunta:", key="chat_input_aula")
            if st.button("Consultar IA", key="btn_chat_aula"):
                if pregunta_docente:
                    with st.spinner("Pensando..."):
                        prompt = f"CONTEXTO CLASE: {clase_de_hoy}. PREGUNTA DOCENTE: {pregunta_docente}. DAME UNA RESPUESTA BREVE Y PRÁCTICA."
                        resp = generar_respuesta([{"role":"user","content":prompt}], 0.7)
                        st.session_state.chat_asistente_aula.append({"user": pregunta_docente, "ia": resp})
            
            for msg in reversed(st.session_state.chat_asistente_aula[-2:]):
                st.markdown(f"**Tú:** {msg['user']}")
                st.info(f"**IA:** {msg['ia']}")

        st.divider()
        
        # --- PEI EXPRESS (MOVIDO ARRIBA DE LAS CÁMARAS) ---
        with st.expander("🧩 Adaptación P.E.I. Express (Planificar antes de ejecutar)"):
            try:
                df_mat = st.session_state.cache_matricula
                alums = df_mat[df_mat['DOCENTE_TITULAR'] == titular]['NOMBRE_ALUMNO'].dropna().unique().tolist()
            except: alums = []
            
            c1, c2 = st.columns(2)
            with c1: al_a = st.selectbox("Alumno:", ["(Seleccionar)"] + sorted(alums), key="av_pei_al_v13")
            with c2: ctx_a = st.text_input("Situación:", placeholder="Ej: Crisis sensorial...", key="av_pei_ctx_v13")
            
            if st.button("💡 Estrategia IA", key="btn_av_ia_v13"):
                if al_a != "(Seleccionar)":
                    p_pei = f"PLAN: {clase_de_hoy}. ALUMNO: {al_a}. SITUACIÓN: {ctx_a}. Dame estrategia rápida."
                    st.markdown(f'<div class="eval-box">{generar_respuesta([{"role":"user","content":p_pei}], 0.7)}</div>', unsafe_allow_html=True)
        
        st.divider()

        # --- CÁMARAS SECUENCIALES (BLOQUEO PARA NO COLAPSAR) ---
        col_momento1, col_momento2 = st.columns(2)
        
        # FOTO 1: INICIO (Siempre activa)
        with col_momento1:
            st.markdown("#### 1. Inicio")
            if st.session_state.av_foto1 is None:
                f1 = st.camera_input("Capturar Inicio", key="av_cam1_v13")
                if f1 and st.button("📤 Subir Inicio", key="btn_save_f1_v13"):
                    u1 = subir_a_imgbb(f1)
                    if u1: st.session_state.av_foto1 = u1; st.rerun()
            else:
                st.image(st.session_state.av_foto1, use_container_width=True, caption="✅ Inicio")
                if st.button("♻️ Reset Inicio", key="reset_f1_v13"): st.session_state.av_foto1 = None; st.rerun()

        # FOTO 2: DESARROLLO (Bloqueada hasta tener Foto 1)
        with col_momento2:
            st.markdown("#### 2. Desarrollo")
            if st.session_state.av_foto1 is None:
                st.info("🔒 **Cámara Bloqueada**")
                st.caption("Complete la evidencia de **Inicio** para desbloquear.")
            else:
                if st.session_state.av_foto2 is None:
                    f2 = st.camera_input("Capturar Desarrollo", key="av_cam2_v13")
                    if f2 and st.button("📤 Subir Desarrollo", key="btn_save_f2_v13"):
                        u2 = subir_a_imgbb(f2)
                        if u2: st.session_state.av_foto2 = u2; st.rerun()
                else:
                    st.image(st.session_state.av_foto2, use_container_width=True, caption="✅ Desarrollo")
                    if st.button("♻️ Reset Desarr.", key="reset_f2_v13"): st.session_state.av_foto2 = None; st.rerun()

    # =====================================================================
    # PESTAÑA 2: EVALUACIÓN (V13 + CACHÉ + MATRÍCULA CORRECTA)
    # =====================================================================
    with tab2:
        st.subheader("📝 Evaluación Individual")
        try:
            df_mat = st.session_state.cache_matricula
            alums = df_mat[df_mat['DOCENTE_TITULAR'] == titular]['NOMBRE_ALUMNO'].dropna().unique().tolist()
        except: alums = []
        
        if not alums:
            st.warning(f"No se encontraron alumnos para **{titular}** en 'MATRICULA_GLOBAL'.")
        else:
            e_sel = st.selectbox("Estudiante:", sorted(alums), key="av_eval_al_v13")
            
            if st.button("🔍 Cargar Datos de Hoy", key="btn_load_act_v13"):
                st.session_state.av_titulo_hoy = st.session_state.get('temp_titulo_extract', 'Actividad Manual')
                st.session_state.av_contexto_hoy = st.session_state.get('temp_contexto_extract', 'Sin contexto.')
                st.session_state.temp_propuesta_ia = ""
                st.rerun()
            
            st.caption(f"Actividad: {st.session_state.av_titulo_hoy}")
            o_eval = st.text_area("Observación Anecdótica:", placeholder="¿Qué logró hoy?", key="av_eval_obs_v13")
            
            if o_eval and st.button("✨ Mejorar Redacción (IA)", key="btn_sugerir_ia_v13"):
                with st.spinner("Redactando..."):
                    p_ev = f"Alumno: {e_sel}. Obs: {o_eval}. Contexto: {st.session_state.av_contexto_hoy}. Mejora redacción pedagógica."
                    st.session_state.temp_propuesta_ia = generar_respuesta([{"role":"user","content":p_ev}], 0.5)
            
            if st.session_state.temp_propuesta_ia:
                st.info("Propuesta IA:")
                st.write(st.session_state.temp_propuesta_ia)

            if st.button("💾 Guardar Nota", type="primary", key="btn_save_final_v13"):
                if o_eval and st.session_state.av_titulo_hoy:
                    nota_final = st.session_state.temp_propuesta_ia if st.session_state.temp_propuesta_ia else o_eval
                    
                    try:
                        # 1. Guardar en NUBE (EVALUACIONES)
                        nueva_n = pd.DataFrame([{
                            "FECHA": ahora_ve().strftime("%d/%m/%Y"), 
                            "USUARIO": st.session_state.u['NOMBRE'], 
                            "DOCENTE_TITULAR": titular, 
                            "ESTUDIANTE": e_sel, 
                            "ACTIVIDAD": st.session_state.av_titulo_hoy, 
                            "ANECDOTA": o_eval, 
                            "EVALUACION_IA": nota_final, # Regla de Oro: Tu columna
                            "PLANIFICACION_ACTIVA": pa['RANGO']
                        }])
                        df_ev = conn.read(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", ttl=0)
                        conn.update(spreadsheet=URL_HOJA, worksheet="EVALUACIONES", data=pd.concat([df_ev, nueva_n], ignore_index=True))
                        
                        # 2. Guardar en CACHÉ
                        if st.session_state.cache_evaluaciones is not None:
                            st.session_state.cache_evaluaciones = pd.concat([st.session_state.cache_evaluaciones, nueva_n], ignore_index=True)

                        st.success("✅ Nota Guardada")
                        st.session_state.temp_propuesta_ia = ""
                        time.sleep(1); st.rerun()
                    except Exception as e: st.error(f"Error guardando: {e}")
                else: st.error("Faltan datos.")

    # =====================================================================
    # PESTAÑA 3: CIERRE (FOTO 3 BLOQUEADA + CONSOLIDACIÓN)
    # =====================================================================
    with tab3:
        st.subheader("🏁 Cierre de Jornada")
        
        # Verificación en CACHÉ
        try:
            hoy_check = ahora_ve().strftime("%d/%m/%Y")
            df_check = st.session_state.cache_ejecucion
            ya_cerro = not df_check[(df_check['USUARIO'] == st.session_state.u['NOMBRE']) & (df_check['FECHA'] == hoy_check)].empty
        except: ya_cerro = False
        
        if ya_cerro:
            st.success("✅ Jornada de hoy ya consolidada.")
            if st.button("🏠 Volver"): st.session_state.pagina_actual = "HOME"; st.rerun()
        else:
            st.markdown("#### 3. Evidencia de Cierre")
            # BLOQUEO DE CÁMARA 3: Requiere Desarrollo listo
            if st.session_state.av_foto2 is None:
                 st.info("🔒 **Cámara Bloqueada**")
                 st.caption("Complete la evidencia de **Desarrollo** para habilitar el Cierre.")
            else:
                if st.session_state.av_foto3 is None:
                    f3 = st.camera_input("Capturar Cierre", key="av_cam3_v13")
                    if f3 and st.button("📤 Subir Cierre", key="btn_save_f3_v13"):
                        u3 = subir_a_imgbb(f3)
                        if u3: st.session_state.av_foto3 = u3; st.rerun()
                else:
                    st.image(st.session_state.av_foto3, width=200, caption="✅ Cierre")
                    if st.button("♻️ Reset Cierre", key="reset_f3_v13"): st.session_state.av_foto3 = None; st.rerun()

            st.divider()
            st.session_state.av_resumen = st.text_area("Resumen Pedagógico:", value=st.session_state.av_resumen, key="av_res_v13", height=100)
            
            if st.button("🚀 CONSOLIDAR JORNADA", type="primary", key="btn_fin_v13"):
                # Validación V13
                faltan = []
                if not st.session_state.av_foto1: faltan.append("Inicio")
                if not st.session_state.av_foto2: faltan.append("Desarrollo")
                if not st.session_state.av_foto3: faltan.append("Cierre")
                
                if faltan:
                    st.error(f"⚠️ Faltan evidencias: {', '.join(faltan)}")
                elif not st.session_state.av_resumen:
                    st.error("⚠️ Falta el resumen.")
                else:
                    with st.spinner("Guardando Bitácora..."):
                        try:
                            fotos_str = f"{st.session_state.av_foto1}|{st.session_state.av_foto2}|{st.session_state.av_foto3}"
                            nueva_f = pd.DataFrame([{
                                "FECHA": hoy_check, 
                                "USUARIO": st.session_state.u['NOMBRE'], 
                                "DOCENTE_TITULAR": titular, 
                                "ACTIVIDAD_TITULO": st.session_state.av_titulo_hoy or "General", 
                                "EVIDENCIA_FOTO": fotos_str, 
                                "RESUMEN_LOGROS": st.session_state.av_resumen, 
                                "ESTADO": "CULMINADA", 
                                "PUNTOS": 5
                            }])
                            
                            # 1. Guardar NUBE
                            df_ej = conn.read(spreadsheet=URL_HOJA, worksheet="EJECUCION", ttl=0)
                            conn.update(spreadsheet=URL_HOJA, worksheet="EJECUCION", data=pd.concat([df_ej, nueva_f], ignore_index=True))
                            
                            # 2. Guardar CACHÉ
                            if st.session_state.cache_ejecucion is not None:
                                st.session_state.cache_ejecucion = pd.concat([st.session_state.cache_ejecucion, nueva_f], ignore_index=True)
                            
                            # Limpieza
                            st.session_state.av_foto1 = None
                            st.session_state.av_foto2 = None
                            st.session_state.av_foto3 = None
                            st.session_state.av_resumen = ""
                            st.balloons()
                            st.success("✅ ¡Jornada Exitosa!")
                            time.sleep(2); st.session_state.pagina_actual = "HOME"; st.rerun()
                        except Exception as e: st.error(f"Error: {e}")
