from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import CustomerSignUp


class LoginAppViewsTestCase(TestCase):
    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser', 
            password='password123'
        )

        # Create a test customer linked to the user
        self.customer = CustomerSignUp.objects.create(user=self.user)

    def test_sign_up_view_valid(self):
        # Test valid signup data
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'password1': 'strongpassword',
            'password2': 'strongpassword',
        })
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_sign_up_view_invalid(self):
        # Test invalid signup (password mismatch)
        response = self.client.post(reverse('sign_up'), {
            'username': 'newuser',
            'password1': 'strongpassword',
            'password2': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stay on the signup page
        self.assertContains(response, 'Your password is not strong enough or both passwords must match')

    def test_login_view_valid(self):
        # Test valid login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_view_invalid(self):
        # Test invalid login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Stay on the login page
        self.assertContains(response, 'Invalid username or password')

    def test_logout_view(self):
        # Log in the user first
        self.client.login(username='testuser', password='password123')

        # Test logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to home
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_edit_customer_view(self):
        # Log in the user first
        self.client.login(username='testuser', password='password123')

        # Test editing the customer's profile
        response = self.client.post(reverse('edit_customer'), {
            'first_name': 'Updated Name',
        })
        self.assertEqual(response.status_code, 302)  # Redirect to home

        # Verify that the customer's profile is updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Updated Name')
