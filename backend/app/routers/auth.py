from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AdminUser
from app.utils.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/admin-login")
def admin_login(payload: dict, db: Session = Depends(get_db)):

    username = payload.get("username")

    password = payload.get("password")

    admin = db.query(AdminUser).filter(
        AdminUser.username == username,
        AdminUser.is_active == True
    ).first()

    if not admin:
        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    if password != admin.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = create_access_token(
        {
            "sub": admin.username
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }