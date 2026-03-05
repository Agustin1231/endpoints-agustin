import uuid
import base64
import asyncio
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page

router = APIRouter(prefix="/browser", tags=["Browser"])

# Global storage for persistent sessions
class SessionManager:
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.sessions: Dict[str, Dict[str, Any]] = {}

    async def init_browser(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)

manager = SessionManager()


class StartHubspotLoginRequest(BaseModel):
    email: str = "agustin@naranjamedia.co"
    password: str = "naranja123@2026"

class SessionResponse(BaseModel):
    session_id: str
    status: str
    message: str
    screenshot_base64: Optional[str] = None


@router.post("/hubspot/login/start", response_model=SessionResponse)
async def start_hubspot_login(request: StartHubspotLoginRequest):
    """
    Paso 1: Inicia el flujo de login en HubSpot usando Google. 
    Llega hasta la pantalla de ingreso del código 2FA.
    Retorna un session_id para mantener la sesión viva.
    """
    await manager.init_browser()
    
    session_id = str(uuid.uuid4())
    context = await manager.browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    )
    page = await context.new_page()
    
    manager.sessions[session_id] = {
        "context": context,
        "page": page
    }
    
    try:
        # 1. Navegar a HubSpot
        await page.goto("https://app.hubspot.com/login", wait_until="networkidle")
        
        # 2. Llenar email en HubSpot y presionar Enter
        await page.wait_for_selector('input[type="email"]', timeout=10000)
        await page.fill('input[type="email"]', request.email)
        await page.press('input[type="email"]', 'Enter')
        await asyncio.sleep(3)
        
        # 3. Click en "Iniciar sesión con Google"
        try:
            await page.wait_for_selector('button:has-text("Google")', timeout=5000)
            await page.click('button:has-text("Google")')
            await asyncio.sleep(4) # Esperamos que abra / redirija a Google
        except Exception:
            raise HTTPException(status_code=400, detail="Botón de Google no encontrado en HubSpot")

        # 4. Google Login: Email
        await page.wait_for_selector('input[type="email"]', timeout=10000)
        await page.fill('input[type="email"]', request.email)
        await page.press('input[type="email"]', 'Enter')
        await asyncio.sleep(3)
        
        # 5. Google Login: Password
        await page.wait_for_selector('input[type="password"]', timeout=10000)
        await page.fill('input[type="password"]', request.password)
        await page.press('input[type="password"]', 'Enter')
        await asyncio.sleep(5) # Esperar a que procese y pida 2FA
        
        # 6. Estamos en la pantalla de 2FA. Tomar screenshot para ver qué pide.
        png_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(png_bytes).decode("utf-8")
        
        return SessionResponse(
            session_id=session_id,
            status="awaiting_code",
            message="Esperando el código de verificación de Google. Revisa el screenshot devuelto para ver qué tipo de código/acción pide Google.",
            screenshot_base64=screenshot_b64
        )
        
    except Exception as e:
        # Si falla, limpiamos
        await context.close()
        if session_id in manager.sessions:
            del manager.sessions[session_id]
        raise HTTPException(status_code=500, detail=f"Error en flujo de login: {str(e)}")


class SubmitCodeRequest(BaseModel):
    session_id: str
    code: str

