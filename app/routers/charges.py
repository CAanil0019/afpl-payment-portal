from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ChargeMaster
from app.schemas import ChargeResponse

router = APIRouter(
    prefix="/charges",
    tags=["Charges"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[ChargeResponse])
def get_active_charges(db: Session = Depends(get_db)):
    charges = db.query(ChargeMaster).filter(ChargeMaster.is_active == True).all()
    return charges