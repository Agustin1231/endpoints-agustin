from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import subprocess
import sys

app = FastAPI(title="Python Utils API")

# === Ejecutar código Python dinámico ===
class CodeRequest(BaseModel):
    code: str
    variables: dict = {}

@app.post("/execute")
def execute_code(request: CodeRequest):
    """Ejecuta código Python y retorna el resultado"""
    try:
        local_vars = request.variables.copy()
        exec(request.code, {"__builtins__": __builtins__}, local_vars)
        return {"success": True, "result": local_vars.get("result")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# === Instalar librerías en caliente ===
class InstallRequest(BaseModel):
    package: str

@app.post("/install")
def install_package(request: InstallRequest):
    """Instala un paquete pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", request.package])
        return {"success": True, "message": f"{request.package} instalado"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=str(e))

# === Endpoints específicos que vayas necesitando ===
@app.post("/pandas/process")
def process_with_pandas(data: dict):
    """Ejemplo: procesar datos con pandas"""
    import pandas as pd
    df = pd.DataFrame(data.get("rows", []))
    # Tu lógica aquí
    return {"columns": list(df.columns), "shape": df.shape}

@app.get("/health")
def health():
    return {"status": "ok"}