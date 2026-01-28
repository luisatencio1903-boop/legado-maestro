import requests
import io
from PIL import Image
import streamlit as st

def comprimir_imagen(archivo_camara):
    """
    Comprime la imagen para ahorrar datos y espacio.
    Reduce el peso manteniendo la calidad (Tipo WhatsApp).
    """
    try:
        img = Image.open(archivo_camara)
        if img.mode in ("RGBA", "P"): 
            img = img.convert("RGB")
        
        # Redimensionar si es muy grande (max 800px)
        img.thumbnail((800, 800))
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70, optimize=True)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error comprimiendo: {e}")
        return None

def subir_a_imgbb(archivo_foto):
    """Sube la foto a ImgBB usando tu API KEY."""
    try:
        # TU API KEY ORIGINAL
        API_KEY = "3bc2c5bae6c883fdcdcc4da6ec4122bd"
        
        # 1. Comprimir primero
        foto_bytes_io = comprimir_imagen(archivo_foto)
        if not foto_bytes_io: return None
        
        foto_bytes = foto_bytes_io.getvalue()

        # 2. Enviar a ImgBB
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": API_KEY}
        files = {'image': foto_bytes}
        
        res = requests.post(url, payload, files=files)
        
        if res.status_code == 200:
            return res.json()['data']['url']
        else:
            return None
    except Exception as e:
        st.error(f"Error subida: {e}")
        return None
