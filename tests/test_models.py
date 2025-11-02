
"""
Unit tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.kpi.models import MainParameter, SubParameter
from apps.submissions.models import Submission
from apps.common.constants import UserRole, SubmissionStatus

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model"""
    
    def setUp(self):
        self.dept = Department.objects.create(code='CSE', name='Computer Science')
    
    def test_create_faculty(self):
        """Test creating a faculty user"""
        user = User.objects.create_user(
            email='faculty@test.com',
            password='test123',
            full_name='Test Faculty',
            role=UserRole.FACULTY,
            department=self.dept
        )
        self.assertEqual(user.email, 'faculty@test.com')
        self.assertTrue(user.is_faculty)
        self.assertFalse(user.is_admin)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@test.com',
            password='admin123',
            full_name='Test Admin'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_admin)


class MainParameterTest(TestCase):
    """Test MainParameter model"""
    
    def test_create_main_parameter(self):
        """Test creating a main parameter"""
        param = MainParameter.objects.create(
            name='Research',
            description='Research publications',
            weightage=25,
            role_owner=UserRole.FACULTY
        )
        self.assertEqual(param.name, 'Research')
        self.assertEqual(param.weightage, 25)


class SubmissionTest(TestCase):
    """Test Submission model"""
    
    def setUp(self):
        self.dept = Department.objects.create(code='CSE', name='Computer Science')
        self.user = User.objects.create_user(
            email='faculty@test.com',
            password='test123',
            full_name='Test Faculty',
            role=UserRole.FACULTY,
            department=self.dept
        )
        self.main_param = MainParameter.objects.create(
            name='Research',
            weightage=25,
            role_owner=UserRole.FACULTY
        )
        self.sub_param = SubParameter.objects.create(
            main_parameter=self.main_param,
            name='Journal Papers',
            max_points=50
        )
    
    def test_create_submission(self):
        """Test creating a submission"""
        submission = Submission.objects.create(
            user=self.user,
            sub_parameter=self.sub_param,
            month=1,
            year=2025,
            status=SubmissionStatus.DRAFT
        )
        self.assertEqual(submission.status, SubmissionStatus.DRAFT)
        self.assertTrue(submission.can_edit())
