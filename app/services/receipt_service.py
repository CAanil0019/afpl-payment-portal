from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os


def generate_receipt_pdf(transaction):
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    logo_path = os.path.join(
        os.getcwd(),
        "app",
        "static",
        "ANNAPURNA.png"
    )

    if os.path.exists(logo_path):
        pdf.drawImage(
            logo_path,
            60,
            height - 90,
            width=220,
            height=60,
            preserveAspectRatio=True,
            mask="auto"
        )

    y = height - 120

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(60, y, "Annapurna Finance Pvt. Ltd.")
    y -= 25

    pdf.setFont("Helvetica", 11)
    pdf.drawString(60, y, "Customer Service Request Payment Receipt")
    y -= 40

    pdf.line(60, y, width - 60, y)
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y, "Receipt Details")
    y -= 25

    pdf.setFont("Helvetica", 10)

    rows = [
        ("Reference No", transaction.order_reference),
        ("Customer Name", transaction.customer_name),
        ("Loan Account No", transaction.loan_account_number),
        ("Mobile No", transaction.mobile_number),
        ("Charge Type", transaction.charge_type),
        ("Base Amount", f"INR {transaction.base_amount}"),
        ("GST Amount", f"INR {transaction.gst_amount}"),
        ("Total Paid", f"INR {transaction.total_amount}"),
        ("Gateway", transaction.gateway_name),
        ("Payment Status", transaction.payment_status),
        ("Payment ID", transaction.gateway_payment_id or ""),
        ("Transaction Date", str(transaction.transaction_date)),
    ]

    for label, value in rows:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(60, y, f"{label}:")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(200, y, str(value))
        y -= 22

    y -= 20
    pdf.line(60, y, width - 60, y)
    y -= 25

    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(
        60,
        y,
        "This is a system-generated receipt and does not require signature."
    )

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer