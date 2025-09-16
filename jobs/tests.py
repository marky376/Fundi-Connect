from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Job, Payment, Category
from .mpesa_api import MpesaAPI

class PaymentModelTest(TestCase):
	def setUp(self):
		User = get_user_model()
		self.customer = User.objects.create_user(username='customer', email='customer@test.com', password='pass', role='customer')
		self.category = Category.objects.create(name='Plumbing')
		self.job = Job.objects.create(title='Fix sink', description='Leaking', customer=self.customer, category=self.category, location='Nairobi')

	def test_create_payment(self):
		payment = Payment.objects.create(job=self.job, customer=self.customer, amount=500, phone_number='254700000000')
		self.assertEqual(payment.status, 'initiated')
		self.assertEqual(payment.amount, 500)
		self.assertEqual(payment.customer, self.customer)

class PaymentViewTest(TestCase):
	def setUp(self):
		User = get_user_model()
		self.customer = User.objects.create_user(username='customer', email='customer@test.com', password='pass', role='customer')
		self.category = Category.objects.create(name='Plumbing')
		self.job = Job.objects.create(title='Fix sink', description='Leaking', customer=self.customer, category=self.category, location='Nairobi')

	def test_payment_initiation_view(self):
		self.client.login(email='customer@test.com', password='pass')
		url = reverse('jobs:initiate_payment', args=[self.job.id])
		response = self.client.post(url, {'amount': 500, 'phone_number': '254700000000'})
		self.assertEqual(response.status_code, 302)  # Redirect after payment
		payment = Payment.objects.filter(job=self.job).last()
		self.assertIsNotNone(payment)
		self.assertEqual(payment.amount, 500)
		self.assertEqual(payment.status, 'pending')
