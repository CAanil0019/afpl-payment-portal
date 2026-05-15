import razorpay
from app.config import settings

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


def create_razorpay_order(order_reference, amount):
    amount_float = float(amount)

    payment_data = {
        "amount": int(round(amount_float * 100)),
        "currency": "INR",
        "receipt": order_reference,
        "payment_capture": 1
    }

    order = client.order.create(data=payment_data)
    return order


def verify_razorpay_signature(order_id, payment_id, signature):
    params_dict = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature,
    }

    client.utility.verify_payment_signature(params_dict)
    return True