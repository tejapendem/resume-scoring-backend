# utils/extract.py

import re
import random

def extract_text_from_pdf(filepath):
    # Use PyMuPDF or PDFMiner as previously setup
    import fitz
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_info_from_text(text):
    name = re.findall(r'Name[:\s]*([A-Z][a-z]+ [A-Z][a-z]+)', text)
    email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
    phone = re.findall(r'\+?\d[\d\s()-]{8,}', text)
    return {
        "name": name[0] if name else "N/A",
        "email": email[0] if email else "N/A",
        "phone": phone[0] if phone else "N/A",
        "summary": text[:300] + "..." if len(text) > 300 else text,
    }

def score_resume(text, job_desc):
    # Basic NLP scoring — improve with spaCy/transformers later
    jd_words = set(job_desc.lower().split())
    resume_words = set(text.lower().split())
    matched = jd_words & resume_words
    score = int((len(matched) / len(jd_words)) * 100) if jd_words else 0
    top_skills = list(matched)[:5]
    return score, top_skills
