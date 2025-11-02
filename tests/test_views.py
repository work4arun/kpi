
"""
Functional tests for views
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.common.constants import UserRole

User = get_user_model()


class AuthViewsTest(TestCase):
    """Test authentication views"""
    
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(code='CSE', name='Computer Science')
        self.user = User.objects.create_user(
            email='test@rtc.edu',
            password='test123',
            full_name='Test User',
            role=UserRole.FACULTY,
            department=self.dept
        )
    
    def test_login_view_get(self):
        """Test GET request to login page"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in')
    
    def test_login_view_post_valid(self):
        """Test POST request with valid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@rtc.edu',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_login_view_post_invalid(self):
        """Test POST request with invalid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@rtc.edu',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid')


class DashboardViewsTest(TestCase):
    """Test dashboard views"""
    
    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(code='CSE', name='Computer Science')
        self.faculty = User.objects.create_user(
            email='faculty@rtc.edu',
            password='test123',
            full_name='Test Faculty',
            role=UserRole.FACULTY,
            department=self.dept
        )
        self.admin = User.objects.create_superuser(
            email='admin@rtc.edu',
            password='admin123',
            full_name='Test Admin'
        )
    
    def test_faculty_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get(reverse('dashboards:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_faculty_dashboard_authenticated(self):
        """Test faculty can access their dashboard"""
        self.client.login(email='faculty@rtc.edu', password='test123')
        response = self.client.get(reverse('dashboards:dashboard'))
        self.assertEqual(response.status_code, 200)
