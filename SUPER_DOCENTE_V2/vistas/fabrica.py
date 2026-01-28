import streamlit as st
import pandas as pd
import time
from utils.comunes import ahora_ve
from cerebros.nucleo import generar_respuesta

def render_fabrica(conn):
    # --- CONFIGURACIÓN INICIAL ---
    st.header("🏗️ Fábrica de Diseño Instruccional (TEL ERAC)")
    st.markdown("Generador estandarizado de currículo y gestión de activación por Bloques.")

    # URL de la hoja para guardar en Biblioteca
    try:
        URL_HOJA = st.secrets["GSHEETS_URL"]
    except:
        st.error("Error de configuración de secretos.")
        return

    # --- MEMORIA TEMPORAL (SESSION STATE) ---
    if 'fp_fase1' not in st.session_state: st.session_state.fp_fase1 = ""
    if 'fp_fase2' not in st.session_state: st.session_state.fp_fase2 = ""
    if 'fp_fase3' not in st.session_state: st.session_state.fp_fase3 = ""
    if 'fp_completo' not in st.session_state: st.session_state.fp_completo = ""
    
    # Estado del Visor de Lectura
    if 'visor_activo' not in st.session_state: st.session_state.visor_activo = False
    if 'visor_data' not in st.session_state: st.session_state.visor_data = {}

    # --- PESTAÑAS PRINCIPALES ---
    tab_fabrica, tab_biblioteca = st.tabs(["🏭 Línea de Producción (Crear)", "📚 Biblioteca y Configuración"])

    # =====================================================================
    # PESTAÑA 1: LA FÁBRICA (CREACIÓN DE PENSUMS)
    # =====================================================================
    with tab_fabrica:
        st.subheader("1. Ficha Técnica")
        c1, c2 = st.columns(2)
        with c1:
            especialidad = st.text_input("Especialidad a Crear:", placeholder="Ej: Educación Musical")
        with c2:
            docente_resp = st.text_input("Docente Responsable:", value=st.session_state.u['NOMBRE'])
        
        contexto_extra = st.text_area("Recursos y Enfoque (Clave para la adaptación):", 
                                    placeholder="Ej: Tenemos instrumentos de percusión, queremos formar una banda, no hay electricidad...")
        
        st.divider()

        # --- FASE 1: FUNDAMENTACIÓN ---
        st.markdown("### 🔹 Fase 1: Fundamentación Institucional")
        if st.button("Generar Fase 1 (Fundamentación)", type="primary"):
            if especialidad:
                with st.spinner("Redactando bases (Contexto TEL ERAC)..."):
                    prompt_f1 = f"""
                    ACTÚA COMO COORDINADOR DEL TEL ERAC (ZULIA).
                    REDACTA LA "FUNDAMENTACIÓN Y METAS" PARA EL PENSUM DE: {especialidad}.
                    CONTEXTO: "{contexto_extra}".
                    ESTRUCTURA OBLIGATORIA:
                    1. Encabezado Oficial: República Bolivariana... TEL ERAC.
                    2. PEIC VIGENTE: "Una escuela sustentable...". Vértice 5.
                    3. JUSTIFICACIÓN: Adaptada a {especialidad}.
                    4. METAS: Independencia laboral, Resiliencia, Autoestima.
                    5. LIMITACIONES (ZULIA): Fallas eléctricas, transporte, economía multimoneda.
                    REGLA DE ORO: NO ESCRIBAS NINGUNA CONCLUSIÓN O DESPEDIDA.
                    """
                    # Nota: generar_respuesta ya inyecta tu identidad de Super Docente, así que solo pasamos el prompt de usuario.
                    st.session_state.fp_fase1 = generar_respuesta([{"role":"user","content":prompt_f1}], 0.7)
            else: st.error("Falta el nombre de la especialidad.")
        
        if st.session_state.fp_fase1:
            st.session_state.fp_fase1 = st.text_area("Edición Fase 1:", value=st.session_state.fp_fase1, height=200)

        # --- FASE 2: TEMARIO ---
        st.markdown("### 🔹 Fase 2: Temario y Contenidos")
        st.info("La IA generará listas de conceptos (Temario) para que el Planificador tenga material.")
        
        if st.button("Generar Fase 2 (Temario)", type="primary"):
            if st.session_state.fp_fase1:
                with st.spinner("Diseñando Estructura de Temas..."):
                    prompt_f2 = f"""
                    CONTEXTO: {especialidad}. RECURSOS: {contexto_extra}.
                    TAREA: DISEÑA LOS BLOQUES DE CONTENIDO (TEMARIO).
                    IMPORTANTE: NO GENERES ACTIVIDADES ESPECÍFICAS. GENERA LISTAS DE CONCEPTOS.
                    FORMATO DE NUMERACIÓN ESTRICTO: "1. BLOQUE: [NOMBRE]"
                    
                    ORDEN EXACTO SUGERIDO:
                    1. BLOQUE: INTRODUCCIÓN A {especialidad}
                    2. BLOQUE: ATENCIÓN AL PÚBLICO
                    3. BLOQUE: [TEMA TÉCNICO BÁSICO]
                    4. BLOQUE: SEGURIDAD E HIGIENE
                    5. BLOQUE: [TEMA TÉCNICO INTERMEDIO]
                    6. BLOQUE: SERVICIOS Y TRÁMITES
                    7. BLOQUE: [TEMA TÉCNICO AVANZADO]
                    8. BLOQUE: IDENTIDAD Y TIEMPO
                    9. BLOQUE: PROYECTO DE VIDA
                    10. BLOQUE: TECNOLOGÍA
                    11. BLOQUE: CONO MONETARIO
                    12. BLOQUE: SALUD INTEGRAL
                    13. BLOQUE: P.S.P. (Producto Final)
                    14. BLOQUE: MERCADEO Y VENTAS
                    NO AGREGUES CONCLUSIONES.
                    """
                    st.session_state.fp_fase2 = generar_respuesta([{"role":"user","content":prompt_f2}], 0.7)
            else: st.error("Genera la Fase 1 primero.")

        if st.session_state.fp_fase2:
            st.session_state.fp_fase2 = st.text_area("Edición Fase 2:", value=st.session_state.fp_fase2, height=300)

        # --- FASE 3: ESTRATEGIAS ---
        st.markdown("### 🔹 Fase 3: Estrategias y Evaluación")
        if st.button("Generar Fase 3 (Metodología)", type="primary"):
            if st.session_state.fp_fase2:
                with st.spinner("Creando metodología..."):
                    prompt_f3 = f"""
                    PARA EL PENSUM DE: {especialidad}.
                    GENERA: ESTRATEGIAS, RECURSOS Y EVALUACIÓN.
                    NO HAGAS CONCLUSIONES.
                    - ESTRATEGIAS: Vivenciales.
                    - RECURSOS: "{contexto_extra}", materiales de provecho.
                    - EVALUACIÓN: Lista de Cotejo, Observación.
                    """
                    st.session_state.fp_fase3 = generar_respuesta([{"role":"user","content":prompt_f3}], 0.6)
            else: st.error("Genera la Fase 2 primero.")

        if st.session_state.fp_fase3:
            st.session_state.fp_fase3 = st.text_area("Edición Fase 3:", value=st.session_state.fp_fase3, height=200)

        st.divider()

        # --- CONSOLIDACIÓN ---
        st.markdown("### 🔗 Consolidación Final")
        if st.button("🔗 UNIR TODO EL DOCUMENTO", type="primary", use_container_width=True):
            if st.session_state.fp_fase1 and st.session_state.fp_fase2 and st.session_state.fp_fase3:
                st.session_state.fp_completo = f"""
================================================================
DISEÑO INSTRUCCIONAL: {especialidad.upper()}
INSTITUCIÓN: TEL ELENA ROSA ARANGUREN DE CASTELLANO (ERAC)
DOCENTE RESPONSABLE: {docente_resp}
FECHA: {ahora_ve().strftime("%d/%m/%Y")}
================================================================

{st.session_state.fp_fase1}

----------------------------------------------------------------
MALLA CURRICULAR Y TEMARIO (CONTENIDOS)
----------------------------------------------------------------
{st.session_state.fp_fase2}

----------------------------------------------------------------
ESTRATEGIAS METODOLÓGICAS Y EVALUACIÓN
----------------------------------------------------------------
{st.session_state.fp_fase3}
                """
                st.success("✅ Documento Unificado.")
            else:
                st.error("Faltan fases.")

        if st.session_state.fp_completo:
            st.markdown("#### 📄 Vista Previa y Guardado")
            st.session_state.fp_completo = st.text_area("Documento Maestro (Editable):", 
                                                      value=st.session_state.fp_completo, height=400)
            
            c_save, c_down = st.columns(2)
            with c_save:
                if st.button("💾 Guardar en Biblioteca"):
                    try:
                        # Intentamos leer la hoja BIBLIOTECA_PENSUMS
                        try:
                            df_lib = conn.read(spreadsheet=URL_HOJA, worksheet="BIBLIOTECA_PENSUMS", ttl=0)
                        except:
                            # Si no existe, creamos la estructura en memoria (Pandas)
                            df_lib = pd.DataFrame(columns=["FECHA", "USUARIO", "TITULO_PENSUM", "CONTENIDO_FULL", "ESTADO", "DIAS", "BLOQUE_ACTUAL"])

                        nuevo_pen = pd.DataFrame([{
                            "FECHA": ahora_ve().strftime("%d/%m/%Y"),
                            "USUARIO": st.session_state.u['NOMBRE'],
                            "TITULO_PENSUM": especialidad,
                            "CONTENIDO_FULL": st.session_state.fp_completo,
                            "ESTADO": "INACTIVO", 
                            "DIAS": "",
                            "BLOQUE_ACTUAL": "1. BLOQUE: INTRODUCCIÓN" # Valor inicial por defecto
                        }])
                        
                        conn.update(spreadsheet=URL_HOJA, worksheet="BIBLIOTECA_PENSUMS", data=pd.concat([df_lib, nuevo_pen], ignore_index=True))
                        st.balloons()
                        st.success("Guardado en la Nube.")
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")

            with c_down:
                st.download_button("📥 Descargar Archivo (.txt)", data=st.session_state.fp_completo, file_name=f"PENSUM_{especialidad}_ERAC.txt")

    # =====================================================================
    # PESTAÑA 2: BIBLIOTECA (GESTIÓN + VISOR + SELECTOR DE BLOQUE)
    # =====================================================================
    with tab_biblioteca:
        
        # ESCENARIO A: MODO LECTURA ACTIVADO (Visor Pantalla Completa)
        if st.session_state.visor_activo:
            data = st.session_state.visor_data
            
            c_vol, c_tit = st.columns([1, 6])
            with c_vol:
                if st.button("🔙 SALIR", use_container_width=True):
                    st.session_state.visor_activo = False
                    st.rerun()
            with c_tit:
                st.subheader(f"📖 Leyendo: {data['TITULO_PENSUM']}")
            
            st.divider()
            st.text_area("Documento Maestro:", value=data['CONTENIDO_FULL'], height=600)

        # ESCENARIO B: GESTIÓN DE TARJETAS (SELECTOR DE BLOQUES)
        else:
            st.subheader("📚 Gestión de Pensums y Bloques")
            try:
                df_biblio = conn.read(spreadsheet=URL_HOJA, worksheet="BIBLIOTECA_PENSUMS", ttl=0)
                mis_p = df_biblio[df_biblio['USUARIO'] == st.session_state.u['NOMBRE']]
                
                if mis_p.empty:
                    st.info("No tienes pensums registrados.")
                else:
                    for i, row in mis_p.iterrows():
                        # Variables Actuales
                        estado_actual = row['ESTADO']
                        es_activo = (estado_actual == "ACTIVO")
                        
                        # Recuperar Bloque Actual (NUEVO - REGLA DE ORO)
                        bloque_guardado = "1. BLOQUE: INTRODUCCIÓN"
                        if "BLOQUE_ACTUAL" in row and pd.notna(row['BLOQUE_ACTUAL']) and row['BLOQUE_ACTUAL'] != "":
                            bloque_guardado = row['BLOQUE_ACTUAL']

                        # --- MAGIA: DETECTAR LOS BLOQUES DEL TEXTO ---
                        texto_full = row['CONTENIDO_FULL']
                        lista_bloques_detectados = []
                        for linea in texto_full.split('\n'):
                            if "BLOQUE:" in linea.upper():
                                lista_bloques_detectados.append(linea.strip())
                        
                        if not lista_bloques_detectados:
                            lista_bloques_detectados = ["1. BLOQUE: GENERAL (No detectados)"]

                        # Tarjeta Visual
                        titulo_card = f"🟢 {row['TITULO_PENSUM']}" if es_activo else f"⚪ {row['TITULO_PENSUM']} (Inactivo)"
                        
                        with st.expander(titulo_card):
                            st.caption(f"Fecha: {row['FECHA']}")
                            
                            # 1. BOTÓN LECTURA
                            if st.button(f"📖 CONSULTAR DOCUMENTO", key=f"read_{i}", use_container_width=True):
                                st.session_state.visor_activo = True
                                st.session_state.visor_data = row
                                st.rerun()
                            
                            st.divider()
                            
                            # 2. CONFIGURACIÓN COMPLETA
                            c_conf, c_del = st.columns([3, 1])
                            
                            with c_conf:
                                st.markdown("##### ⚙️ Configuración")
                                
                                # A. INTERRUPTOR ACTIVAR
                                nuevo_estado_bool = st.toggle("Activar este Pensum", value=es_activo, key=f"tog_{i}")
                                
                                if nuevo_estado_bool:
                                    # B. SELECTOR DE BLOQUE (¿Qué tema toca?)
                                    st.info("📌 **¿En qué Bloque estás trabajando?**")
                                    
                                    # Encontrar índice del bloque guardado
                                    idx_bloque = 0
                                    if bloque_guardado in lista_bloques_detectados:
                                        idx_bloque = lista_bloques_detectados.index(bloque_guardado)
                                    
                                    seleccion_bloque = st.selectbox(
                                        "Selecciona el Bloque Actual:",
                                        lista_bloques_detectados,
                                        index=idx_bloque,
                                        key=f"sb_bloq_{i}",
                                        help="Esto define qué contenido verá el Planificador."
                                    )
                                else:
                                    seleccion_bloque = ""
                                
                                # BOTÓN GUARDAR
                                if st.button("💾 Guardar Cambios", key=f"upd_{i}"):
                                    try:
                                        df_biblio.at[i, 'ESTADO'] = "ACTIVO" if nuevo_estado_bool else "INACTIVO"
                                        df_biblio.at[i, 'BLOQUE_ACTUAL'] = seleccion_bloque 
                                        
                                        conn.update(spreadsheet=URL_HOJA, worksheet="BIBLIOTECA_PENSUMS", data=df_biblio)
                                        st.toast(f"✅ Guardado: {seleccion_bloque}")
                                        time.sleep(1)
                                        st.rerun()
                                    except Exception as e: st.error(f"Error guardando: {e}")

                            with c_del:
                                st.write("")
                                if st.button("🗑️", key=f"del_{i}"):
                                    df_new = df_biblio.drop(i)
                                    conn.update(spreadsheet=URL_HOJA, worksheet="BIBLIOTECA_PENSUMS", data=df_new)
                                    st.rerun()

            except Exception as e:
                st.warning(f"Error cargando biblioteca: {e}")
