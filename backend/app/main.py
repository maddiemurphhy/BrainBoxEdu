"""
Entry point. Run with:  uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs to try every endpoint in the browser.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import documents, questions

# Creates the SQLite tables on startup if they don't already exist.
# (Fine for an MVP; a real project would use migrations eventually.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="StudyBuddy API", version="0.1.0")

# Allows the deployed frontend (and local dev servers) to call this API
# from the browser. Listed explicitly now that there's a real deployed
# frontend domain, instead of the "*" wildcard used during local dev.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://brainboxedu.vercel.app",
        "https://brainboxedu-we-are-learning.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(questions.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
