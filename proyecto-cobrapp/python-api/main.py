from fastapi import FastAPI, UploadFile, File
import pytesseract
from PIL import Image
import cv2
import numpy as np
import io
import re
from datetime import datetime

app = FastAPI()

def preprocesar_imagen(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img   = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

def extraer_datos(texto):
    # Regex para buscar montos, números de operación y fechas [cite: 221, 222]
    monto = re.search(r'S/\.?\s*(\d+\.\d{2})', texto)
    oper  = re.search(r'Operaci[oó]n[:\s]+(\d+)', texto)
    fecha = re.search(r'(\d{2}/\d{2}/\d{4})', texto)
    
    return {
        "monto": monto.group(1) if monto else None,
        "operacion": oper.group(1) if oper else None,
        "fecha": fecha.group(1) if fecha else datetime.now().strftime('%d/%m/%Y'),
        "tipo": "Yape" if "yape" in texto.lower() else "Plin" if "plin" in texto.lower() else "Desconocido",
        "texto_raw": texto
    }

@app.post("/procesar-imagen")
async def procesar_imagen(file: UploadFile = File(...)):
    contenido = await file.read()
    img_proc  = preprocesar_imagen(contenido)
    # Importante: se requiere tener instalado tesseract en el sistema/contenedor [cite: 223]
    texto     = pytesseract.image_to_string(img_proc, lang='spa')
    datos     = extraer_datos(texto)
    datos["valido"] = datos["monto"] is not None
    return datos