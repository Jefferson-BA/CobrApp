from fastapi import FastAPI, UploadFile, File
import pytesseract
from PIL import Image
import cv2
import numpy as np
import io
import re
from datetime import datetime
import os
import json  # <-- Importante para poder guardar y leer el archivo de pagos

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
    # El monto ahora acepta "s 80", "S/ 80.00", "S 0,10", etc.
    monto = re.search(r'[sS5][/\\]?\s*(\d+(?:[.,]\d+)?)', texto)
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
    
    # NUEVO: Si el pago es válido, lo guardamos en un archivo local (pagos.json)
    if datos["valido"]:
        pagos_guardados = []
        # Leemos los pagos anteriores si el archivo existe
        if os.path.exists("pagos.json"):
            with open("pagos.json", "r", encoding="utf-8") as f:
                try:
                    pagos_guardados = json.load(f)
                except:
                    pass
        # Agregamos el nuevo pago procesado
        pagos_guardados.append(datos)
        # Guardamos el archivo actualizado
        with open("pagos.json", "w", encoding="utf-8") as f:
            json.dump(pagos_guardados, f, ensure_ascii=False, indent=4)

    return datos

@app.get("/pagos")
async def obtener_pagos():
    # Ahora lee los datos REALES que Python ha procesado
    pagos_guardados = []
    if os.path.exists("pagos.json"):
        with open("pagos.json", "r", encoding="utf-8") as f:
            try:
                pagos_guardados = json.load(f)
            except:
                pass
    
    return {
        "fecha": datetime.now().strftime('%d/%m/%Y'),
        "total_registros": len(pagos_guardados),
        "pagos": pagos_guardados,
        "mensaje": "Lista de pagos reales consultada con éxito"
    }

@app.get("/reporte")
async def obtener_reporte():
    # Calcula el total real sumando los montos guardados
    total = 0.0
    if os.path.exists("pagos.json"):
        with open("pagos.json", "r", encoding="utf-8") as f:
            try:
                pagos_guardados = json.load(f)
                # Sumamos todos los montos convirtiéndolos a float 
                # (reemplazamos coma por punto por si el OCR leyó "80,00")
                total = sum(float(p["monto"].replace(",", ".")) for p in pagos_guardados if p.get("monto"))
            except:
                pass
                
    return {
        "fecha": datetime.now().strftime('%d/%m/%Y'),
        "total_recaudado": round(total, 2),
        "mensaje": "Reporte diario real generado con éxito"
    }