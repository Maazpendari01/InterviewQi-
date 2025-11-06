from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routers import interview

app = FastAPI(title="AI Interview Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview.router)

@app.get("/")
async def root():
    return{"message":"Welcome to my AI Interview Platform"}
