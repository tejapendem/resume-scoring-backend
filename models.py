# models.py

from sqlalchemy import Column, Integer, String, Text, JSON
from database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    file_path = Column(String)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    score = Column(Integer)
    summary = Column(Text)
    skills = Column(JSON)
