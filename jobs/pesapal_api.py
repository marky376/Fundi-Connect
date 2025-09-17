# Pesapal integration scaffold
import requests
from django.conf import settings

PESAPAL_CONSUMER_KEY = getattr(settings, 'PESAPAL_CONSUMER_KEY', '')
PESAPAL_CONSUMER_SECRET = getattr(settings, 'PESAPAL_CONSUMER_SECRET', '')

def initiate_pesapal_payment(amount, description, phone_number, callback_url):
    # Placeholder for Pesapal payment initiation
    # You will need to fill in the actual API call and authentication
    payload = {
        'amount': amount,
        'description': description,
        'phone_number': phone_number,
        'callback_url': callback_url,
    }
    # Example: response = requests.post(PESAPAL_API_URL, data=payload, auth=(PESAPAL_CONSUMER_KEY, PESAPAL_CONSUMER_SECRET))
    # return response.json()
    return {'status': 'initiated', 'redirect_url': '/'}

def verify_pesapal_payment(payment_id):
    # Placeholder for Pesapal payment verification
    # You will need to fill in the actual API call
    return {'status': 'completed'}
import requests
from django.conf import settings

class PesapalAPI:
    def __init__(self):
        self.consumer_key = settings.PESAPAL_CONSUMER_KEY
        self.consumer_secret = settings.PESAPAL_CONSUMER_SECRET
        self.base_url = "https://pay.pesapal.com/v3"

    def get_access_token(self):
        url = f"{self.base_url}/api/Auth/RequestToken"
        response = requests.post(url, auth=(self.consumer_key, self.consumer_secret))
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print("Pesapal Auth Error:", response.status_code, response.text)
            raise
        return response.json().get('token')

    def initiate_payment(self, amount, currency, description, customer_email, customer_phone):
        token = self.get_access_token()
        url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "Amount": amount,
            "Currency": currency,
            "Description": description,
            "Customer": {
                "Email": customer_email,
                "PhoneNumber": customer_phone
            },
            "CallbackUrl": "https://yourdomain.com/pesapal/callback/"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
