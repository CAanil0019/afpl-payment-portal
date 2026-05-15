from sqlalchemy import Column, Integer, String, Numeric, Boolean, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base


class ChargeMaster(Base):
    __tablename__ = "charge_master"

    charge_id = Column(Integer, primary_key=True, index=True)
    charge_name = Column(String(200), nullable=False)
    description = Column(Text)
    base_amount = Column(Numeric(12, 2), nullable=False)
    gst_percent = Column(Numeric(5, 2), nullable=False, default=18)
    is_active = Column(Boolean, default=True)


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    order_reference = Column(String(100), unique=True, index=True)

    customer_name = Column(String(200), nullable=False)
    loan_account_number = Column(String(100), nullable=False)
    mobile_number = Column(String(10), nullable=False)

    charge_type = Column(String(200), nullable=False)
    base_amount = Column(Numeric(12, 2), nullable=False)
    gst_amount = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    gateway_name = Column(String(50))
    gateway_order_id = Column(String(200))
    gateway_payment_id = Column(String(200))

    payment_status = Column(String(50), default="PENDING")
    transaction_date = Column(TIMESTAMP, server_default=func.now())
    callback_response = Column(Text)

class AdminUser(Base):
    __tablename__ = "admin_users"

    admin_id = Column(Integer, primary_key=True)

    username = Column(String(100), unique=True)

    password = Column(String(500))

    is_active = Column(Boolean, default=True)