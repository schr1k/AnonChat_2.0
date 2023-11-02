import json

from config import *

from yookassa import Configuration, Payment
import uuid

Configuration.account_id = YOOKASSA_ACCOUNT_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def get_payments() -> str:
    payments = Payment.list()
    return payments.json()


def create_payment(amount: int, description: str) -> tuple[str, str]:
    idempotence_key = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": float(str(amount)),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": RETURN_URL
        },
        "description": description
    }, idempotence_key)
    return payment.confirmation.confirmation_url, payment.id


def get_payment_status(payment_id: str):
    payment = Payment.find_one(payment_id)
    return json.loads(payment.json())['status']


def confirm_payment(payment_id: str):
    idempotence_key = str(uuid.uuid4())
    response = Payment.capture(
        payment_id,
        {},
        idempotence_key
    )
    return response.json()
