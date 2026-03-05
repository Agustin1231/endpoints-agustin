from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from weasyprint import HTML, CSS

router = APIRouter()

class HTMLRequest(BaseModel):
    html: str
    filename: str = "document.pdf"
    page_size: str = "A4"  # A3, A4, A5, Letter, Legal
    base_url: Optional[str] = None
    custom_css: Optional[str] = None

@router.post("/html-to-pdf")
def html_to_pdf(request: HTMLRequest):
    """
    Convierte contenido HTML a un documento PDF.
    
    - **html**: El contenido HTML a convertir.
    - **filename**: Nombre del archivo PDF resultante.
    - **page_size**: Tamaño de la página (A4, Letter, etc.).
    - **base_url**: URL base para resolver recursos externos (imágenes, fuentes).
    - **custom_css**: Estilos CSS adicionales para aplicar al documento.
    """
    try:
        stylesheets = []
        
        # CSS para el tamaño de página
        page_css = CSS(string=f"@page {{ size: {request.page_size}; margin: 1cm; }}")
        stylesheets.append(page_css)
        
        # CSS personalizado si se proporciona
        if request.custom_css:
            stylesheets.append(CSS(string=request.custom_css))
            
        # Generar PDF
        pdf_bytes = HTML(string=request.html, base_url=request.base_url).write_pdf(stylesheets=stylesheets)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")