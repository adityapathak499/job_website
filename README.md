# job_website
This is a simple Job Portal backend API built using **FastAPI** and **SQLite**. It allows two types of users — **Candidates** and **Recruiters** — to interact with job postings, applications, and user authentication securely via JWT tokens.

## Features

### Candidates
- Sign up / Log in
- View all jobs
- Apply to jobs (single or multiple)
- View applied jobs
- Email notification on application

### Recruiters
- Sign up / Log in
- Post new jobs
- View applicants
- Email notification when someone applies

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite (via SQLAlchemy)
- **Authentication:** JWT (using `python-jose`)
- **Password Hashing:** `passlib` with bcrypt
- **Email Notifications:** Simulated via print (mocked)

---

## Installation & Running

```bash
# Clone the repo
git clone https://github.com/adityapathak499/job_website.git
cd job_website

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn main:app --reload



################## API Endpoints & Payloads ##########################
🔹 POST /signup
Register a user.

Payload:


{
  "email": "aditya@example.com",
  "password": "aditya123",
  "role": "candidate"
}
🔹 POST /login
Login and receive a JWT token.

Payload:


{
  "email": "aditya@example.com",
  "password": "aditya123"
}
Response:


{
  "access_token": "<JWT>",
  "token_type": "bearer"
}

🔹 POST /jobs (Recruiter only)
Create a job posting.

Payload:


{
  "title": "Backend Developer",
  "description": "Experience with FastAPI and SQL."
}

🔹 GET /jobs
Get a list of all available jobs.

🔹 POST /apply/{job_id} (Candidate only)
Apply to a job by ID.

🔹 POST /apply-multiple (Candidate only)
Apply to multiple jobs at once.

Payload:

{
  "job_ids": [1, 2, 3]
}

🔹 GET /applied (Candidate only)
List jobs the current candidate has applied to.

🔹 GET /applicants (Recruiter only)
List all applicants to jobs posted by the recruiter.

🔹 POST /logout
Dummy endpoint – logs user out (token removal handled client-side).

📧 Email Notification
Simulated with print() via the send_email() utility.

Replace with SMTP or services like SendGrid for production.