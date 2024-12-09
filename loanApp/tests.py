from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import loanRequest, loanTransaction, CustomerLoan

class LoanAppViewsTestCase(TestCase):

    def setUp(self):
        # Create test user and customer
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user.customer = CustomerLoan.objects.create(customer=self.user, total_loan=10000, payable_loan=8000)
        self.user.customer.save()

        # Create loan requests and transactions
        self.loan_request = loanRequest.objects.create(customer=self.user.customer, amount=5000, status='approved')
        self.loan_transaction = loanTransaction.objects.create(customer=self.user.customer, payment=2000)

        # Log in the user
        self.client.force_login(self.user)

    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_loan_request_view_get(self):
        response = self.client.get('/loan-request/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loanApp/loanrequest.html')
        self.assertIn('form', response.context)

    def test_loan_request_view_post(self):
        data = {'amount': 3000, 'status': 'pending'}
        response = self.client.post('/loan-request/', data)
        self.assertEqual(response.status_code, 302)  # Redirects after success
        self.assertEqual(loanRequest.objects.count(), 2)  # New request created

    def test_loan_payment_view_get(self):
        response = self.client.get('/loan-payment/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loanApp/payment.html')
        self.assertIn('form', response.context)

    def test_loan_payment_view_post(self):
        data = {'payment': 1000}
        response = self.client.post('/loan-payment/', data)
        self.assertEqual(response.status_code, 302)  # Redirects after success
        self.assertEqual(loanTransaction.objects.count(), 2)  # New transaction created

    def test_user_transaction_view(self):
        response = self.client.get('/user-transactions/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loanApp/user_transaction.html')
        self.assertIn('transactions', response.context)
        self.assertEqual(len(response.context['transactions']), 1)

    def test_user_loan_history_view(self):
        response = self.client.get('/user-loan-history/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loanApp/user_loan_history.html')
        self.assertIn('loans', response.context)
        self.assertEqual(len(response.context['loans']), 1)

    def test_user_dashboard_view(self):
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loanApp/user_dashboard.html')
        self.assertIn('totalLoan', response.context)
        self.assertEqual(response.context['totalLoan'], 10000)
        self.assertIn('totalPayable', response.context)
        self.assertEqual(response.context['totalPayable'], 8000)
        self.assertIn('totalPaid', response.context)
        self.assertEqual(response.context['totalPaid'], 2000)

    def test_404_view(self):
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'notFound.html')
