from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
import os
import shutil
import traceback

from config import UPLOAD_DIR, OUTPUT_DIR, SAMPLE_FORMS_DIR, PORT
from models import ExtractedData, FillRequest, URLFillRequest
from extractor import extract_text_from_pdf, extract_text_from_image, extract_data_from_text, merge_data
from filler import fill_pdf, fill_url

app = FastAPI(title="AI Form Filler API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "AI Form Filler API is running!",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/upload-documents")
async def upload_documents(
    documents: List[UploadFile] = File(...),
    documentType: str = Form(...)
):
    try:
        print(f"\n{'='*60}")
        print(f"Processing {len(documents)} document(s) of type: {documentType}")
        print(f"{'='*60}\n")
        
        # Ensure upload directory exists
        os.makedirs(os.path.join(UPLOAD_DIR, "documents"), exist_ok=True)
        
        uploaded_files = []
        extracted_data_list = []
        
        for i, doc in enumerate(documents):
            print(f"\n--- Document {i+1}: {doc.filename} ---")
            
            file_path = os.path.join(UPLOAD_DIR, "documents", doc.filename)
            
            # Save uploaded file
            with open(file_path, "wb") as f:
                content = await doc.read()
                f.write(content)
            
            print(f"Saved to: {file_path}")
            uploaded_files.append({"filename": doc.filename, "path": file_path})
            
            # Extract text based on file type
            ext = os.path.splitext(doc.filename)[1].lower()
            text = ""
            
            print(f"File extension: {ext}")
            
            if ext == '.pdf':
                print("Extracting from PDF...")
                text = extract_text_from_pdf(file_path)
            elif ext in ['.jpg', '.jpeg', '.png']:
                print("Extracting from image using OCR...")
                text = extract_text_from_image(file_path)
            else:
                print(f"Unsupported file type: {ext}")
            
            print(f"Extracted text length: {len(text)} characters")
            
            if text:
                print(f"\nFirst 300 characters of extracted text:")
                print(f"{text[:300]}\n")
                
                # Extract structured data
                data = extract_data_from_text(text)
                extracted_data_list.append(data)
            else:
                print("WARNING: No text extracted from document!")
        
        # Merge data from all documents
        final_data = merge_data(extracted_data_list) if extracted_data_list else ExtractedData()
        
        print(f"\n{'='*60}")
        print("FINAL MERGED DATA:")
        print(f"{'='*60}")
        for field, value in final_data.dict().items():
            if value:
                print(f"{field}: {value}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "files": uploaded_files,
            "extractedData": final_data.dict()
        }
        
    except Exception as e:
        print(f"\n{'!'*60}")
        print(f"ERROR in upload_documents:")
        print(f"{'!'*60}")
        print(traceback.format_exc())
        print(f"{'!'*60}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-form")
async def upload_form(form: UploadFile = File(...)):
    try:
        os.makedirs(os.path.join(UPLOAD_DIR, "forms"), exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, "forms", form.filename)
        
        with open(file_path, "wb") as f:
            content = await form.read()
            f.write(content)
        
        print(f"Form uploaded: {form.filename} -> {file_path}")
        
        return {
            "success": True,
            "formFile": form.filename,
            "formPath": file_path,
            "fields": []
        }
    except Exception as e:
        print(f"Error in upload_form: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fill-pdf")
async def fill_pdf_endpoint(request: FillRequest):
    try:
        print(f"\nFilling PDF form: {request.formPath}")
        print(f"Data fields: {len(request.data)}")
        
        output_path = await fill_pdf(request.formPath, request.data)
        filename = os.path.basename(output_path)
        
        print(f"PDF filled successfully: {output_path}")
        
        return {
            "success": True,
            "outputPath": output_path,
            "downloadUrl": f"http://localhost:{PORT}/api/download/{filename}"
        }
    except Exception as e:
        print(f"Error in fill_pdf: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fill-url")
async def fill_url_endpoint(request: URLFillRequest):
    try:
        print(f"\nFilling URL form: {request.url}")
        print(f"Data fields: {len(request.data)}")
        
        result = await fill_url(request.url, request.data)
        
        if result['success']:
            print(f"URL form filled: {result['message']}")
            return {
                "success": True,
                "message": result['message']
            }
        else:
            print(f"URL form filling failed: {result['message']}")
            raise HTTPException(status_code=500, detail=result['message'])
    except Exception as e:
        print(f"Error in fill_url: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sample-forms")
def get_sample_forms():
    try:
        forms = []
        if os.path.exists(SAMPLE_FORMS_DIR):
            for filename in os.listdir(SAMPLE_FORMS_DIR):
                if filename.endswith('.pdf'):
                    forms.append({
                        "id": filename.replace('.pdf', ''),
                        "name": filename.replace('-', ' ').replace('.pdf', '').title(),
                        "type": "PDF",
                        "path": os.path.join(SAMPLE_FORMS_DIR, filename)
                    })
        
        print(f"Found {len(forms)} sample forms")
        return {"success": True, "forms": forms}
    except Exception as e:
        print(f"Error in get_sample_forms: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    print(f"Downloading file: {file_path}")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/pdf'
    )