import base64
import io
from PIL import Image

def foto_a_texto(archivo_foto):
    if archivo_foto is None:
        return None
    try:
        if isinstance(archivo_foto, str):
            return archivo_foto
        bytes_data = archivo_foto.getvalue()
        base64_str = base64.b64encode(bytes_data).decode('utf-8')
        return f"data:image/jpeg;base64,{base64_str}"
    except:
        return None

def texto_a_foto(base64_str):
    if base64_str is None or not base64_str.startswith('data:image'):
        return None
    try:
        header, encoded = base64_str.split(",", 1)
        data = base64.b64decode(encoded)
        return io.BytesIO(data)
    except:
        return None
