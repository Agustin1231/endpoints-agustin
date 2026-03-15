# Python Utils API (endpoints-agustin)

Esta es una API de utilidades basada en **FastAPI** diseñada para automatizar flujos de trabajo, manejar documentos PDF y realizar automatización de navegadores.

## Características Principales

- **Automatización de Navegador**: Soporte especializado para HubSpot (login, 2FA, extracción de reportes).
- **Procesamiento de PDF**: Conversión de HTML a PDF y unión (merge) de múltiples PDFs.
- **Herramientas de Imagen**: Limpieza de metadatos y eliminación de firmas de IA (C2PA/caBX) en archivos PNG y JPG.
- **Ejecución Dinámica**: Endpoints para instalar paquetes de Python y ejecutar código dinámicamente.

## Instalación y Uso

### Local
1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
3. Inicia el servidor:
   ```bash
   python main.py
   ```

### Docker
El proyecto incluye un `Dockerfile` para un despliegue rápido:
```bash
docker build -t python-utils-api .
docker run -p 8000:8000 python-utils-api
```

## Estructura del Proyecto

- `main.py`: Punto de entrada y configuración de FastAPI.
- `endpoints/`: Routers divididos por funcionalidad:
  - `browser.py`: Playwright y HubSpot logic.
  - `html_pdf.py`: Renderizado de PDF.
  - `pdf_tools.py`: Manipulación de archivos PDF.
  - `image_tools.py`: Procesamiento de imágenes y eliminación de metadatos.

## Notas para n8n
Los endpoints de imagen cuentan con versiones que aceptan y devuelven Base64 para facilitar su integración en flujos de n8n.
