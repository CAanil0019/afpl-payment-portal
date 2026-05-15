from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")

    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

    CCAVENUE_MERCHANT_ID = os.getenv("CCAVENUE_MERCHANT_ID")
    CCAVENUE_ACCESS_CODE = os.getenv("CCAVENUE_ACCESS_CODE")
    CCAVENUE_WORKING_KEY = os.getenv("CCAVENUE_WORKING_KEY")
    CCAVENUE_REDIRECT_URL = os.getenv("CCAVENUE_REDIRECT_URL")
    CCAVENUE_CANCEL_URL = os.getenv("CCAVENUE_CANCEL_URL")

    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    REPORT_TO = os.getenv("REPORT_TO")

    SECRET_KEY = os.getenv("SECRET_KEY")

settings = Settings()


settings = Settings()

settings = Settings()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
REPORT_TO = os.getenv("REPORT_TO")