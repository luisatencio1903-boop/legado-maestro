import streamlit as st
import pandas as pd
import time
from utils.maletin import recuperar_del_dispositivo, borrar_del_dispositivo
from utils.traductor import texto_a_foto
from utils.drive_api import subir_a_imgbb

def sincronizar_todo_el_maletin(conn, url_hoja):
    progreso = st.progress(0, text="Iniciando sincronización...")
    
    # 1. SINCRONIZAR ASISTENCIA
    maletin_asis = recuperar_del_dispositivo("maletin_asistencia")
    if maletin_asis:
        progreso.progress(25, text="Sincronizando Asistencia...")
        
        # Si la foto es texto (Base64), la subimos a ImgBB
        if "data:image" in str(maletin_asis.get("FOTO_ENTRADA", "")):
            foto_file = texto_a_foto(maletin_asis["FOTO_ENTRADA"])
            link = subir_a_imgbb(foto_file)
            if link: maletin_asis["FOTO_ENTRADA"] = link

        if "data:image" in str(maletin_asis.get("FOTO_SALIDA", "")):
            foto_file_s = texto_a_foto(maletin_asis["FOTO_SALIDA"])
            link_s = subir_a_imgbb(foto_file_s)
            if link_s: maletin_asis["FOTO_SALIDA"] = link_s

        try:
            df_asis = conn.read(spreadsheet=url_hoja, worksheet="ASISTENCIA", ttl=0)
            # Buscamos si ya existe el registro para actualizar o crear
            filtro = (df_asis['USUARIO'] == maletin_asis['USUARIO']) & (df_asis['FECHA'] == maletin_asis['FECHA'])
            if not df_asis[filtro].empty:
                idx = df_asis[filtro].index[0]
                for c in maletin_asis:
                    if c in df_asis.columns: df_asis.at[idx, c] = maletin_asis[c]
                conn.update(spreadsheet=url_hoja, worksheet="ASISTENCIA", data=df_asis)
            else:
                nuevo_df = pd.concat([df_asis, pd.DataFrame([maletin_asis])], ignore_index=True)
                conn.update(spreadsheet=url_hoja, worksheet="ASISTENCIA", data=nuevo_df)
            
            borrar_del_dispositivo("maletin_asistencia")
            st.toast("✅ Asistencia sincronizada")
        except:
            st.error("Fallo al subir asistencia. Reintente.")

    # 2. SINCRONIZAR AULA VIRTUAL (EJECUCIÓN)
    maletin_clase = recuperar_del_dispositivo("maletin_super_docente")
    if maletin_clase and maletin_clase.get("av_resumen"):
        progreso.progress(75, text="Sincronizando Aula Virtual...")
        
        f1 = maletin_clase.get("av_foto1")
        f2 = maletin_clase.get("av_foto2")
        f3 = maletin_clase.get("av_foto3")
        
        # Procesar fotos 1, 2 y 3 si son Base64
        urls_finales = []
        for f in [f1, f2, f3]:
            if f and "data:image" in str(f):
                link = subir_a_imgbb(texto_a_foto(f))
                urls_finales.append(link if link else "-")
            else:
                urls_finales.append(f if f else "-")
        
        try:
            df_ej = conn.read(spreadsheet=url_hoja, worksheet="EJECUCION", ttl=0)
            nueva_fila = pd.DataFrame([{
                "FECHA": maletin_clase.get("FECHA", ahora_ve().strftime("%d/%m/%Y")),
                "USUARIO": st.session_state.u['NOMBRE'],
                "DOCENTE_TITULAR": maletin_clase.get("titular", st.session_state.u['NOMBRE']),
                "ACTIVIDAD_TITULO": maletin_clase.get("av_titulo_hoy", "Clase Recuperada"),
                "EVIDENCIA_FOTO": "|".join(urls_finales),
                "RESUMEN_LOGROS": maletin_clase.get("av_resumen", ""),
                "ESTADO": "CULMINADA",
                "PUNTOS": 5
            }])
            conn.update(spreadsheet=url_hoja, worksheet="EJECUCION", data=pd.concat([df_ej, nueva_fila], ignore_index=True))
            borrar_del_dispositivo("maletin_super_docente")
            st.toast("✅ Aula Virtual sincronizada")
        except:
            st.error("Fallo al subir ejecución. Reintente.")

    progreso.progress(100, text="¡Todo al día!")
    time.sleep(2)
    st.rerun()
