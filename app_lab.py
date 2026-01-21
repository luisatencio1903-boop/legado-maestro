# ---------------------------------------------------------
# PROYECTO: LEGADO MAESTRO (LABORATORIO)
# VERSIÓN: 1.7 (Cerebro IA + Google Sheets + Supervisión)
# FECHA: Enero 2026
# AUTOR: Luis Atencio
# ---------------------------------------------------------

import streamlit as st
import pandas as pd
from datetime import datetime
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import os

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Legado Maestro LAB", page_icon="🧪", layout="centered")

# --- DISFRAZ DE PRUEBAS ---
st.warning("⚠️ MODO LABORATORIO: CONECTADO A GOOGLE SHEETS ☁️")
st.sidebar.warning("🛠️ DATA EN LA NUBE")

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    .plan-box {
        background-color: #f0f2f6 !important;
        color: #000000 !important; 
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0068c9;
        margin-bottom: 20px;
    }
    .plan-box strong { color: #2c3e50 !important; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de conexión a Google: {e}")

# --- 4. FUNCIONES DE BASE DE DATOS ---
def guardar_en_nube(aula, tema, contenido):
    try:
        # Lee la hoja (Hoja 1 debe ser el nombre de la pestaña en tu Excel)
        df_existente = conn.read(worksheet="Hoja 1", ttl=0)
        nueva_fila = pd.DataFrame([{
            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Aula": aula,
            "Tema": tema,
            "Contenido": contenido
        }])
        df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
        conn.update(worksheet="Hoja 1", data=df_final)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

def leer_de_nube():
    try:
        return conn.read(worksheet="Hoja 1", ttl=0)
    except:
        return pd.DataFrame()

# --- 5. LÓGICA DE INTELIGENCIA ARTIFICIAL ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def generar_respuesta(mensajes, temp=0.4):
    chat_completion = client.chat.completions.create(
        messages=mensajes, model="llama-3.3-70b-versatile", temperature=temp
    )
    return chat_completion.choices[0].message.content

# --- 6. INTERFAZ Y MENÚ ---
with st.sidebar:
    st.title("Legado Maestro")
    st.caption("🧪 MODO LABORATORIO")
    st.markdown("---")
    
    # VISOR DE GAVETA EN LA NUBE
    st.subheader("📂 Gaveta en la Nube")
    if st.button("🔄 Actualizar Gaveta"):
        st.rerun()
    
    df_nube = leer_de_nube()
    if not df_nube.empty:
        # Mostramos los últimos 3 registros para no saturar
        for i, row in df_nube.tail(3).iterrows():
            with st.expander(f"📅 {row['Fecha']} - {row['Tema']}"):
                st.write(row['Contenido'])

opcion = st.selectbox("Herramienta:", ["📝 Planificación Profesional", "📊 Panel de Supervisión (Jefatura)"])

# --- OPCIÓN 1: PLANIFICADOR ---
if opcion == "📝 Planificación Profesional":
    st.subheader("Planificación Técnica (Taller Laboral)")
    col1, col2 = st.columns(2)
    with col1: rango = st.text_input("Lapso:", placeholder="Ej: 19 al 23 de Enero")
    with col2: aula = st.text_input("Aula/Taller:", value="Mantenimiento")
    tema = st.text_input("Tema central:")
    notas = st.text_area("Notas adicionales:", height=100)

    if st.button("🚀 Generar Planificación"):
        prompt = f"Actúa como Luis Atencio. Crea una planificación técnica de 8 puntos para {aula} sobre {tema}. Notas: {notas}. Lapso: {rango}."
        res = generar_respuesta([{"role": "user", "content": prompt}])
        st.session_state.plan_lab = res
        st.rerun()

    if 'plan_lab' in st.session_state:
        st.markdown(f'<div class="plan-box">{st.session_state.plan_lab}</div>', unsafe_allow_html=True)
        
        if st.button("💾 GUARDAR EN GOOGLE SHEETS"):
            with st.spinner("Subiendo a la nube de Google..."):
                if guardar_en_nube(aula, tema, st.session_state.plan_lab):
                    st.success("✅ ¡Guardado en la Nube con éxito!")
                    st.balloons()

# --- OPCIÓN 2: SUPERVISIÓN ---
elif opcion == "📊 Panel de Supervisión (Jefatura)":
    st.subheader("📡 Supervisión en Tiempo Real (Demo)")
    df_stats = leer_de_nube()
    st.metric("Total de Actividades Registradas", len(df_stats))
    st.dataframe(df_stats, use_container_width=True)
