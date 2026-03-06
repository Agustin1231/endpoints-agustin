from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List
from pypdf import PdfWriter
import io
import base64

router = APIRouter()

class MergeRequest(BaseModel):
    files: List[str]  # Lista de strings en base64

@router.post("/merge-pdfs")
async def merge_pdfs(request: MergeRequest):
    """
    Combina múltiples archivos PDF proporcionados como strings en Base64 en uno solo.
    
    - **files**: Lista de strings en Base64 que representan los archivos PDF a combinar.
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="No se proporcionaron archivos.")

    try:
        merger = PdfWriter()

        for base64_file in request.files:
            try:
                # Decodificar el base64
                file_content = base64.b64decode(base64_file)
                pdf_stream = io.BytesIO(file_content)
                merger.append(pdf_stream)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error decodificando uno de los archivos Base64: {str(e)}")

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
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error merging PDFs: {str(e)}")