@router.post("/hubspot/login/submit-code", response_model=SessionResponse)
async def submit_hubspot_code(request: SubmitCodeRequest):
    """
    Paso 2: Recibe el código 2FA y lo ingresa en la sesión activa de Google.
    """
    if request.session_id not in manager.sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada o ya cerrada")
        
    session_data = manager.sessions[request.session_id]
    page = session_data["page"]
    
    try:
        # Los inputs de código en Google suelen ser type="tel" o no tienen type pero sí id
        # Buscamos de forma genérica el primer input visible que parece ser el código
        input_selector = 'input[type="tel"], input[name="Pin"], input[autocomplete="one-time-code"], input[type="text"]'
        
        try:
            await page.wait_for_selector(input_selector, timeout=5000)
            await page.fill(input_selector, request.code)
            await page.press(input_selector, 'Enter')
            await asyncio.sleep(6) # Esperar a que pase el 2FA e inicie sesión en HubSpot
        except Exception:
            # Si no encuentra el input estándar
            png_bytes = await page.screenshot()
            screenshot_b64 = base64.b64encode(png_bytes).decode("utf-8")
            raise HTTPException(status_code=400, detail=f"No se encontró el campo para ingresar el código. Screenshot actualizado en log.", headers={"X-Screenshot-Base64": screenshot_b64})
        
        # Tomar screenshot del resultado (debería ser el dashboard de HubSpot o similar)
        png_bytes_final = await page.screenshot()
        screenshot_b64_final = base64.b64encode(png_bytes_final).decode("utf-8")
        
        return SessionResponse(
            session_id=request.session_id,
            status="logged_in",
            message="Código ingresado. Revisa el screenshot para confirmar si inició sesión correctamente en HubSpot.",
            screenshot_base64=screenshot_b64_final
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar código: {str(e)}")


class ReportRequest(BaseModel):
    session_id: str
    url: str

class ReportResponse(BaseModel):
    session_id: str
    status: str
    performance_html: str
    recipients_html: str
    screenshot_performance_base64: Optional[str] = None
    screenshot_recipients_base64: Optional[str] = None

@router.post("/hubspot/report/email", response_model=ReportResponse)
async def get_hubspot_email_report(request: ReportRequest):
    """
    Paso 3: Usando una sesión ya logueada, navega a un reporte de email de HubSpot.
    Extrae el HTML del reporte de rendimiento (Performance), 
    luego hace click en la pestaña 'Destinatarios', y extrae el HTML nuevamente.
    """
    if request.session_id not in manager.sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada o ya cerrada")
        
    session_data = manager.sessions[request.session_id]
    page = session_data["page"]
    
    try:
        # 1. Navegar a la URL del reporte
        await page.goto(request.url, wait_until="networkidle", timeout=45000)
        await asyncio.sleep(5)  # Dar tiempo extra para que carguen los gráficos de HubSpot
        
        # Tomar HTML y screenshot de la vista principal (Performance)
        performance_html = await page.content()
        png_perf = await page.screenshot(full_page=True)
        screenshot_perf = base64.b64encode(png_perf).decode("utf-8")
        
        # 2. Hacer click en "Destinatarios" (Recipients)
        # Intentamos buscar un elemento que contenga el texto "Destinatarios" 
        # (puede ser un span, div o a dentro de una pestaña)
        try:
            # Seleccionamos un elemento clickeable que tenga texto "Destinatarios"
            # O equivalentemente en el DOM de HubSpot:
            dest_selector = 'text="Destinatarios"'
            await page.wait_for_selector(dest_selector, timeout=10000)
            await page.click(dest_selector)
        except Exception:
            # Si el idioma está en inglés podría decir "Recipients"
            try:
                dest_selector_en = 'text="Recipients"'
                await page.wait_for_selector(dest_selector_en, timeout=5000)
                await page.click(dest_selector_en)
            except Exception:
                raise HTTPException(status_code=400, detail="No se pudo encontrar la pestaña 'Destinatarios' o 'Recipients'.")

        # Esperar a que cargue la tabla de destinatarios
        await asyncio.sleep(5)
        await page.wait_for_load_state("networkidle")
        
        # Tomar HTML y screenshot de la vista de Destinatarios
        recipients_html = await page.content()
        png_recip = await page.screenshot(full_page=True)
        screenshot_recip = base64.b64encode(png_recip).decode("utf-8")
        
        return ReportResponse(
            session_id=request.session_id,
            status="success",
            performance_html=performance_html,
            recipients_html=recipients_html,
            screenshot_performance_base64=screenshot_perf,
            screenshot_recipients_base64=screenshot_recip
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo reporte: {str(e)}")

class NavigateRequest(BaseModel):
    url: str
    wait_until: str = "networkidle"
    screenshot: bool = True
    full_page: bool = False

class NavigateResponse(BaseModel):
    url: str
    title: str
    status: Optional[int] = None
    screenshot_base64: Optional[str] = None

@router.post("/navigate", response_model=NavigateResponse)
async def browser_navigate(request: NavigateRequest):
    """Endpoint general genérico (refactorizado a async)."""
    await manager.init_browser()
    context = await manager.browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    )
    page = await context.new_page()
    
    try:
        response = await page.goto(request.url, wait_until=request.wait_until, timeout=30000)
        status_code = response.status if response else None

        title = await page.title()
        final_url = page.url

        screenshot_b64 = None
        if request.screenshot:
            png_bytes = await page.screenshot(full_page=request.full_page)
            screenshot_b64 = base64.b64encode(png_bytes).decode("utf-8")

        await context.close()
        return NavigateResponse(
            url=final_url,
            title=title,
            status=status_code,
            screenshot_base64=screenshot_b64,
        )
    except Exception as e:
        await context.close()
        raise HTTPException(status_code=500, detail=f"Browser error: {str(e)}")
