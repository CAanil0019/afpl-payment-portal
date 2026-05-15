from datetime import datetime
import random
import string


def generate_order_reference():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"AFPL-{timestamp}-{random_part}"