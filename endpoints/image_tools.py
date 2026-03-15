from fastapi import APIRouter, HTTPException, UploadFile, File, Response
from PIL import Image
import io

router = APIRouter(prefix="/image", tags=["Image Tools"])

@router.post("/strip-metadata")
async def strip_metadata(file: UploadFile = File(...)):
    """
    Recibe una imagen (PNG/JPG/etc) y elimina toda su metadata (EXIF, Chunks de IA como caBX/C2PA).
    Retorna el binario de la imagen limpia.
    """
    try:
        # Leer el contenido del archivo subido
        content = await file.read()
        img = Image.open(io.BytesIO(content))
        
        # Preparar buffer para la salida
        output = io.BytesIO()
        
        # Al guardar con Pillow, si no pasamos el argumento 'pnginfo' o 'exif', 
        # la mayoría de la metadata se descarta automáticamente.
        # 'optimize=True' ayuda a reconstruir el archivo de forma limpia.
        img_format = img.format if img.format else "PNG"
        
        # Forzar la eliminación de metadata guardando solo los datos de la imagen
        img.save(output, format=img_format, optimize=True)
        
        cleaned_content = output.getvalue()
        
        return Response(
            content=cleaned_content,
            media_type=f"image/{img_format.lower()}",
            headers={"Content-Disposition": f"attachment; filename=cleaned_{file.filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la imagen: {str(e)}")

@router.post("/strip-metadata-base64")
async def strip_metadata_base64(data: dict):
    """
    Versión que recibe y entrega Base64 para flujos tipo n8n que prefieran JSON.
    Esperado: {"image_base64": "...", "filename": "test.png"}
    """
    import base64
    try:
        b64_str = data.get("image_base64")
        filename = data.get("filename", "image.png")
        
        if not b64_str:
            raise HTTPException(status_code=400, detail="Falta image_base64")
            
        content = base64.b64decode(b64_str)
        img = Image.open(io.BytesIO(content))
        
        output = io.BytesIO()
        img_format = img.format if img.format else "PNG"
        img.save(output, format=img_format, optimize=True)
        
        cleaned_b64 = base64.b64encode(output.getvalue()).decode("utf-8")
        
        return {
            "success": True,
            "filename": f"cleaned_{filename}",
            "image_base64": cleaned_b64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando base64: {str(e)}")
