import streamlit as st
import pandas as pd
from datetime import datetime
import time

# --- ESTRUCTURA DE PANTALLA PROFESIONAL ---
st.set_page_config(page_title="Legado Maestro - Torre de Control", layout="wide")

# Estilos CSS para tarjetas y botones
st.markdown("""
    <style>
    .card { background: white; padding: 20px; border-radius: 10px; border-left: 5px solid #0068c9; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; }
    .status-pendiente { color: #f39c12; font-weight: bold; }
    .status-aprobado { color: #2ecc71; font-weight: bold; }
    .status-envivo { color: #e74c3c; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE USUARIOS (Ya funcional) ---
# (Asumimos que el usuario ya está logueado y tenemos st.session_state.usuario)

u = st.session_state.usuario

# --- PANEL DOCENTE (ESTILO NAVEGADOR) ---
if u['ROL'] == "DOCENTE":
    st.title(f"👨‍🏫 Aula de {u['NOMBRE']}")
    
    # Sistema de ventanas tipo navegador
    t_semana, t_hoy, t_historial = st.tabs(["📅 Planificación Semanal", "🚀 Actividad de Hoy", "📜 Mi Memoria"])

    with t_semana:
        st.subheader("Planificación de la Próxima Semana")
        # Aquí el docente genera su plan (por ejemplo un domingo)
        plan_propuesto = st.text_area("Desarrolle la planificación técnica:", height=200)
        if st.button("Enviar para Revisión del Director"):
            # GUARDAR EN EXCEL con ESTADO = "PENDIENTE REVISION"
            st.success("Planificación enviada. Espere la aprobación del Director para ejecutar.")

    with t_hoy:
        # Filtramos en el Excel si hay una planificación APROBADA para HOY
        st.subheader(f"Actividad Programada: {datetime.now().strftime('%A %d/%m')}")
        
        # Simulamos que hay una aprobada
        st.info("✅ Planificación Aprobada por Dirección: 'Mantenimiento de Circuitos'")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶️ INICIAR ACTIVIDAD"):
                st.session_state.en_clase = True
                # Registrar HORA_INICIO en Hoja1
        with c2:
            if st.button("⏹️ CULMINAR ACTIVIDAD"):
                st.session_state.en_clase = False
                # Registrar HORA_FIN y pedir EVIDENCIA
        
        if st.session_state.get('en_clase'):
            st.markdown("### <span class='status-envivo'>● ACTIVIDAD EN PROGRESO</span>", unsafe_allow_html=True)
            foto = st.file_uploader("Subir Evidencia (Foto/Reporte)")

# --- PANEL DIRECTOR (MONITOR INTERACTIVO) ---
elif u['ROL'] == "DIRECTOR":
    st.title("🏛️ Torre de Control Institucional")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Docentes Activos", "4", "+1")
    col_m2.metric("Pendientes por Revisar", "2")
    col_m3.metric("Evidencias Cargadas", "85%")

    st.markdown("---")
    
    # VENTANA 1: REVISIÓN DE PLANES (Lo que pediste de los viernes/lunes)
    with st.expander("📥 Planificaciones por Aprobar", expanded=True):
        st.write("Docente: Luis Atencio - Aula: Mantenimiento")
        st.text("Plan: Mantenimiento de motores para el día miércoles...")
        
        # Cuadro de sugerencias que pediste
        observacion = st.text_input("Sugerencias o modificaciones (Ej: Cambiar actividad del miércoles):")
        
        c_a1, c_a2 = st.columns(2)
        if c_a1.button("✅ APROBAR PLAN"):
            st.success("Plan aprobado. El docente ya puede visualizarlo.")
        if c_a2.button("⚠️ ENVIAR CON OBSERVACIONES"):
            st.warning("Sugerencias enviadas al docente.")

    # VENTANA 2: MONITOR EN VIVO
    st.subheader("👀 Monitor de Actividad en Tiempo Real (Hoy)")
    # Simulamos datos del día
    st.markdown("""
        <div class='card'>
            <h4>Docente: Luis Atencio</h4>
            <p><b>Estado:</b> <span class='status-envivo'>● EN CLASE</span></p>
            <p><b>Tema:</b> Motores Eléctricos | <b>Inicio:</b> 08:00 AM</p>
            <p><b>Evidencia:</b> <span style='color:gray'>Esperando culminación...</span></p>
        </div>
    """, unsafe_allow_html=True)
