import streamlit as st
import pandas as pd
import time
from utils.comunes import ahora_ve
# --- IMPORTACIONES PARA MEJORAS v7.5 (BIOMETRÍA Y RESILIENCIA) ---
from utils.drive_api import subir_a_imgbb
from cerebros.nucleo import generar_respuesta
from utils.maletin import persistir_en_dispositivo, recuperar_del_dispositivo
from utils.traductor import foto_a_texto

def render_asistencia(conn):
    st.title("⏱️ Control de Asistencia")
    st.info("Registro oficial de entrada y salida docente con verificación biométrica v7.5.")

    # --- 1. RELOJ VENEZUELA (Regla de Oro: Tu horario real preservado) ---
    hora_actual = ahora_ve()
    str_fecha = hora_actual.strftime("%d/%m/%Y")
    str_hora = hora_actual.strftime("%I:%M %p")
    h_actual_int = hora_actual.hour
    
    c1, c2 = st.columns(2)
    c1.metric("📅 Fecha", str_fecha)
    c2.metric("⌚ Hora", str_hora)
    st.divider()

    # --- 2. CONEXIÓN Y VERIFICACIÓN (MEJORADA CON FALLBACK AL MALETÍN) ---
    try:
        url = st.secrets["GSHEETS_URL"]
        # Intentamos leer de la nube
        df_asis = conn.read(spreadsheet=url, worksheet="ASISTENCIA", ttl=0)
        
        # Filtramos: Solo TÚ y solo HOY
        mi_registro = df_asis[
            (df_asis['USUARIO'] == st.session_state.u['NOMBRE']) & 
            (df_asis['FECHA'] == str_fecha)
        ]
    except Exception as e:
        # SI FALLA EL INTERNET: Intentamos recuperar del disco duro del móvil
        st.warning("⚠️ Sin conexión a la nube. Consultando Maletín de Campo...")
        reg_local = recuperar_del_dispositivo("maletin_asistencia")
        if reg_local and reg_local.get("FECHA") == str_fecha:
            mi_registro = pd.DataFrame([reg_local])
            st.info("📱 Registro recuperado localmente (Pendiente por subir).")
        else:
            mi_registro = pd.DataFrame()

    # --- FUNCIÓN INTERNA DE RESPALDO (v7.5) ---
    def respaldar_en_dispositivo(datos):
        persistir_en_dispositivo("maletin_asistencia", datos)

    # --- 3. LÓGICA DE BOTONES (ENTRADA VS SALIDA VS INASISTENCIA) ---
    
    if mi_registro.empty:
        # CASO A: NO HA LLEGADO -> MOSTRAR FLUJO DE ENTRADA
        status = st.radio("¿Cuál es tu estatus hoy?", ["✅ Asistí al Plantel", "❌ No Asistí"], index=0)

        if status == "✅ Asistí al Plantel":
            st.warning("⚠️ Aún no registras entrada hoy.")
            
            # --- MEJORA: DETECCIÓN DE ENTRADA TARDÍA ---
            es_tarde_entrada = h_actual_int > 8 or (h_actual_int == 8 and hora_actual.minute > 15)
            motivo_entrada = "Cumplimiento"
            
            if es_tarde_entrada:
                st.error("🚨 Registro fuera de horario (Después de las 8:15 AM)")
                incidencia_e = st.selectbox("Justifique el retraso en el registro:", [
                    "Sin inconvenientes (Llegada tardía)",
                    "Corte Eléctrico en la Institución/Sector",
                    "Sin señal de Datos Móviles / Internet",
                    "Problemas de Transporte / Gasolina",
                    "Otro"
                ])
                obs_manual = st.text_input("Novedades al llegar (Opcional):", placeholder="Explique brevemente...")
                motivo_entrada = f"INCIDENCIA: {incidencia_e} | {obs_manual}"
            else:
                motivo_entrada = st.text_input("Novedades al llegar (Opcional):", placeholder="Todo en orden...")

            # --- MEJORA: CÁMARA BIOMÉTRICA ---
            foto_ent = st.camera_input("📸 Capture foto de entrada (Presencia)")
            
            if st.button("☀️ MARCAR ENTRADA", type="primary", use_container_width=True):
                if foto_ent:
                    with st.spinner("Registrando huella visual y guardando en Maletín..."):
                        # Subir foto
                        url_e = subir_a_imgbb(foto_ent)
                        
                        # Preparar datos para persistencia (Nube + Local)
                        datos_entrada = {
                            "FECHA": str_fecha,
                            "USUARIO": st.session_state.u['NOMBRE'],
                            "TIPO": "ASISTENCIA",
                            "HORA_ENTRADA": str_hora,
                            "FOTO_ENTRADA": url_e if url_e else foto_a_texto(foto_ent),
                            "HORA_SALIDA": "",
                            "FOTO_SALIDA": "-",
                            "MOTIVO": motivo_entrada,
                            "ALERTA_IA": "ENTRADA_REVISAR" if es_tarde_entrada else "-",
                            "PUNTOS_MERITO": 10,
                            "ESTADO": "ACTIVO"
                        }

                        # 1. Guardar en el teléfono (Resiliencia)
                        respaldar_en_dispositivo(datos_entrada)

                        # 2. Intentar guardar en la nube
                        try:
                            df_final = pd.concat([df_asis, pd.DataFrame([datos_entrada])], ignore_index=True)
                            conn.update(spreadsheet=url, worksheet="ASISTENCIA", data=df_final)
                            st.success(f"✅ Entrada registrada en la nube a las: {str_hora}")
                        except:
                            st.warning("⚠️ Guardado en memoria local (Sin internet). Se sincronizará luego.")
                        
                        st.balloons()
                        time.sleep(2)
                        st.session_state.pagina_actual = "HOME"
                        st.rerun()
                else:
                    st.error("Es obligatorio tomar la foto para validar la presencia en el plantel.")

        else:
            # --- MEJORA: REPORTE DE INASISTENCIA (v7.0) ---
            st.subheader("Reportar Inasistencia")
            motivo_falta = st.selectbox("Causa de la falta:", [
                "Salud (Reposo/Cita)", "Falla Mecánica / Transporte", 
                "Lluvia / Desastre Natural", "Asuntos Personales"
            ])
            obs_f = st.text_area("Detalles de la falta:")
            if st.button("📤 Enviar Reporte de Falta"):
                with st.spinner("Analizando..."):
                    # IA analiza salud para alerta legal
                    an = generar_respuesta([{"role":"user","content":f"¿Es salud? '{obs_f}'"}], 0.1)
                    alerta = "⚠️ Entregar justificativo médico." if "ALERTA_SALUD" in an or "Salud" in motivo_falta else "-"
                    pts = 5 if "Salud" in motivo_falta or "Lluvia" in motivo_falta else 0
                    
                    nuevo_f = pd.DataFrame([{
                        "FECHA": str_fecha, "USUARIO": st.session_state.u['NOMBRE'], "TIPO": "INASISTENCIA",
                        "HORA_ENTRADA": "-", "FOTO_ENTRADA": "-", "HORA_SALIDA": "-", "FOTO_SALIDA": "-",
                        "MOTIVO": f"{motivo_falta}: {obs_f}", "ALERTA_IA": alerta, "PUNTOS_MERITO": pts, "ESTADO": "CERRADO"
                    }])
                    conn.update(spreadsheet=url, worksheet="ASISTENCIA", data=pd.concat([df_asis, nuevo_f]))
                    st.warning(f"Reportado. Se asignaron {pts} puntos solidarios."); time.sleep(2); st.rerun()
            
    else:
        # YA HAY REGISTRO, VERIFICAMOS SI FALTA SALIDA (CASE B)
        fila = mi_registro.iloc[0]
        
        if not fila['HORA_SALIDA'] or fila['HORA_SALIDA'] == "" or fila['HORA_SALIDA'] == "-":
            st.success(f"✅ Entrada marcada a las: {fila['HORA_ENTRADA']}")
            st.info("La jornada está en curso. Que tengas buen día.")
            
            # --- MEJORA: BONO HEROICO Y TRABAJO EXTRA ---
            col_h, col_e = st.columns(2)
            with col_h:
                es_heroe = st.checkbox("🦸 ¿Hice Suplencia?")
            with col_e:
                es_extra = st.checkbox("💼 ¿Trabajo Extra?")
            
            suplencia_a = "-"
            puntos_finales = 10
            
            if es_heroe:
                lista_c = st.session_state.get('LISTA_DOCENTES', [st.session_state.u['NOMBRE']])
                suplencia_a = st.selectbox("¿A quién cubriste?", [p for p in lista_c if p != st.session_state.u['NOMBRE']])
                puntos_finales += 5
                st.caption(f"Bono Heroico activado (+5 pts por {suplencia_a})")

            if es_extra:
                actividad_extra = st.text_input("¿Qué labor extra realizó?", placeholder="Ej: Carteleras, Mantenimiento...")
                puntos_finales += 3
            
            # --- MEJORA: LÓGICA DE COHERENCIA HORARIA ---
            es_fuera_hora = h_actual_int >= 14 or h_actual_int < 11
            motivo_salida = "Salida Normal"
            
            if es_fuera_hora:
                st.warning("⚠️ Registro de salida fuera de horario habitual.")
                just_s = st.selectbox("Motivo del retraso:", ["Corte Eléctrico", "Sin Datos", "Olvido", "Actividad Prolongada"])
                h_real = st.text_input("Hora REAL de salida del plantel (Libro físico):")
                motivo_salida = f"FUERA_HORA: {just_s} | Real: {h_real}"
                if not h_real: st.stop()

            obs_sal = st.text_input("Novedades de salida:", placeholder="Jornada cumplida sin novedad...")
            
            # --- MEJORA: CÁMARA DE SALIDA ---
            foto_sal = st.camera_input("📸 Capture foto de salida (Evidencia)")

            if st.button("🌙 MARCAR SALIDA", type="primary", use_container_width=True):
                if foto_sal:
                    with st.spinner("Cerrando jornada y guardando en Maletín..."):
                        url_s = subir_a_imgbb(foto_sal)
                        h_s_sis = ahora_ve().strftime('%I:%M %p')
                        
                        # Actualizar datos
                        datos_completos = dict(fila)
                        datos_completos["HORA_SALIDA"] = h_s_sis
                        datos_completos["FOTO_SALIDA"] = url_s if url_s else foto_a_texto(foto_sal)
                        datos_completos["MOTIVO"] = f"{motivo_salida} | {obs_sal}"
                        datos_completos["PUNTOS_MERITO"] = puntos_finales
                        datos_completos["SUPLENCIA_A"] = suplencia_a
                        datos_completos["ESTADO"] = "CERRADO"

                        # 1. Actualizar Maletín
                        respaldar_en_dispositivo(datos_completos)

                        # 2. Intentar Nube
                        try:
                            idx = mi_registro.index[0]
                            df_asis.at[idx, 'HORA_SALIDA'] = h_s_sis
                            df_asis.at[idx, 'FOTO_SALIDA'] = url_s if url_s else "-"
                            df_asis.at[idx, 'MOTIVO'] = datos_completos["MOTIVO"]
                            df_asis.at[idx, 'PUNTOS_MERITO'] = puntos_finales
                            df_asis.at[idx, 'SUPLENCIA_A'] = suplencia_a
                            df_asis.at[idx, 'ESTADO'] = "CERRADO"
                            
                            conn.update(spreadsheet=url, worksheet="ASISTENCIA", data=df_asis)
                            # Si tuvo éxito, podemos limpiar el maletín de hoy
                            from utils.maletin import borrar_del_dispositivo
                            borrar_del_dispositivo("maletin_asistencia")
                            st.success(f"✅ Jornada cerrada en la nube: {h_s_sis}")
                        except:
                            st.warning("⚠️ Salida guardada en el dispositivo. Sincronice al tener internet.")
                        
                        time.sleep(1.5)
                        st.session_state.pagina_actual = "HOME"
                        st.rerun()
                else:
                    st.error("Es obligatorio tomar la foto de salida para certificar la culminación de la actividad.")
        else:
            # CASO C: YA SE FUE -> RESUMEN (Original preservado)
            st.success("🏆 JORNADA COMPLETADA.")
            st.write(f"**Entrada:** {fila['HORA_ENTRADA']}")
            st.write(f"**Salida:** {fila['HORA_SALIDA']}")
            st.write(f"**Puntos ganados hoy:** {fila.get('PUNTOS_MERITO', 10)}")
            
            if st.button("🏠 Volver al Menú"):
                st.session_state.pagina_actual = "HOME"
                st.rerun()
