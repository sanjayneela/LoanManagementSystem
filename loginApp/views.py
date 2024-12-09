from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerSignUpForm, CustomerLoginForm, UpdateCustomerForm
from .models import CustomerSignUp
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Create your views here.

def sign_up_view(request):
    error = ''
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('home'))

    form = CustomerSignUpForm()
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_profile = CustomerSignUp(user=user)
            user_profile.save()
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            user = authenticate(request, username=username, password=password1)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            return HttpResponseRedirect(reverse('login_App:login_customer'))
        else:
            if User.objects.filter(username=request.POST['username']).exists():
                error = 'Customer already exists'
            else:
                error = 'Your password is not strong enough or both passwords must match'

    return render(request, 'loginApp/signup.html', context={'form': form, 'user': "Customer Register", 'error': error})


def login_view(request):
    form = CustomerLoginForm()
    if request.method == 'POST':
        form = CustomerLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'loginApp/login.html', context={'form': form, 'user': "Customer Login", 'error': 'Invalid username or password'})
    return render(request, 'loginApp/login.html', context={'form': form, 'user': "Customer Login"})


@login_required()
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required(login_url='/account/login-customer')
def edit_customer(request):
    customer = CustomerSignUp.objects.get(user=request.user)
    form = UpdateCustomerForm(instance=customer)
    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.save()
            return HttpResponseRedirect(reverse('home'))
    return render(request, 'loginApp/edit.html', context={'form': form})


# Unit Tests for Prototyping Purposes
if __name__ == '__main__':
    import unittest
    from django.test import Client, TestCase

    class LoginAppViewsTestCase(TestCase):
        def setUp(self):
            self.client = Client()
            self.user = User.objects.create_user(username='testuser', password='password123')
            self.customer = CustomerSignUp.objects.create(user=self.user)

        def test_sign_up_view(self):
            response = self.client.post('/signup/', {
                'username': 'newuser',
                'password1': 'strongpassword',
                'password2': 'strongpassword',
            })
            self.assertEqual(response.status_code, 302)  # Should redirect to home

        def test_login_view_valid(self):
            response = self.client.post('/login/', {
                'username': 'testuser',
                'password': 'password123',
            })
            self.assertEqual(response.status_code, 302)  # Should redirect to home

        def test_login_view_invalid(self):
            response = self.client.post('/login/', {
                'username': 'testuser',
                'password': 'wrongpassword',
            })
            self.assertEqual(response.status_code, 200)  # Should render login page with error

        def test_logout_view(self):
            self.client.login(username='testuser', password='password123')
            response = self.client.get('/logout/')
            self.assertEqual(response.status_code, 302)  # Should redirect to home

        def test_edit_customer_view(self):
            self.client.login(username='testuser', password='password123')
            response = self.client.post('/edit/', {
                'first_name': 'Updated Name',
            })
            self.assertEqual(response.status_code, 302)  # Should redirect to home

    # Run tests
    #unittest.main()
