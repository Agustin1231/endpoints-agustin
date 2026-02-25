from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from weasyprint import HTML, CSS

router = APIRouter()

class HTMLRequest(BaseModel):
    html: str
    filename: str = "document.pdf"
    page_size: str = "A4"  # A3, A4, A5, Letter, Legal

@router.post("/html-to-pdf")
def html_to_pdf(request: HTMLRequest):
    from weasyprint import HTML, CSS
    
    # CSS para el tamaño de página
    page_css = CSS(string=f"@page {{ size: {request.page_size}; margin: 1cm; }}")
    
    pdf_bytes = HTML(string=request.html).write_pdf(stylesheets=[page_css])
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={request.filename}"}
    )