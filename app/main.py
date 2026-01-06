from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import resume
from app.api.v1.routes.interview_flow import router as interview_flow_router
from app.api.v1.routes.llm import router as llm_router
from app.services.resume_storage_service import init_db

app = FastAPI(title="AI Interview Bot Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "AI Interview Bot Backend running"}


@app.on_event("startup")
async def startup_event():
    init_db()


# Routers
app.include_router(llm_router)
app.include_router(interview_flow_router)
app.include_router(resume.router)
