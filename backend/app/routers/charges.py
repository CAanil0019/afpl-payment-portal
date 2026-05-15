from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

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


# -----------------------------
# Create Charge Schema
# -----------------------------
class ChargeCreate(BaseModel):
    charge_name: str
    description: str
    base_amount: float
    gst_percent: float


# -----------------------------
# GET ACTIVE CHARGES
# -----------------------------
@router.get("/", response_model=list[ChargeResponse])
def get_active_charges(db: Session = Depends(get_db)):

    charges = (
        db.query(ChargeMaster)
        .filter(ChargeMaster.is_active == True)
        .all()
    )

    return charges


# -----------------------------
# CREATE CHARGE MASTER
# -----------------------------
@router.post("/")
def create_charge(
    data: ChargeCreate,
    db: Session = Depends(get_db)
):

    charge = ChargeMaster(
        charge_name=data.charge_name,
        description=data.description,
        base_amount=data.base_amount,
        gst_percent=data.gst_percent,
        is_active=True
    )

    db.add(charge)
    db.commit()
    db.refresh(charge)

    return {
        "message": "Charge created successfully",
        "charge_id": charge.charge_id
    }
