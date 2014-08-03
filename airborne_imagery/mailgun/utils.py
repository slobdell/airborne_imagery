import requests
from .constants import API_KEY


def _send_email_with_data(customer_email, subject, text):
    # TODO need to add domain stuff in order to unlock more stuff...
    domain = "sandboxe9b6d6cc30e74befbb13769f0334d1e1.mailgun.org"
    return requests.post(
        "https://api.mailgun.net/v2/%s/messages" % domain,
        auth=("api", API_KEY),
        data={"from": "Airborne Imaging <no-reply@AirborneImaging.com>",
              "to": customer_email,
              "subject": subject,
              "text": text})


def send_order_email(customer_email, order):
    text = "Make sure to actually write some stuff here.  Parameters should just be the order.."
    _send_email_with_data(customer_email, "Digital Picture Delivery!", text)


def send_order_confirmation_email(customer_email, order):
    text = "This email confirms your purchase from AirborneImaging.com.  "
    text += "Your credit card has been charged a total of $%s " % order.total_price
    text += "for %s pictures.  " % order.num_pictures
    text += "Your images are now being processed to the image quality specified in your order.  "
    text += "If there are any issues with your order, your order ID is %s" % order.id
    _send_email_with_data(customer_email, "Order Confirmation", text)
