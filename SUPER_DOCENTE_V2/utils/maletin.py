import json
import streamlit as st

# Intentamos conectar con el motor del navegador (Stlite)
try:
    from js import window
    localStorage = window.localStorage
except ImportError:
    # Si estamos en Streamlit Cloud normal, usamos un maletín virtual
    localStorage = None

def inicializar_maletin():
    """Retorna el objeto localStorage del navegador."""
    return localStorage

def persistir_en_dispositivo(llave, valor):
    """Guarda datos físicamente en el disco duro del navegador del celular."""
    if localStorage:
        try:
            dato_json = json.dumps(valor)
            localStorage.setItem(llave, dato_json)
        except:
            pass
    else:
        # Fallback para modo Online
        st.session_state[llave] = valor

def recuperar_del_dispositivo(llave):
    """Busca y recupera datos del celular aunque no haya internet."""
    if localStorage:
        try:
            dato_json = localStorage.getItem(llave)
            return json.loads(dato_json) if dato_json else None
        except:
            return None
    return st.session_state.get(llave, None)

def borrar_del_dispositivo(llave):
    """Limpia el maletín después de sincronizar con Google Sheets."""
    if localStorage:
        try:
            localStorage.removeItem(llave)
        except:
            pass
    elif llave in st.session_state:
        del st.session_state[llave]
