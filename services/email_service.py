import smtplib
from email.message import EmailMessage
import pandas as pd
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Transaction
from app.config import settings
from datetime import datetime
import tempfile


def send_daily_transaction_email():

    db: Session = SessionLocal()

    try:

        transactions = db.query(Transaction).all()

        data = []

        total_amount = 0
        success_count = 0
        failed_count = 0

        for txn in transactions:

            data.append({
                "Reference": txn.order_reference,
                "Customer": txn.customer_name,
                "Loan No": txn.loan_account_number,
                "Mobile": txn.mobile_number,
                "Charge": txn.charge_type,
                "Amount": txn.total_amount,
                "Gateway": txn.gateway_name,
                "Status": txn.payment_status,
                "Date": txn.transaction_date
            })

            if txn.payment_status == "SUCCESS":
                success_count += 1
                total_amount += float(txn.total_amount)

            if txn.payment_status == "FAILED":
                failed_count += 1

        df = pd.DataFrame(data)

        temp_file = tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False
        )

        df.to_excel(temp_file.name, index=False)

        msg = EmailMessage()

        msg["Subject"] = (
            f"AFPL Daily Transaction Report - "
            f"{datetime.now().strftime('%d-%m-%Y')}"
        )

        msg["From"] = settings.SMTP_USER

        msg["To"] = settings.REPORT_TO

        html_body = f"""
        <h3>AFPL Daily Transaction Summary</h3>

        <p><b>Total Transactions:</b> {len(data)}</p>

        <p><b>Successful Transactions:</b> {success_count}</p>

        <p><b>Failed Transactions:</b> {failed_count}</p>

        <p><b>Total Collection:</b> ₹{total_amount}</p>
        """

        msg.add_alternative(html_body, subtype="html")

        with open(temp_file.name, "rb") as f:
            file_data = f.read()

        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="octet-stream",
            filename="daily_transaction_report.xlsx"
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            int(settings.SMTP_PORT)
        ) as smtp:

            smtp.starttls()

            smtp.login(
                settings.SMTP_USER,
                settings.SMTP_PASSWORD
            )

            smtp.send_message(msg)

        print("Daily transaction email sent successfully")

    except Exception as e:
        print("Email sending failed:", str(e))

    finally:
        db.close()