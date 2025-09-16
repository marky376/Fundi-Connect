import requests
from django.conf import settings

class MpesaAPI:
    def __init__(self):
        self.base_url = getattr(settings, 'MPESA_BASE_URL', 'https://sandbox.safaricom.co.ke')
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', 'demo')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', 'demo')
        self.shortcode = getattr(settings, 'MPESA_SHORTCODE', '123456')
        self.passkey = getattr(settings, 'MPESA_PASSKEY', 'demo')

    def authenticate(self):
        # Mock authentication for demo
        return 'mock_access_token'

    def initiate_stk_push(self, phone_number, amount, account_reference, transaction_desc):
        # This is a mock implementation. Replace with real API call for production.
        # Simulate success response
        return {
            'ResponseCode': '0',
            'ResponseDescription': 'Success. Request accepted for processing',
            'MerchantRequestID': '12345',
            'CheckoutRequestID': '67890',
            'CustomerMessage': 'Success. Please enter your Mpesa PIN to complete the transaction.'
        }
