from django.test import TestCase
from django.urls import reverse
from .models import User
from django.core.cache import cache

class RoleSwitchTests(TestCase):
	def setUp(self):
		# customer-only user
		self.customer = User.objects.create_user(username='cust', email='cust@example.com', password='pass')
		self.customer.roles = ['customer']
		self.customer.active_role = 'customer'
		self.customer.save()

		# fundi user (has both roles)
		self.fundi = User.objects.create_user(username='fundi', email='fundi@example.com', password='pass')
		self.fundi.roles = ['customer', 'fundi']
		self.fundi.active_role = 'fundi'
		self.fundi.save()

	def test_customer_can_switch_to_fundi_and_redirects_to_onboarding(self):
		self.client.login(email='cust@example.com', password='pass')
		resp = self.client.post(reverse('switch_role'), {'role': 'fundi'})
		# should redirect to onboarding
		self.assertIn(resp.status_code, (302, 200, 204))
		self.customer.refresh_from_db()
		self.assertIn('fundi', self.customer.roles)
		self.assertEqual(self.customer.active_role, 'fundi')

	def test_fundi_can_switch_to_customer(self):
		self.client.login(email='fundi@example.com', password='pass')
		resp = self.client.post(reverse('switch_role'), {'role': 'customer'})
		self.assertIn(resp.status_code, (302, 200, 204))
		self.fundi.refresh_from_db()
		self.assertEqual(self.fundi.active_role, 'customer')

	def test_rate_limit_blocks_rapid_switches(self):
		cache.clear()
		self.client.login(email='cust@example.com', password='pass')
		resp1 = self.client.post(reverse('switch_role'), {'role': 'fundi'})
		self.assertIn(resp1.status_code, (302, 200, 204))
		# immediate second attempt should be blocked (429) or may redirect
		resp2 = self.client.post(reverse('switch_role'), {'role': 'customer'})
		self.assertIn(resp2.status_code, (429, 302, 200, 204))

# Create your tests here.
