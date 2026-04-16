from fastapi import FastAPI, UploadFile, File
import pytesseract
from PIL import Image
import cv2
import numpy as np
import io
import re
from datetime import datetime
import os  # <-- Agregamos esto

# 1. Le decimos dónde está el programa ejecutable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 2. Le decimos dónde está la carpeta de idiomas (tessdata)
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

app = FastAPI()

def preprocesar_imagen(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def extraer_datos(texto):
    # Usamos re.IGNORECASE para ignorar mayúsculas y minúsculas
    # El monto ahora acepta "s 80", "S/ 80.00", etc.
    monto = re.search(r'[sS][/\\]?\s*(\d+(?:\.\d+)?)', texto)
    oper  = re.search(r'operaci[oó]n\s*(\d+)', texto, re.IGNORECASE)
    
    # Extraer el nombre (suele estar en la 3ra línea de texto en Yape)
    lineas = [linea.strip() for linea in texto.split('\n') if linea.strip()]
    nombre = "Desconocido"
    # Si detectamos que hay suficientes líneas, el nombre suele estar en la posición 2
    if len(lineas) > 2:
        nombre = lineas[2]

    return {
        "monto": monto.group(1) if monto else None,
        "operacion": oper.group(1) if oper else None,
        "nombre": nombre,
        "fecha": datetime.now().strftime('%d/%m/%Y'), # Usamos la fecha de registro actual
        "tipo": "Yape" if "yape" in texto.lower() else "Plin" if "plin" in texto.lower() else "Desconocido",
        "texto_raw": texto
    }

@app.post("/procesar-imagen")
async def procesar_imagen(file: UploadFile = File(...)):
    contenido = await file.read()
    img_proc  = preprocesar_imagen(contenido)
    
    # Lo regresamos a su forma original, ya que ahora Python sabe dónde buscar
    texto     = pytesseract.image_to_string(img_proc, lang='spa')
    
    datos     = extraer_datos(texto)
    datos["valido"] = datos["monto"] is not None
    return datos