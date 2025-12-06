from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
import io

class PDFService:
    async def extract_text_from_upload(self, file: UploadFile) -> str:
        """
        Lee un archivo PDF subido vía HTTP y extrae su texto.
        """
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
        
        try:
            # Leemos el archivo en memoria
            content = await file.read()
            
            # Usamos pypdf para leer el stream de bytes
            pdf_reader = PdfReader(io.BytesIO(content))
            
            text = ""
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            if not text.strip():
                raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF (quizás es una imagen escaneada)")
                
            return text
            
        except Exception as e:
            print(f"Error leyendo PDF: {e}")
            raise HTTPException(status_code=500, detail="Error procesando el archivo PDF")

pdf_service = PDFService()