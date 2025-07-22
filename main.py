# from fastapi import FastAPI, File, UploadFile, Form, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy import create_engine, Column, Integer, String, Float
# from sqlalchemy.orm import declarative_base, sessionmaker
# from utils import extract_text, compute_score, authenticate_user, create_access_token
# import shutil, os

# # === FastAPI app setup ===
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], allow_credentials=True,
#     allow_methods=["*"], allow_headers=["*"]
# )

# # === Upload folder ===
# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# # === Job description storage ===
# job_description_text = ""

# # === SQLite DB setup ===
# Base = declarative_base()
# engine = create_engine("sqlite:///resumes.db", connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(bind=engine)
# session = SessionLocal()

# class Resume(Base):
#     __tablename__ = "resumes"
#     id = Column(Integer, primary_key=True, index=True)
#     filename = Column(String)
#     text = Column(String)
#     score = Column(Float)

# Base.metadata.create_all(bind=engine)

# # === Login route ===
# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user = authenticate_user(form_data.username, form_data.password)
#     if not user:
#         return {"error": "Invalid credentials"}
#     access_token = create_access_token(data={"sub": user["username"]})
#     return {"access_token": access_token, "token_type": "bearer"}

# # === Update job description and re-score resumes ===
# @app.post("/job-description")
# def update_job_description(description: str = Form(...)):
#     global job_description_text
#     job_description_text = description

#     resumes = session.query(Resume).all()
#     for r in resumes:
#         r.score = round(compute_score(job_description_text, r.text) * 100, 2)
#     session.commit()

#     return {"message": "Job description updated and scores refreshed"}

# # === Upload and score resume ===
# @app.post("/upload-resume")
# async def upload_resume(file: UploadFile = File(...)):
#     global job_description_text

#     file_location = f"{UPLOAD_DIR}/{file.filename}"
#     with open(file_location, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     resume_text = extract_text(file_location)

#     if job_description_text.strip():
#         score = compute_score(job_description_text, resume_text)
#     else:
#         score = 0.0

#     new_resume = Resume(
#         filename=file.filename,
#         text=resume_text,
#         score=round(score * 100, 2)
#     )
#     session.add(new_resume)
#     session.commit()

#     return {
#         "filename": file.filename,
#         "score": new_resume.score,
#         "text": resume_text[:500]
#     }

# # === Get all uploaded resumes ===
# @app.get("/resumes")
# def get_uploaded_resumes():
#     resumes = session.query(Resume).all()
#     return [
#         {
#             "filename": r.filename,
#             "score": r.score,
#             "text": r.text[:500]
#         } for r in resumes
#     ]


from fastapi import FastAPI, File, UploadFile, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils import extract_text, compute_score, authenticate_user, create_access_token
import shutil, os

from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
# backend/main.py
from database import SessionLocal, Base
from fastapi.responses import FileResponse
# ==== Setup ====
app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-scoring-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DATABASE_URL = "sqlite:///./resumes.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# ==== Models ====
class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True)
    text = Column(String)
    score = Column(Float)

class JDText(Base):
    __tablename__ = "jd_text"
    id = Column(Integer, primary_key=True)
    text = Column(String)

Base.metadata.create_all(bind=engine)

# ==== Login ====
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        return {"error": "Invalid credentials"}
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# ==== Upload Resume ====
# @app.post("/upload-resume")
# async def upload_resume(file: UploadFile = File(...)):
#     session = Session()

#     file_location = f"{UPLOAD_DIR}/{file.filename}"
#     with open(file_location, "wb") as f:
#         shutil.copyfileobj(file.file, f)

#     resume_text = extract_text(file_location)

#     # Get current job description
#     jd = session.query(JDText).first()
#     jd_text = jd.text if jd else ""

#     # If JD is empty, score = 0
#     score = compute_score(jd_text, resume_text) if jd_text.strip() else 0.0

#     resume = Resume(filename=file.filename, text=resume_text, score=round(score * 100, 2))
#     session.add(resume)
#     session.commit()

#     return {
#         "filename": resume.filename,
#         "score": resume.score,
#         "text": resume.text[:500]
#     }

# ==== Set Job Description + Recalculate ====
# @app.post("/job-description")
# def update_job_description(description: str = Form(...)):
#     session = Session()

#     jd = session.query(JDText).first()
#     if jd:
#         jd.text = description
#     else:
#         jd = JDText(text=description)
#         session.add(jd)

#     # Recalculate scores for all resumes
#     resumes = session.query(Resume).all()
#     for r in resumes:
#         r.score = round(compute_score(description, r.text) * 100, 2)

#     session.commit()
#     return {"message": "Job description updated and scores refreshed"}

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.post("/job-description")
def update_job_description(description: str = Form(...), db: Session = Depends(get_db)):
    global job_description_text
    job_description_text = description.strip()

    resumes = db.query(Resume).all()

    for resume in resumes:
        if job_description_text:
            new_score = round(compute_score(job_description_text, resume.text) * 100, 2)
        else:
            new_score = 0
        resume.score = new_score

    db.commit()

    return {"message": "Job description updated and resume scores refreshed."}


# ==== Get All Resumes ====
# @app.get("/resumes")
# def get_uploaded_resumes():
#     session = Session()
#     resumes = session.query(Resume).all()
#     return [
#         {
#             "filename": r.filename,
#             "score": r.score,
#             "text": r.text[:500]
#         }
#         for r in resumes
#     ]

@app.get("/resumes")
def get_uploaded_resumes():
    session = Session()
    resumes = session.query(Resume).all()

    from utils import extract_name, extract_email, extract_phone, extract_summary, extract_skills

    result = []
    for r in resumes:
        text = r.text
        result.append({
            "filename": r.filename,
            "score": r.score,
            "text": text[:500],
            "name": extract_name(text),
            "email": extract_email(text),
            "phone": extract_phone(text),
            "summary": extract_summary(text),
            "skills": extract_skills(text)
        })
    return result

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    session = Session()

    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    resume_text = extract_text(file_location)

    # Get current job description
    jd = session.query(JDText).first()
    jd_text = jd.text if jd else ""

    # Score the resume
    score = compute_score(jd_text, resume_text) if jd_text.strip() else 0.0

    # Extract metadata
    from utils import extract_name, extract_email, extract_phone, extract_summary, extract_skills

    name = extract_name(resume_text)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)
    summary = extract_summary(resume_text)
    skills = extract_skills(resume_text)

    # 🔁 Check if resume already exists
    existing = session.query(Resume).filter_by(filename=file.filename).first()
    if existing:
        # Update the existing resume
        existing.text = resume_text
        existing.score = round(score * 100, 2)
        existing.name = name
        existing.email = email
        existing.phone = phone
        existing.summary = summary
        existing.skills = skills
        resume = existing
    else:
        # Create a new resume
        resume = Resume(
            filename=file.filename,
            text=resume_text,
            score=round(score * 100, 2),
            name=name,
            email=email,
            phone=phone,
            summary=summary,
            skills=skills
        )
        session.add(resume)

    session.commit()

    return {
        "filename": resume.filename,
        "score": resume.score,
        "text": resume.text[:500],
        "name": resume.name,
        "email": resume.email,
        "phone": resume.phone,
        "summary": resume.summary,
        "skills": resume.skills
    }


@app.get("/download/{filename}")
def download_resume(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
    return {"error": "File not found"}