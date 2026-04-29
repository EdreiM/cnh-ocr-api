from fastapi import FastAPI, UploadFile, File, HTTPException
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
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_path = os.path.join(temp_dir, "documento.pdf")
        image_path = os.path.join(temp_dir, "pagina.png")

        with open(pdf_path, "wb") as f:
            f.write(await file.read())

        try:
            doc = fitz.open(pdf_path)

            if len(doc) == 0:
                raise HTTPException(status_code=400, detail="PDF vazio.")

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

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
