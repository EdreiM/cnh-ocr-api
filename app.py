from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import fitz
import pytesseract
from PIL import Image
import tempfile
import os
import re

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API CNH OCR rodando"}

@app.post("/ler-cnh")
async def ler_cnh(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "documento.pdf")
        image_path = os.path.join(temp_dir, "pagina.png")

        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=300)
        pix.save(image_path)
        doc.close()

        imagem = Image.open(image_path)
        texto = pytesseract.image_to_string(imagem, lang="por")

        cpf = re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", texto)
        datas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)

        return JSONResponse(content={
            "cpf": cpf.group() if cpf else None,
            "datas_encontradas": datas,
            "texto_completo": texto
        })
