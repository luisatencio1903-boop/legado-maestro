import streamlit as st
import os
import pandas as pd

def obtener_plan_activa(conn, usuario):
    """Consulta rápida a la BD para ver si hay plan activo (Lógica V1)."""
    try:
        # Usamos ttl=60 (1 min) para no saturar, igual que en V1
        df = conn.read(spreadsheet=st.secrets["GSHEETS_URL"], worksheet="PLAN_ACTIVA", ttl=60)
        activo = df[(df['USUARIO'] == usuario) & (df['ACTIVO'] == True)]
        if not activo.empty:
            return activo.iloc[0].to_dict()
        return None
    except:
        return None

def render_sidebar(conn):
    with st.sidebar:
        # 1. LOGO (Si existe el archivo)
        if os.path.exists("logo_legado.png"):
            st.image("logo_legado.png", width=150)
        else:
            st.header("🍎") # Emoji por si no has subido la foto aún
            
        st.title("SUPER DOCENTE 2.0")
        st.caption(f"Prof. {st.session_state.u['NOMBRE']}")
        
        # 2. ESTADO DE PLANIFICACIÓN (Regla de Oro: Info Vital)
        st.markdown("---")
        plan = obtener_plan_activa(conn, st.session_state.u['NOMBRE'])
        
        if plan:
            st.success("📌 **Planificación Activa**")
            with st.expander("Ver detalles", expanded=False):
                st.caption(f"**Rango:** {plan.get('RANGO', '--')}")
                st.caption(f"**Aula:** {plan.get('AULA', '--')}")
        else:
            st.warning("⚠️ **Sin planificación activa**")
            st.caption("Ve a 'Mi Archivo' para activar una.")
            
        st.markdown("---")
