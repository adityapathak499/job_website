from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class JobCreate(BaseModel):
    title: str
    description: str

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    recruiter_id: int

    class Config:
        orm_mode = True

class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int

    class Config:
        orm_mode = True

class JobApplicationRequest(BaseModel):
    job_ids: List[int]
