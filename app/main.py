from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models import user
from app.api import auth, user_actions

user.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Remooovy API",
    description="API for background removal service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user_actions.router)
