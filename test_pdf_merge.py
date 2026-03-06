import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def generate_pdf(name, content):
    print(f"Generando PDF {name}...")
    payload = {
        "html": f"<h1>Documento {name}</h1><p>{content}</p>",
        "filename": f"{name}.pdf"
    }
    response = requests.post(f"{BASE_URL}/html-to-pdf", json=payload)
    if response.status_code == 200:
        with open(f"{name}.pdf", "wb") as f:
            f.write(response.content)
        return f"{name}.pdf"
    else:
        print(f"Error generando {name}: {response.text}")
        return None

def test_merge():
    # 1. Generar 3 PDFs
    files_to_merge = []
    for char in ['A', 'B', 'C']:
        pdf_path = generate_pdf(f"informe_{char}", f"Este es el contenido del informe {char}.")
        if pdf_path:
            files_to_merge.append(pdf_path)
    
    if len(files_to_merge) < 3:
        print("No se pudieron generar todos los PDFs.")
        return

    # 2. Hacer merge
    print("Enviando archivos para merge...")
    files = [('files', (f, open(f, 'rb'), 'application/pdf')) for f in files_to_merge]
    
    response = requests.post(f"{BASE_URL}/merge-pdfs", files=files)
    
    # Cerrar archivos
    for _, (_, f_obj, _) in files:
        f_obj.close()
    
    # 3. Verificar resultado
    if response.status_code == 200:
        output_file = "informe_merged.pdf"
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Merge exitoso! Guardado en: {output_file}")
        
        # Opcional: limpiar archivos temporales
        for f in files_to_merge:
            os.remove(f)
    else:
        print(f"Error en merge: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_merge()
