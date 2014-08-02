import stripe
from .constants import get_secret_key


def charge_card(stripe_token, amount_in_cents, customer_email):
    stripe.api_key = get_secret_key()
    try:
        stripe.Charge.create(
            amount=amount_in_cents,
            currency="usd",
            card=stripe_token,
            description=customer_email
        )
    except stripe.CardError as e:
        return False, e.message
    return True, ""
