import requests
import os
import base64

BASE_URL = "http://127.0.0.1:8000"

def generate_pdf(name, content):
    print(f"Generando PDF {name}...")
    payload = {
        "html": f"<h1>Documento {name}</h1><p>{content}</p>",
        "filename": f"{name}.pdf"
    }
    response = requests.post(f"{BASE_URL}/html-to-pdf", json=payload)
    if response.status_code == 200:
        return response.content  # Retorna los bytes del PDF
    else:
        print(f"Error generando {name}: {response.text}")
        return None

def test_merge_base64():
    # 1. Generar 3 PDFs y obtener sus bytes
    pdf_contents = []
    for char in ['A', 'B', 'C']:
        content = generate_pdf(f"informe_{char}", f"Este es el contenido del informe {char}.")
        if content:
            # Convertir a base64 string
            b64_str = base64.b64encode(content).decode('utf-8')
            pdf_contents.append(b64_str)
    
    if len(pdf_contents) < 3:
        print("No se pudieron generar todos los PDFs.")
        return

    # 2. Hacer merge enviando la lista de base64
    print("Enviando lista de Base64 para merge...")
    payload = {
        "files": pdf_contents
    }
    
    response = requests.post(f"{BASE_URL}/merge-pdfs", json=payload)
    
    # 3. Verificar resultado
    if response.status_code == 200:
        output_file = "informe_merged_base64.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Merge Base64 exitoso! Guardado en: {output_file}")
    else:
        print(f"Error en merge Base64: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_merge_base64()
