import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Legado Maestro - Gestión Zulia", layout="wide")

# --- 2. CONEXIÓN (Usa el encabezado [connections.gsheets] de tus Secrets) ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_HOJA = st.secrets["GSHEETS_URL"]

# --- 3. FUNCIONES DE LIMPIEZA Y SEGURIDAD ---
def limpiar_dato(valor):
    """Quita espacios y el .0 de las cédulas de Google Sheets"""
    return str(valor).strip().split('.')[0]

# --- 4. GESTIÓN DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None

# --- 5. INTERFAZ DE ACCESO ---
if not st.session_state.autenticado:
    st.title("🛡️ Seguridad Legado Maestro")
    tab_login, tab_registro = st.tabs(["🔐 Entrar", "📝 Registrarse"])

    with tab_login:
        c_login = st.text_input("Cédula", key="l_ced")
        p_login = st.text_input("Contraseña", type="password", key="l_pass")
        if st.button("INICIAR SESIÓN"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            # Limpiamos y buscamos coincidencia real
            df_u['CEDULA_LIMPIA'] = df_u['CEDULA'].apply(limpiar_dato)
            match = df_u[(df_u['CEDULA_LIMPIA'] == limpiar_dato(c_login)) & (df_u['CLAVE'] == p_login)]
            
            if not match.empty:
                st.session_state.autenticado = True
                st.session_state.usuario = match.iloc[0].to_dict()
                st.success("Acceso concedido...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Credenciales incorrectas o usuario no activo.")

    with tab_registro:
        st.subheader("Validación de Nómina")
        c_reg = st.text_input("Ingrese su Cédula", key="r_ced")
        p_reg = st.text_input("Cree su Contraseña", type="password", key="r_pass")
        
        if st.button("VALIDAR Y ACTIVAR CUENTA"):
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            df_u['CEDULA_LIMPIA'] = df_u['CEDULA'].apply(limpiar_dato)
            cedula_ingresada = limpiar_dato(c_reg)

            if cedula_ingresada in df_u['CEDULA_LIMPIA'].values:
                idx = df_u.index[df_u['CEDULA_LIMPIA'] == cedula_ingresada][0]
                
                if pd.notna(df_u.loc[idx, 'CLAVE']) and str(df_u.loc[idx, 'CLAVE']).strip() != "":
                    st.warning("Usted ya tiene una cuenta activa.")
                else:
                    df_u.loc[idx, 'CLAVE'] = p_reg
                    df_u.loc[idx, 'ESTADO'] = "ACTIVO"
                    # Eliminamos la columna temporal antes de subir
                    df_subir = df_u.drop(columns=['CEDULA_LIMPIA'])
                    conn.update(spreadsheet=URL_HOJA, worksheet="USUARIOS", data=df_subir)
                    st.success("✅ ¡Registro exitoso! Ahora puede iniciar sesión.")
            else:
                st.error("🚫 Su cédula no está autorizada en la nómina oficial.")

# --- 6. PANEL DE CONTROL (SI ESTÁ AUTENTICADO) ---
else:
    u = st.session_state.usuario
    st.sidebar.title(f"👤 {u['NOMBRE']}")
    st.sidebar.write(f"Rol: **{u['ROL']}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    # --- VISTA DOCENTE ---
    if u['ROL'] == "DOCENTE":
        st.header("👨‍🏫 Planificador Técnico en Vivo")
        tema = st.text_input("Tema de la clase:", value="Mantenimiento General")
        
        if st.button("🧠 GENERAR PLANIFICACIÓN IA"):
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            res = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Planifica 8 puntos técnicos para {tema} en educación especial."}],
                model="llama-3.3-70b-versatile"
            )
            st.session_state.plan_doc = res.choices[0].message.content
            st.info(st.session_state.plan_doc)

        if 'plan_doc' in st.session_state:
            if st.button("🚀 INICIAR CLASE Y REPORTAR"):
                df_act = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
                nueva_fila = pd.DataFrame([{
                    "FECHA": datetime.now().strftime("%d/%m/%Y"),
                    "USUARIO": u['NOMBRE'],
                    "ROL": u['ROL'],
                    "AULA": "MANTENIMIENTO",
                    "TEMA": tema,
                    "CONTENIDO": st.session_state.plan_doc,
                    "ESTADO": "EN CURSO",
                    "HORA_INICIO": datetime.now().strftime("%H:%M")
                }])
                df_final = pd.concat([df_act, nueva_fila], ignore_index=True)
                conn.update(spreadsheet=URL_HOJA, worksheet="Hoja1", data=df_final)
                st.balloons()
                st.success("Reporte enviado al Director con éxito.")

    # --- VISTA DIRECTOR / SUPERVISOR ---
    else:
        st.header(f"📊 Monitor de Gestión: {u['ROL']}")
        df_ver = conn.read(spreadsheet=URL_HOJA, worksheet="Hoja1", ttl=0)
        
        # Filtro de seguridad: El Director ve todo el historial
        st.subheader("Seguimiento de Actividades Escolares")
        st.dataframe(df_ver)
