# **DocuOCR – Intelligent Document Parsing & Classification (Prototype)**

DocuOCR is a lightweight prototype demonstrating an automated OCR pipeline for processing loan-related documents used by banks and NBFCs.  
It extracts text from images/PDFs, identifies document types, separates individual documents, and displays structured results via a simple UI and backend.

This project was created as part of Crunchfinn’s internal exploration into AI-powered document automation.

Also check: https://github.com/jai0204/Docuocr-Website

---

## 🚀 Features

### ✔ Document Upload & Pre-Processing
- Supports **images** and **PDFs**
- Handles multi-page PDFs
- Basic validation for unclear or low-quality files

### ✔ OCR Extraction
- Uses OCR (Google Vision / Tesseract / Cloud API)
- Extracts text page-wise
- Cleans and normalizes noisy OCR text

### ✔ Document Classification
Identifies common document types such as:
- Aadhaar  
- PAN  
- Passport  
- Marksheets  
- Bank Statements  
- Fee Structure  
- Offer Letters  

### ✔ Lightweight Web UI
- Simple, minimal HTML interface  
- Document upload + result view  

### ✔ Express.js Backend
- File upload (Multer)
- Forwards OCR request to dedicated OCR server
- Returns structured JSON with classification info

### ✔ Ready for Scaling
- Architecture supports future ML integration  
- Extendable for large-scale document automation

---

## ⚙️ Tech Stack

**Backend:** Node.js, Express.js, Multer, Axios  
**Frontend:** HTML / CSS (Tailwind optional)  
**OCR:** Google Vision API or Easy OCR  
**Deployment:** AWS EC2, Nginx, Certbot SSL  
**Subdomain:** `docuocr.crunchfinn.com`

---

## 🧠 Document Classification Logic (Prototype)

Uses lightweight rule-based detection:
- Keyword matching
- Regex identification
- Document-specific text cues
- Structural patterns
(Designed only for prototype demos.)

---

## 📍 Deployment Notes

- Hosted on AWS EC2
- Static files served through Nginx
- SSL enabled using Certbot
- OCR engine runs on GCP VM
- Subdomain routing: docuocr.crunchfinn.com
- Express.js handles GET/POST for the OCR flow

---

## 📌 Limitations

- No authentication
- Limited error handling
- No database
- Basic rule-based classification
- OCR accuracy depends on file clarity
- Not optimized for large-scale workloads

