<div align="center">

# 🤖 CobrApp
### Automatización Inteligente de Comprobantes de Pago

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram_Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)

*Sistema que automatiza la recepción, validación y registro de comprobantes Yape/Plin enviados por Telegram, usando OCR con Inteligencia Artificial y flujos de automatización con n8n.*

[Ver Demo](#-demo) · [Instalación](#%EF%B8%8F-instalación-y-configuración) · [Documentación](#-documentación)

</div>

---

## 📌 ¿Qué problema resuelve?

En muchos negocios, verificar los pagos de Yape/Plin es un proceso **manual, lento y propenso a errores**: el cliente envía una captura de pantalla, y alguien debe revisar, leer y registrar el monto a mano.

**CobrApp elimina ese proceso por completo.** El cliente envía la foto del comprobante al bot de Telegram y el sistema se encarga de todo lo demás en segundos.

```
Cliente envía foto  →  OCR extrae los datos  →  Se registra en Google Sheets  →  Se confirma al cliente
```

---

## 🎬 Demo

| Entregable | Enlace |
|---|---|
| 🎥 Video demostrativo | [Ver el sistema en funcionamiento](https://drive.google.com/file/d/1LBTO6EHhb-VKeRSmTCGcLh-IzO-IlF-w/view?usp=sharing) |
| 📄 Informe Técnico | [Descargar PDF](proyecto-cobrapp/evidencias/CobrApp_Informe_Tecnico.pdf) |
| 📊 Base de Datos (Pruebas) | [Ver Google Sheets](https://docs.google.com/spreadsheets/d/1zEEF8Zi0-QSa1dnvseMA9dcEQEq3OHwV8a1pm3aa1WM/edit?usp=sharing) |

---

## ✨ Funcionalidades

- **🔍 OCR con IA** — Extrae automáticamente el monto, número de operación, nombre y fecha del comprobante usando Tesseract OCR + Expresiones Regulares tolerantes a errores de lectura.
- **✅ Validación inteligente** — Rechaza imágenes que no son comprobantes (fotos borrosas, memes) y notifica al usuario con un mensaje amigable.
- **💾 Registro automático** — Guarda los pagos validados en Google Sheets sin intervención humana.
- **👤 Confirmación personalizada** — Responde al cliente saludándolo por su nombre de Telegram.
- **📊 Reporte diario** — Envía automáticamente el resumen de caja al administrador a las 23:59 (hora Lima).
- **🐳 Dockerizable** — Preparado para desplegarse en un VPS en la nube (AWS EC2, DigitalOcean).

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────┐     imagen      ┌──────────────┐     webhook     ┌──────────────────┐
│   Cliente   │ ─────────────▶  │  Bot Telegram │ ─────────────▶  │   n8n (Docker)   │
└─────────────┘                 └──────────────┘                  └────────┬─────────┘
                                                                           │ POST multipart
                                                                           ▼
                                                                  ┌──────────────────┐
                                                                  │  FastAPI + Uvicorn│
                                                                  │  ┌─────────────┐ │
                                                                  │  │ OpenCV      │ │
                                                                  │  │ Tesseract   │ │
                                                                  │  │ Regex       │ │
                                                                  │  └─────────────┘ │
                                                                  └────────┬─────────┘
                                                                           │ JSON {valido: true}
                                                              ┌────────────┴────────────┐
                                                              ▼                         ▼
                                                     ┌──────────────┐        ┌─────────────────┐
                                                     │ Google Sheets│        │ Mensaje de error │
                                                     │ (Append Row) │        │ al cliente       │
                                                     └──────────────┘        └─────────────────┘
```

### Stack Tecnológico

| Capa | Tecnología | Función |
|---|---|---|
| Interfaz de usuario | `Bot de Telegram` | Canal de comunicación con el cliente |
| Orquestador | `n8n` (Docker) | Coordinación de los flujos de trabajo |
| Túnel HTTP | `ngrok` | Expone el webhook local a internet |
| Backend / API | `FastAPI` + `Uvicorn` | Motor de procesamiento y endpoints REST |
| IA / OCR | `Tesseract OCR` (`spa`) | Extracción de texto desde imágenes |
| Preprocesamiento | `OpenCV` + `Pillow` | Mejora de imagen antes del OCR |
| Base de datos | `Google Sheets` (vía n8n) | Almacenamiento de pagos registrados |

---

## 🔄 Flujos de Trabajo (Workflows n8n)

### Flujo 1 — Registro de Pago en Tiempo Real

```
Telegram Trigger
     │
     ▼
Indicador "Escribiendo..." (UX)
     │
     ▼
HTTP Request → POST /procesar-imagen (FastAPI)
     │
     ▼
 ┌───┴───┐
 IF valido?
 │       │
YES      NO
 │       │
 ▼       ▼
Google  Mensaje
Sheets  de Error
Append  al Cliente
 │
 ▼
Telegram: Confirmación
"¡Gracias, {nombre}! Tu pago de S/.{monto} fue registrado."
```

### Flujo 2 — Reporte Diario Automatizado

```
Schedule Trigger (23:59 - America/Lima)
     │
     ▼
Google Sheets → Leer todos los registros del día
     │
     ▼
Calcular suma total recaudada
     │
     ▼
Telegram → Enviar resumen de caja al administrador
```

---

## 📡 Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/procesar-imagen` | Recibe la imagen del comprobante (`multipart/form-data`) y retorna un JSON con los datos extraídos y el campo `valido`. |
| `GET` | `/pagos` | Lista todos los pagos registrados en `pagos.json` con el total de registros. |
| `GET` | `/reporte` | Calcula y retorna el monto total recaudado del día. |

**Ejemplo de respuesta `/procesar-imagen`:**
```json
{
  "monto": "80.00",
  "operacion": "123456789",
  "nombre": "Juan Pérez",
  "fecha": "15/05/2025",
  "tipo": "Yape",
  "valido": true,
  "texto_raw": "..."
}
```

---

## 📂 Estructura del Proyecto

```
📁 CobrApp/
 ├── 📁 flujos_n8n/
 │    ├── flujo_n8n_CobrApp.json          # Flujo de registro de pagos
 │    └── Reporte Diario CobrApp.json     # Flujo del reporte automático
 ├── 📁 python-api/
 │    ├── main.py                         # API FastAPI + lógica OCR
 │    ├── requirements.txt                # Dependencias de Python
 │    └── docker-compose.yml             # Configuración de Docker para n8n
 ├── 📁 evidencias/
 │    └── Informe_Tecnico_CobrApp.pdf     # Documentación técnica completa
 └── README.md
```

---

## 📋 Requisitos Previos

Asegúrate de tener instalado lo siguiente antes de continuar:

- [Python 3.9+](https://www.python.org/downloads/)
- [Docker y Docker Compose](https://www.docker.com/products/docker-desktop)
- [ngrok](https://ngrok.com/download)
- [Tesseract OCR para Windows](https://github.com/UB-Mannheim/tesseract/wiki) — instalar en `C:\Program Files\Tesseract-OCR`

---

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Jefferson-BA/CobrApp.git
cd CobrApp/python-api
```

### 2. Instalar Tesseract OCR

Descarga e instala [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki). Durante la instalación, selecciona el paquete de idioma **Spanish**.

La ruta por defecto debe ser:
```
C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 3. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución del Proyecto

El sistema requiere **tres servicios activos en paralelo**. Abre tres terminales distintas:

**Terminal 1 — Levantar n8n con Docker:**
```bash
docker-compose up
# n8n estará disponible en http://localhost:5678
```

**Terminal 2 — Exponer el webhook con ngrok:**
```bash
ngrok http 5678
# Copia la URL https://...ngrok-free.app y actualízala en el webhook de Telegram en n8n
```

**Terminal 3 — Iniciar la API de Python:**
```bash
python -m uvicorn main:app --reload
# La API estará escuchando en http://127.0.0.1:8000
```

### 4. Importar los flujos en n8n

1. Accede a `http://localhost:5678`
2. Ve a **Workflows → Import from file**
3. Importa los dos archivos `.json` de la carpeta `flujos_n8n/`

---

## 🧠 Decisiones Técnicas Clave

**¿Por qué FastAPI y no Flask?**
FastAPI ofrece soporte asíncrono nativo, validación automática con Pydantic y documentación interactiva en `/docs` sin configuración adicional, lo que acelera el desarrollo y las pruebas.

**¿Por qué Tesseract OCR y no Google Vision?**
Tesseract es 100% open source (Apache 2.0), costo operativo cero y los datos de los comprobantes no salen del servidor, garantizando la privacidad financiera del negocio.

**¿Por qué Google Sheets como base de datos?**
Para el contexto de una pyme, Google Sheets ofrece accesibilidad inmediata sin software especializado, integración nativa con n8n y costo cero, con posibilidad de migrar a PostgreSQL en una fase posterior.

---

## 🐛 Dificultades Técnicas Resueltas

| Problema | Solución |
|---|---|
| Tesseract confundía `S/.` con `5` al leer montos | Regex tolerante: `r'[sS5][/\\]?\s*(\d+(?:[.,]\d+)?)'` — busca el patrón numérico sin depender del símbolo exacto |
| Registro de datos nulos si la imagen no era un comprobante | Campo `valido` booleano en la API + Nodo IF en n8n que desvía el flujo antes de escribir en Sheets |
| Error `Can't get data for expression` al obtener el nombre del usuario | Referencia absoluta al nodo origen: `{{ $('Telegram Trigger1').item.json.message.from.first_name }}` |
| Reporte diario ejecutándose en horario UTC en vez de Lima | Zona horaria del flujo configurada explícitamente a `America/Lima (UTC-05:00)` en n8n |

---

## 📄 Documentación

El informe técnico académico completo (arquitectura, flujos, análisis de dificultades y conclusiones) está disponible en:

```
📁 evidencias/Informe_Tecnico_CobrApp.pdf
```

---

## 🚀 Despliegue en la Nube (Futuro)

El proyecto está estructurado para migrar a producción con un solo comando:

```bash
# En un VPS Ubuntu (AWS EC2 capa gratuita / DigitalOcean)
git clone https://github.com/Jefferson-BA/CobrApp.git
cd CobrApp/python-api
docker-compose up -d
```

---

## 📜 Licencia

Distribuido bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

---

<div align="center">
  Desarrollado como proyecto universitario · Ingeniería de Software · 2025
</div>