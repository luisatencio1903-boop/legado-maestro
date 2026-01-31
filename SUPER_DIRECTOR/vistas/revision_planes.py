import streamlit as st
import pandas as pd
import time

# Agregamos 'universo' a los argumentos que recibe la función
def render_revision(conn, URL_HOJA, universo):
    
    # --- CAMBIO CLAVE: LECTURA DESDE MEMORIA ---
    # En lugar de leer directo de GSheets, buscamos en el universo cargado
    # En comunes.py definimos que la hoja "Hoja1" se guarda en la clave "planes"
    if 'planes' in universo:
        # Usamos .copy() para no alterar los datos originales hasta guardar
        df_planes = universo['planes'].copy()
    else:
        st.error("Error: No se encontraron datos de planificación en el universo.")
        return
    # -------------------------------------------

    st.subheader("📩 Buzón de Planificaciones Semanales")
    st.markdown("Revisión de planes enviados para la implementación de la próxima semana.")

    # Filtramos sobre el dataframe que sacamos del universo
    pendientes = df_planes[df_planes['ESTADO'] == "PENDIENTE"]

    if pendientes.empty:
        st.success("No hay planificaciones nuevas por revisar en el buzón.")
    else:
        for idx, fila in pendientes.iterrows():
            with st.expander(f"📄 {fila['TEMA']} | 👤 {fila['USUARIO']} | 📅 {fila['FECHA']}"):
                st.markdown(f'<div class="plan-box">{fila["CONTENIDO"]}</div>', unsafe_allow_html=True)
                
                st.divider()
                st.markdown("#### ⚖️ Decisión de Dirección")
                comentario = st.text_area("Sugerencias o correcciones (Solo si manda a corregir):", key=f"com_{idx}")
                
                c1, c2 = st.columns(2)
                
                if c1.button("✅ Aprobar e Implementar", key=f"btn_ap_pl_{idx}", use_container_width=True):
                    df_planes.at[idx, 'ESTADO'] = "APROBADO"
                    df_planes.at[idx, 'COMENTARIO_DIRECTOR'] = "Aprobada para su ejecución."
                    
                    # Escritura: Aquí sí usamos la conexión para guardar en la nube
                    conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_planes)
                    
                    st.success("Planificación aprobada.")
                    # Limpiamos caché para que al recargar se vean los cambios
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                
                if c2.button("❌ Mandar a Corregir", key=f"btn_re_pl_{idx}", use_container_width=True):
                    if comentario:
                        df_planes.at[idx, 'ESTADO'] = "CORRECCION"
                        df_planes.at[idx, 'COMENTARIO_DIRECTOR'] = comentario
                        
                        conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_planes)
                        
                        st.warning("Planificación devuelta para correcciones.")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Debe escribir un comentario para que el docente sepa qué corregir.")
