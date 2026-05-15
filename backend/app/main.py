from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import payment, charges, reports, auth
from app.database import Base, engine
from app import models
from app.services.scheduler_service import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AFPL Payment Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://annapurnafinance-charges.netlify.app",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

start_scheduler()

app.include_router(payment.router)
app.include_router(charges.router)
app.include_router(reports.router)
app.include_router(auth.router)


@app.get("/")
def home():
    return {"message": "AFPL Payment Portal Running"}
