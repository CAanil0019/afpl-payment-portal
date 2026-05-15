from decimal import Decimal, ROUND_HALF_UP


def calculate_gst(base_amount, gst_percent):
    base = Decimal(str(base_amount))
    gst_rate = Decimal(str(gst_percent))

    gst_amount = (base * gst_rate / Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    total_amount = (base + gst_amount).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    return gst_amount, total_amount