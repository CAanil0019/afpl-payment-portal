from pydantic import BaseModel, Field
from typing import Optional


class ChargeResponse(BaseModel):
    charge_id: int
    charge_name: str
    description: Optional[str]
    base_amount: float
    gst_percent: float

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    customer_name: str = Field(..., min_length=2)
    loan_account_number: str = Field(..., min_length=3)
    mobile_number: str = Field(..., pattern=r"^[6-9][0-9]{9}$")
    charge_id: int
    gateway_name: str = Field(..., pattern=r"^(RAZORPAY|CCAVENUE)$")


class TransactionResponse(BaseModel):
    transaction_id: int
    order_reference: str
    customer_name: str
    loan_account_number: str
    mobile_number: str
    charge_type: str
    base_amount: float
    gst_amount: float
    total_amount: float
    gateway_name: str
    payment_status: str

    class Config:
        from_attributes = True

class RazorpayVerifyRequest(BaseModel):
    order_reference: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str