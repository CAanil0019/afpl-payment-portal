from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import ChargeMaster, Transaction
from app.schemas import TransactionCreate
from app.utils.gst_calc import calculate_gst
from app.services.order_service import generate_order_reference
from app.services.razorpay_service import create_razorpay_order
from app.config import settings
import json
from app.schemas import TransactionCreate, RazorpayVerifyRequest
from app.services.razorpay_service import create_razorpay_order, verify_razorpay_signature
from fastapi.responses import HTMLResponse
from urllib.parse import urlencode, parse_qs
from app.config import settings
from app.services.ccavenue_service import encrypt, decrypt
from fastapi import Request
from fastapi.responses import StreamingResponse
from app.services.receipt_service import generate_receipt_pdf

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/create-transaction")
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):

    charge = db.query(ChargeMaster).filter(
        ChargeMaster.charge_id == payload.charge_id,
        ChargeMaster.is_active == True
    ).first()

    if not charge:
        raise HTTPException(status_code=404, detail="Invalid charge")

    gst_amount, total_amount = calculate_gst(
        charge.base_amount,
        charge.gst_percent
    )

    order_reference = generate_order_reference()

    razorpay_order = create_razorpay_order(
        order_reference,
        float(total_amount)
    )

    transaction = Transaction(
        order_reference=order_reference,
        customer_name=payload.customer_name,
        loan_account_number=payload.loan_account_number,
        mobile_number=payload.mobile_number,
        charge_type=charge.charge_name,
        base_amount=charge.base_amount,
        gst_amount=gst_amount,
        total_amount=total_amount,
        gateway_name=payload.gateway_name,
        gateway_order_id=razorpay_order["id"],
        payment_status="CREATED"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "message": "Order Created",
        "order_reference": order_reference,
        "razorpay_order_id": razorpay_order["id"],
        "amount": float(total_amount),
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID
    }

@router.post("/verify-payment")
def verify_payment(
    payload: RazorpayVerifyRequest,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.order_reference == payload.order_reference,
        Transaction.gateway_order_id == payload.razorpay_order_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    try:
        verify_razorpay_signature(
            payload.razorpay_order_id,
            payload.razorpay_payment_id,
            payload.razorpay_signature
        )

        transaction.gateway_payment_id = payload.razorpay_payment_id
        transaction.payment_status = "SUCCESS"
        transaction.callback_response = json.dumps(payload.dict())

        db.commit()

        return {
            "message": "Payment verified successfully",
            "order_reference": transaction.order_reference,
            "payment_status": transaction.payment_status
        }

    except Exception as e:
        transaction.payment_status = "FAILED"
        transaction.callback_response = str(e)
        db.commit()

        raise HTTPException(status_code=400, detail="Payment verification failed")
    
@router.post("/create-ccavenue-order")
def create_ccavenue_order(
    payload: TransactionCreate,
    db: Session = Depends(get_db)
):
    charge = db.query(ChargeMaster).filter(
        ChargeMaster.charge_id == payload.charge_id,
        ChargeMaster.is_active == True
    ).first()

    if not charge:
        raise HTTPException(status_code=404, detail="Invalid charge")

    gst_amount, total_amount = calculate_gst(
        charge.base_amount,
        charge.gst_percent
    )

    order_reference = generate_order_reference()

    transaction = Transaction(
        order_reference=order_reference,
        customer_name=payload.customer_name,
        loan_account_number=payload.loan_account_number,
        mobile_number=payload.mobile_number,
        charge_type=charge.charge_name,
        base_amount=charge.base_amount,
        gst_amount=gst_amount,
        total_amount=total_amount,
        gateway_name="CCAVENUE",
        payment_status="CREATED"
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    cca_data = {
        "merchant_id": settings.CCAVENUE_MERCHANT_ID,
        "order_id": order_reference,
        "currency": "INR",
        "amount": str(float(total_amount)),
        "redirect_url": settings.CCAVENUE_REDIRECT_URL,
        "cancel_url": settings.CCAVENUE_CANCEL_URL,
        "language": "EN",
        "billing_name": payload.customer_name,
        "billing_tel": payload.mobile_number,
    }

    plain_text = urlencode(cca_data)

    encrypted_data = encrypt(
        plain_text,
        settings.CCAVENUE_WORKING_KEY
    )

    return {
        "gateway": "CCAVENUE",
        "order_reference": order_reference,
        "access_code": settings.CCAVENUE_ACCESS_CODE,
        "enc_request": encrypted_data,
        "gateway_url": "https://test.ccavenue.com/transaction/transaction.do?command=initiateTransaction"
    }
@router.post("/ccavenue-response", response_class=HTMLResponse)
async def ccavenue_response(request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    enc_resp = form.get("encResp")

    if not enc_resp:
        return HTMLResponse("<h3>Invalid CCAvenue response</h3>")

    decrypted_response = decrypt(
        enc_resp,
        settings.CCAVENUE_WORKING_KEY
    )

    response_dict = {
        key: value[0]
        for key, value in parse_qs(decrypted_response).items()
    }

    order_id = response_dict.get("order_id")
    order_status = response_dict.get("order_status")
    tracking_id = response_dict.get("tracking_id")

    transaction = db.query(Transaction).filter(
        Transaction.order_reference == order_id
    ).first()

    if transaction:
        transaction.gateway_payment_id = tracking_id
        transaction.callback_response = decrypted_response

        if order_status == "Success":
            transaction.payment_status = "SUCCESS"
        elif order_status == "Failure":
            transaction.payment_status = "FAILED"
        else:
            transaction.payment_status = "PENDING"

        db.commit()

    if order_status == "Success":
        return HTMLResponse(
            f"""
            <html>
              <body>
                <h2>Payment Successful</h2>
                <p>Reference No: {order_id}</p>
                <p>Tracking ID: {tracking_id}</p>
                <a href="http://localhost:5173/">Back to Portal</a>
              </body>
            </html>
            """
        )

    return HTMLResponse(
        f"""
        <html>
          <body>
            <h2>Payment Failed / Pending</h2>
            <p>Reference No: {order_id}</p>
            <p>Status: {order_status}</p>
            <a href="http://localhost:5173/">Back to Portal</a>
          </body>
        </html>
        """
    )

@router.get("/download-receipt/{order_reference}")
def download_receipt(
    order_reference: str,
    db: Session = Depends(get_db)
):
    transaction = db.query(Transaction).filter(
        Transaction.order_reference == order_reference
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    pdf_buffer = generate_receipt_pdf(transaction)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            f"attachment; filename={order_reference}.pdf"
        }
    )