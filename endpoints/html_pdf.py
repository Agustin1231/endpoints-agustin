from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from playwright.sync_api import sync_playwright

router = APIRouter()

# Mapeo de tamaños de página a formato Playwright
PAGE_SIZES = {
    "A3": {"width": "297mm", "height": "420mm"},
    "A4": {"width": "210mm", "height": "297mm"},
    "A5": {"width": "148mm", "height": "210mm"},
    "Letter": {"width": "8.5in", "height": "11in"},
    "Legal": {"width": "8.5in", "height": "14in"},
}

class HTMLRequest(BaseModel):
    html: str
    filename: str = "document.pdf"
    page_size: str = "A4"  # A3, A4, A5, Letter, Legal
    base_url: Optional[str] = None
    custom_css: Optional[str] = None

@router.post("/html-to-pdf")
def html_to_pdf(request: HTMLRequest):
    """
    Convierte contenido HTML a un documento PDF usando Playwright (Chromium).
    
    - **html**: El contenido HTML a convertir.
    - **filename**: Nombre del archivo PDF resultante.
    - **page_size**: Tamaño de la página (A4, Letter, etc.).
    - **base_url**: URL base para resolver recursos externos (imágenes, fuentes).
    - **custom_css**: Estilos CSS adicionales para aplicar al documento.
    """
    try:
        size = PAGE_SIZES.get(request.page_size, PAGE_SIZES["A4"])

        # Inyectar CSS personalizado en el HTML si se proporciona
        html_content = request.html
        if request.custom_css:
            html_content = f"<style>{request.custom_css}</style>\n{html_content}"

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            if request.base_url:
                page.goto(request.base_url)
                page.set_content(html_content, wait_until="networkidle")
            else:
                page.set_content(html_content, wait_until="networkidle")

            pdf_bytes = page.pdf(
                format=request.page_size if request.page_size in ["A3", "A4", "A5", "Letter", "Legal"] else "A4",
                margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
                print_background=True,
            )
            browser.close()

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")