 AI Interview Bot Backend — Team Onboarding & Setup Guide

Welcome to the AI Interview Bot Backend project!
This document will help every team member set up the development environment, follow the collaboration workflow, and start contributing immediately.

 1. Project Requirements

Before starting, ensure you have installed:

Required:

Python 3.10 (not 3.11/3.12)

Git

VS Code / PyCharm (recommended)

Virtual environment (venv) enabled

GitHub account with collaborator access

Optional:

Docker

Postman / Thunder Client

2. Clone the Repository
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>

 3. Switch to the develop Branch
git checkout develop
git pull origin develop


This is the branch all development happens on.

 4. Create & Activate Virtual Environment
Linux / Mac
python3.10 -m venv venv
source venv/bin/activate

Windows
python -m venv venv
venv\Scripts\activate


Verify:

python --version


Should show: Python 3.10.x

5. Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

6. Environment Variables

Create your personal .env:

cp .env.example .env


Do NOT commit .env — it contains secrets.

7. Run the Development Server
uvicorn app.main:app --reload


Test in browser:

http://127.0.0.1:8000/

http://127.0.0.1:8000/v1/interview/health

If both respond correctly, setup is successful.

 8. Create Your Feature Branch

Each team member works on their own module.

Examples:

Computer Vision:
git checkout -b feature/cv-module
git push -u origin feature/cv-module

LLM Module:
git checkout -b feature/llm-module
git push -u origin feature/llm-module

Resume Parser:
git checkout -b feature/resume-parser
git push -u origin feature/resume-parser

Integrator:
git checkout -b feature/integration
git push -u origin feature/integration

 9. Daily Team Workflow
 1. Pull latest develop
git checkout develop
git pull origin develop

 2. Switch to your feature branch
git checkout feature/<your-module>

 3. Sync with develop (avoid conflicts)
git pull --rebase origin develop

 4. Code → Commit → Push
git add .
git commit -m "feat(<module>): short message"
git push origin feature/<branch>

 5. Create Pull Request (feature → develop)

On GitHub:

Base branch → develop

Compare → feature/<your-branch>

Add reviewer

Submit PR

Integrator will review & merge.

 10. After PR Merge

Everyone must update their local environment:

git checkout develop
git pull origin develop

 11. Branching Strategy (GitFlow)
main (protected) → production-ready  
develop → active development  
feature/<module> → work branches  


No one pushes to main.
All features merge into develop via Pull Request.

 12. Folder Structure (What Goes Where)
app/
 ├── api/               # all API endpoints
 │    └── v1/routes/    # versioned route files
 ├── core/              # configs, settings, security
 ├── services/          # business logic (ASR, LLM, CV, resume, scoring)
 ├── models/            # pydantic models + DB models
 ├── utils/             # helper utilities (audio, logging, etc.)
 └── main.py            # FastAPI entry point

 13. Contribution Rules
✔ Use feature branches
✔ No direct commits to main or develop
✔ All changes must go through Pull Request
✔ Follow consistent naming conventions
✔ Write meaningful commit messages
✔ Update .env.example if new env variables are added
 14. Troubleshooting
If dependencies fail to install

Run:

pip install --upgrade pip setuptools wheel

If uvicorn is not found
pip install uvicorn

If Python version mismatch

Recreate environment using Python 3.10.