from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

router = APIRouter()

class HTMLRequest(BaseModel):
    html: str
    filename: str = "document.pdf"

@router.post("/html-to-pdf")
def html_to_pdf(request: HTMLRequest):
    from weasyprint import HTML
    pdf_bytes = HTML(string=request.html).write_pdf()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={request.filename}"}
    )