from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User, Job, Application
from schemas import *
from auth import create_access_token, get_current_user
from utils import send_email
from passlib.context import CryptContext

app = FastAPI()
Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(user.password)
    new_user = User(email=user.email, password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    return {"msg": "Signup successful"}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/jobs", response_model=JobResponse)
def post_job(job: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can post jobs")
    new_job = Job(title=job.title, description=job.description, recruiter_id=current_user.id)
    db.add(new_job)
    db.commit()
    return new_job

@app.get("/jobs", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()

@app.post("/apply/{job_id}")
def apply_job(job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply")
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if db.query(Application).filter_by(candidate_id=current_user.id, job_id=job_id).first():
        raise HTTPException(status_code=400, detail="Already applied")
    application = Application(candidate_id=current_user.id, job_id=job_id)
    db.add(application)
    db.commit()

    send_email(current_user.email, "Job Application Submitted", f"You applied for {job.title}")
    recruiter = db.query(User).filter(User.id == job.recruiter_id).first()
    if recruiter:
        send_email(recruiter.email, "New Application", f"{current_user.email} applied for {job.title}")
    return {"msg": "Application submitted"}

@app.post("/apply-multiple")
def apply_multiple_jobs(request: JobApplicationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can apply")

    applied = []
    skipped = []

    for job_id in request.job_ids:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            skipped.append({"job_id": job_id, "reason": "Job not found"})
            continue
        if db.query(Application).filter_by(candidate_id=current_user.id, job_id=job_id).first():
            skipped.append({"job_id": job_id, "reason": "Already applied"})
            continue

        application = Application(candidate_id=current_user.id, job_id=job_id)
        db.add(application)
        applied.append(job)

        # Send email notifications
        send_email(current_user.email, "Job Application Submitted", f"You applied for {job.title}")
        recruiter = db.query(User).filter(User.id == job.recruiter_id).first()
        if recruiter:
            send_email(recruiter.email, "New Application", f"{current_user.email} applied for {job.title}")

    db.commit()

    return {
        "status": "completed",
        "applied_jobs": [job.id for job in applied],
        "skipped": skipped
    }

@app.get("/applied", response_model=List[ApplicationResponse])
def get_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "candidate":
        raise HTTPException(status_code=403, detail="Only candidates can view applications")
    return db.query(Application).filter(Application.candidate_id == current_user.id).all()

@app.get("/applicants", response_model=List[ApplicationResponse])
def view_applicants(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view applicants")
    job_ids = [j.id for j in db.query(Job).filter(Job.recruiter_id == current_user.id).all()]
    return db.query(Application).filter(Application.job_id.in_(job_ids)).all()

@app.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"msg": f"User {current_user.email} logged out (token must be discarded client-side)."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
