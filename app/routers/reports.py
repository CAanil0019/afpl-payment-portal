from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import StringIO
import csv

from app.database import SessionLocal
from app.models import Transaction
from app.utils.security import verify_token
from app.services.email_service import send_daily_transaction_email

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    data = db.query(Transaction).order_by(Transaction.transaction_id.desc()).all()
    return data


@router.get("/transactions-csv")
def download_transactions_csv(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    transactions = db.query(Transaction).order_by(
        Transaction.transaction_id.desc()
    ).all()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Ref No", "Customer", "Loan No", "Mobile", "Charge",
        "Base Amount", "GST Amount", "Total Amount",
        "Gateway", "Status", "Payment ID", "Date"
    ])

    for txn in transactions:
        writer.writerow([
            txn.order_reference,
            txn.customer_name,
            txn.loan_account_number,
            txn.mobile_number,
            txn.charge_type,
            txn.base_amount,
            txn.gst_amount,
            txn.total_amount,
            txn.gateway_name,
            txn.payment_status,
            txn.gateway_payment_id,
            txn.transaction_date
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=transaction_report.csv"
        }
    )


@router.post("/send-test-email-open")
def send_test_email_open():
    send_daily_transaction_email()

    return {
        "message": "Test email triggered successfully"
    }