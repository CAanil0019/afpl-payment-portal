from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import payment, charges, reports
from app.database import Base, engine
from app import models
from app.routers import auth
from app.services.scheduler_service import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AFPL Payment Portal")

start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://afplpayment.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment.router)
app.include_router(charges.router)

@app.get("/")
def home():
    return {"message": "AFPL Payment Portal Running"}

app.include_router(reports.router)
app.include_router(auth.router)
