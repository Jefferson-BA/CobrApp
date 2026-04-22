# 📱 CobrApp - Automatización de Pagos

CobrApp es un sistema inteligente diseñado para automatizar el registro de comprobantes de pago (Yape y Plin) enviados a través de Telegram. Utiliza Inteligencia Artificial (OCR) para extraer los datos clave de las imágenes y registrar la información automáticamente en Google Sheets mediante flujos de n8n, generando reportes diarios.

## 🚀 Funcionalidades

* **Procesamiento de imágenes:** Extracción precisa de texto (monto, fecha, operación, nombre) usando Tesseract OCR, tolerante a variaciones de formato y decimales.
* **API RESTful:** Desarrollada con FastAPI para la recepción de imágenes, consulta de pagos procesados y generación de reportes diarios.
* **Automatización de flujos:** Integración con Telegram (Bot) y Google Sheets vía **n8n**.
* **Notificaciones en tiempo real:** Confirmación automática de pagos exitosos y reportes de cierre de caja enviados al chat correspondiente.

## 📋 Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:
* [Python 3.9 o superior](https://www.python.org/downloads/)
* [Docker y Docker Compose](https://www.docker.com/) (para levantar n8n localmente)
* [ngrok](https://ngrok.com/) (para exponer los webhooks locales a internet)
* **Tesseract OCR** (versión para Windows)

## 🛠️ Instalación y Configuración

**1. Instalar Tesseract OCR**
Descarga e instala Tesseract OCR. Es estrictamente necesario que la ruta de instalación sea:
`C:\Program Files\Tesseract-OCR`

**2. Clonar el repositorio**
```bash
git clone [https://github.com/Jefferson-BA/CobrApp.git](https://github.com/Jefferson-BA/CobrApp.git)
cd TU_REPOSITORIO

3. Instalar dependencias de Python
Puedes instalar todas las dependencias usando el archivo de requerimientos:

Bash
pip install -r requirements.txt
(Alternativamente, puedes instalarlas manualmente: pip install fastapi uvicorn python-multipart pytesseract opencv-python Pillow numpy)

▶️ Ejecución del Proyecto
Para que el sistema funcione en su totalidad, debes levantar tres servicios en terminales diferentes:

Paso 1: Iniciar n8n (Automatización)
Levanta el contenedor de n8n usando Docker:

Bash
docker-compose up --build
n8n estará disponible en http://localhost:5678

Paso 2: Exponer n8n a Internet (ngrok)
Para que el bot de Telegram pueda enviar las imágenes a tu n8n local, debes exponer el puerto 5678:

Bash
ngrok http 5678
(Copia la URL segura https://...ngrok-free.app que te genera la terminal y actualízala en la configuración del webhook de tu bot si es necesario).

Paso 3: Iniciar la API de Python (Procesamiento OCR)
Levanta el servidor de FastAPI que se encargará de leer las imágenes:

Bash
uvicorn main:app --reload
La API estará escuchando en http://127.0.0.1:8000

📡 Rutas de la API (Endpoints)
POST /procesar-imagen: Recibe la imagen del comprobante y devuelve un JSON con los datos extraídos (monto, número de operación, cliente).

GET /pagos: Devuelve la lista en tiempo real de los pagos registrados durante el día.

GET /reporte: Calcula y devuelve la suma total del dinero recaudado en la jornada.

🔄 Flujos de n8n
En la carpeta del repositorio se incluyen los archivos .json exportados para importarlos directamente en tu entorno de n8n:

Registro de Pagos: Recibe foto de Telegram -> API Python -> Condicional IF -> Google Sheets -> Mensaje de confirmación.

Reporte Diario: Cron Trigger (23:59) -> Lee Google Sheets -> Suma Montos -> Envía reporte consolidado por Telegram.