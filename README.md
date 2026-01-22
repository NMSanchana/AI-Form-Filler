# AI Form Filling Assistant for Indian Citizen Services

A web-based AI system that automatically extracts personal information from Indian identity documents and intelligently fills government and online forms.

The application supports Aadhaar, PAN, Passport, Driving License, and Birth Certificate documents, and can auto-fill uploaded forms, built-in government forms, or forms provided via URL.

---

## Core Capabilities

- Upload multiple Indian identity documents (PDF / JPG / PNG)
- Upload blank forms (PDF / Image / DOCX) or provide a form URL
- OCR with image preprocessing (deskew, grayscale, thresholding)
- Extract text with bounding box information
- Structured key-value extraction for Indian IDs:
  - Full Name
  - Date of Birth
  - Gender
  - Address
  - Aadhaar Number
  - PAN Number
  - Parent Name
- Document understanding using layout-aware NLP
- Automatic form field detection and label association
- Intelligent field mapping using semantic similarity
- Confidence scoring for each auto-filled field
- Editable review interface before submission
- Export final filled form as a downloadable PDF

---

## Technology Stack

**Backend**
- Python
- FastAPI
- Tesseract OCR
- OpenCV
- PyMuPDF / pdfplumber
- Transformers (BERT / LayoutLM)
- Sentence-BERT
- PyTorch
- scikit-learn

**Frontend**
- React
- JavaScript
- HTML / CSS

---

## AI & NLP Approach

- **OCR** extracts text and spatial layout from documents
- **Regex + rule-based logic** handles deterministic fields (IDs, dates)
- **BERT / LayoutLM** perform token classification for entity extraction  
  (used for understanding document structure and contextual meaning)
- **Sentence-BERT** enables semantic matching between extracted data and form fields
- **Fuzzy matching** improves robustness across varied form labels
- Confidence scores quantify mapping reliability

---

## System Flow

1. User uploads identity documents and a form (or form URL)
2. OCR extracts text and layout information
3. Entities are detected using NLP models and rules
4. Form fields and labels are identified
5. Intelligent mapping aligns extracted data with form fields
6. Form is auto-filled while preserving formatting
7. User reviews and edits values
8. Final filled PDF is generated and downloaded

---


---

## Run Locally

### Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
### Frontend
cd frontend
npm install
npm start


