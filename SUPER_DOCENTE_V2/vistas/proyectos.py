import streamlit as st
import pandas as pd
import time
from utils.comunes import ahora_ve

def render_proyectos(conn):
    st.header("🏗️ Configuración de Proyectos y Planes")
    st.markdown("Defina su hoja de ruta. El sistema diferenciará los días de Teoría (P.A.) y Práctica (P.S.P.).")

    # 1. LEER DATOS (Con Caché y Prioridad Local)
    try:
        url = st.secrets["GSHEETS_URL"]
        df_proy = conn.read(spreadsheet=url, worksheet="CONFIG_PROYECTO", ttl=0)
        # Filtramos por usuario
        mi_proy = df_proy[df_proy['USUARIO'] == st.session_state.u['NOMBRE']]
    except:
        mi_proy = pd.DataFrame()

    # FORMULARIO
    with st.form("form_config_proyectos"):
        
        st.subheader("1. Identidad del Servicio")
        # Intentamos recuperar el valor guardado
        idx_mod = 0
        if not mi_proy.empty and "MODALIDAD" in mi_proy.columns:
            mod_guardada = mi_proy.iloc[0]['MODALIDAD']
            lista_ops = ["Taller de Educación Laboral (T.E.L.)", "Aula Integrada", "Escuela Especial"]
            if mod_guardada in lista_ops:
                idx_mod = lista_ops.index(mod_guardada)

        modalidad = st.selectbox("¿A qué Modalidad o Servicio pertenece usted?", 
                               ["Taller de Educación Laboral (T.E.L.)", "Aula Integrada", "Escuela Especial"],
                               index=idx_mod)
        
        st.divider()
        
        st.subheader("2. Datos de los Proyectos y Horarios")
        
        # --- SECCIÓN A: PROYECTO DE APRENDIZAJE (P.A.) ---
        st.markdown("##### 📘 Proyecto de Aprendizaje (P.A. - Aula/Teoría)")
        st.caption("Días dedicados a la formación académica, valores y teoría en el aula.")
        
        # Recuperar Titulo PA
        val_pa = "VALORES PARA EL TRABAJO LIBERADOR"
        if not mi_proy.empty and "TITULO_PA" in mi_proy.columns:
             val_pa = mi_proy.iloc[0]['TITULO_PA']
        pa_titulo = st.text_input("Nombre del P.A.:", value=val_pa)
        
        # Recuperar Días PA
        dias_pa_default = []
        if not mi_proy.empty and "DIAS_PA" in mi_proy.columns and pd.notna(mi_proy.iloc[0]['DIAS_PA']):
            raw_pa = str(mi_proy.iloc[0]['DIAS_PA'])
            if raw_pa.strip() != "":
                dias_pa_default = raw_pa.split(",")
                dias_pa_default = [d.strip() for d in dias_pa_default if d.strip() in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]]

        dias_pa_sel = st.multiselect("Seleccione los días de P.A. (Aula):", 
                                     ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
                                     default=dias_pa_default,
                                     key="sel_dias_pa")

        st.write("") 
        st.divider()

        # --- SECCIÓN B: PROYECTO SOCIO-PRODUCTIVO (P.S.P.) ---
        st.markdown("##### 🛠️ Proyecto Socio-Productivo (P.S.P. - Taller/Práctica)")
        st.caption("Días dedicados a la práctica laboral, taller y manos a la obra.")
        
        # Recuperar Titulo PSP
        val_psp = "VIVERO ORNAMENTAL"
        if not mi_proy.empty and "TITULO_PSP" in mi_proy.columns:
             val_psp = mi_proy.iloc[0]['TITULO_PSP']
        psp_titulo = st.text_input("Nombre del P.S.P.:", value=val_psp)
        
        # Recuperar Días PSP
        dias_psp_default = []
        if not mi_proy.empty and "DIAS_PSP" in mi_proy.columns and pd.notna(mi_proy.iloc[0]['DIAS_PSP']):
            raw_psp = str(mi_proy.iloc[0]['DIAS_PSP'])
            if raw_psp.strip() != "":
                dias_psp_default = raw_psp.split(",")
                dias_psp_default = [d.strip() for d in dias_psp_default if d.strip() in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]]

        dias_psp_sel = st.multiselect("Seleccione los días de P.S.P. (Taller):", 
                                      ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"],
                                      default=dias_psp_default,
                                      key="sel_dias_psp")

        st.divider()
        
        # ESTADO DEL PROYECTO
        c_tog, c_st = st.columns([1, 4])
        with c_tog:
            # Recuperar estado
            estado_val = True
            if not mi_proy.empty and "ESTADO" in mi_proy.columns:
                if mi_proy.iloc[0]['ESTADO'] == "PAUSADO":
                    estado_val = False
            activo = st.toggle("✅ ACTIVAR PROYECTO", value=estado_val)
        with c_st:
            st.caption("Si desactiva, el sistema usará planificación genérica.")

        submitted = st.form_submit_button("💾 Guardar Configuración")
        
        if submitted:
            try:
                # Preparamos los días como texto separado por comas
                str_dias_pa = ",".join(dias_pa_sel)
                str_dias_psp = ",".join(dias_psp_sel)
                
                # 1. Borramos el registro anterior del usuario para no duplicar
                df_nuevo = df_proy[df_proy['USUARIO'] != st.session_state.u['NOMBRE']]
                
                # 2. Creamos el nuevo registro con TODOS los campos
                registro_actualizado = pd.DataFrame([{
                    "FECHA": ahora_ve().strftime("%d/%m/%Y"),
                    "USUARIO": st.session_state.u['NOMBRE'],
                    "MODALIDAD": modalidad,
                    "TITULO_PA": pa_titulo,
                    "TITULO_PSP": psp_titulo,
                    "DIAS_PA": str_dias_pa,    
                    "DIAS_PSP": str_dias_psp,  
                    "ESTADO": "ACTIVO" if activo else "PAUSADO"
                }])
                
                # 3. Guardamos
                conn.update(spreadsheet=url, worksheet="CONFIG_PROYECTO", data=pd.concat([df_nuevo, registro_actualizado], ignore_index=True))
                st.success("✅ ¡Horarios diferenciados guardados correctamente!")
                time.sleep(1.5)
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al guardar: {e}. (Verifica que la hoja CONFIG_PROYECTO exista).")
