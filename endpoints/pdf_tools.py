from fastapi import APIRouter, HTTPException, Response, UploadFile, File
from typing import List
from pypdf import PdfWriter
import io

router = APIRouter()

@router.post("/merge-pdfs")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    """
    Combina múltiples archivos PDF en uno solo.
    
    - **files**: Lista de archivos PDF a combinar (multipart/form-data).
    """
    if not files:
        raise HTTPException(status_code=400, detail="No se proporcionaron archivos.")

    try:
        merger = PdfWriter()

        for file in files:
            # Leer el contenido del archivo subido
            content = await file.read()
            # Crear un stream de bytes para pypdf
            pdf_stream = io.BytesIO(content)
            # Añadir al merger
            merger.append(pdf_stream)

        # Guardar el resultado en un stream de bytes
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merged_pdf_bytes = output_stream.getvalue()
        
        merger.close()

        return Response(
            content=merged_pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=informe_merged.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging PDFs: {str(e)}")
