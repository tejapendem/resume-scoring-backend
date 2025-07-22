# import pdfplumber
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from datetime import datetime, timedelta
# from jose import jwt

# # Secret key for token encoding/decoding
# SECRET_KEY = "secret"
# ALGORITHM = "HS256"

# # Load sentence transformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# # Dummy user
# fake_user = {
#     "username": "admin",
#     "password": "admin123"
# }

# def extract_text(pdf_path):
#     text = ""
#     with pdfplumber.open(pdf_path) as pdf:
#         for page in pdf.pages:
#             text += page.extract_text() + "\n"
#     return text.strip()

# def compute_score(job_description, resume_text):
#     embeddings = model.encode([job_description, resume_text])
#     return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

# # def authenticate_user(username: str, password: str):
# #     if username == fake_user["username"] and password == fake_user["password"]:
# #         return fake_user
# #     return None

# def authenticate_user(username: str, password: str):
#     if not username or not password:
#         return None  # ❗ Block empty fields

#     # For demo purpose, hardcoded user
#     if username == "admin" and password == "admin":
#         return {"username": "admin"}
#     return None

# def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
#     to_encode = data.copy()
#     to_encode.update({"exp": datetime.utcnow() + expires_delta})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


import pdfplumber
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
from jose import jwt

# Secret key for token encoding/decoding
SECRET_KEY = "secret"
ALGORITHM = "HS256"

# Load sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Dummy user
fake_user = {
    "username": "admin",
    "password": "admin123"
}

def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def compute_score(job_description, resume_text):
    embeddings = model.encode([job_description, resume_text])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split("\n")
    for line in lines[:5]:  # Check top few lines
        if len(line.split()) <= 4 and not re.search(r'\d', line):
            return line.strip()
    return None

def extract_summary(text):
    summary_keywords = ['summary', 'profile', 'about me', 'professional summary']
    lines = text.lower().split('\n')
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in summary_keywords):
            # Get next few lines after keyword
            summary_lines = lines[i+1:i+5]
            return " ".join(summary_lines).strip()
    return None

def extract_skills(text):
    skills_list = [
        'python', 'java', 'c++', 'html', 'css', 'javascript',
        'react', 'node.js', 'sql', 'mysql', 'mongodb', 'aws',
        'docker', 'git', 'linux', 'tensorflow', 'pytorch',
        'machine learning', 'deep learning', 'data analysis',
        'communication', 'leadership', 'problem solving'
    ]
    found = []
    text_lower = text.lower()
    for skill in skills_list:
        if skill.lower() in text_lower:
            found.append(skill)
    return found

def authenticate_user(username: str, password: str):
    if not username or not password:
        return None  # ❗ Block empty fields

    # For demo purpose, hardcoded user
    if username == "admin" and password == "admin":
        return {"username": "admin"}
    return None

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
