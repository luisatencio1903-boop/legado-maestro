import streamlit as st
import time
import os
from utils.comunes import limpiar_id
from utils.db import conectar_db

def render_login(conn):
    """
    Renderiza la pantalla de Login.
    Incluye lógica de Auto-Login (URL) y Login Manual.
    """
    # --- 1. LÓGICA DE AUTO-LOGIN (VIRTUD V1) ---
    query_params = st.query_params
    usuario_en_url = query_params.get("u", None)
    
    # URL de la hoja (la sacamos de los secretos directamente aquí para rapidez)
    try:
        URL_HOJA = st.secrets["GSHEETS_URL"]
    except:
        st.error("Falta configurar secretos.")
        return

    if usuario_en_url:
        try:
            # Leemos usuarios sin caché (ttl=0) para seguridad máxima al entrar
            df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
            
            # Limpieza para comparar
            df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
            usuario_limpio = limpiar_id(usuario_en_url)
            
            match = df_u[df_u['C_L'] == usuario_limpio]
            
            if not match.empty:
                st.session_state.auth = True
                st.session_state.u = match.iloc[0].to_dict()
                st.rerun()
            else:
                st.query_params.clear()
        except:
            pass 

    # --- 2. PANTALLA VISUAL ---
    st.title("🛡️ SUPER DOCENTE 2.0")
    
    col_logo, col_form = st.columns([1, 2])
    
    with col_logo:
        # Intentamos mostrar el logo, si no, un emoji
        if os.path.exists("logo_legado.png"):
            st.image("logo_legado.png", width=150)
        else:
            st.header("🍎")
            
    with col_form:
        st.markdown("### Iniciar Sesión")
        cedula_input = st.text_input("Cédula de Identidad:", key="login_c")
        pass_input = st.text_input("Contraseña:", type="password", key="login_p")
        
        if st.button("🔐 Entrar", use_container_width=True):
            if not cedula_input or not pass_input:
                st.warning("Escribe tus datos.")
            else:
                try:
                    with st.spinner("Verificando..."):
                        df_u = conn.read(spreadsheet=URL_HOJA, worksheet="USUARIOS", ttl=0)
                        
                        df_u['C_L'] = df_u['CEDULA'].apply(limpiar_id)
                        cedula_limpia = limpiar_id(cedula_input)
                        
                        # Búsqueda exacta
                        match = df_u[
                            (df_u['C_L'] == cedula_limpia) & 
                            (df_u['CLAVE'] == pass_input)
                        ]
                        
                        if not match.empty:
                            st.session_state.auth = True
                            st.session_state.u = match.iloc[0].to_dict()
                            # Guardamos cookie en URL
                            st.query_params["u"] = cedula_limpia 
                            st.success(f"¡Bienvenido, {st.session_state.u['NOMBRE']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Credenciales incorrectas.")
                            
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
