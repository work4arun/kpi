
"""
Tests for service layer
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.departments.models import Department
from apps.kpi.models import MainParameter, SubParameter
from apps.submissions.models import Submission
from apps.submissions.services import SubmissionService
from apps.dashboards.services import ScoringService
from apps.common.constants import UserRole, SubmissionStatus

User = get_user_model()


class SubmissionServiceTest(TestCase):
    """Test submission service"""
    
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
        """Test creating a submission via service"""
        submission = SubmissionService.create_submission(
            user=self.user,
            sub_parameter=self.sub_param,
            month=1,
            year=2025
        )
        self.assertIsNotNone(submission)
        self.assertEqual(submission.status, SubmissionStatus.DRAFT)
    
    def test_cannot_edit_submitted(self):
        """Test that submitted submissions cannot be edited"""
        submission = SubmissionService.create_submission(
            user=self.user,
            sub_parameter=self.sub_param,
            month=1,
            year=2025
        )
        submission.status = SubmissionStatus.SUBMITTED
        submission.save()
        
        can_edit = SubmissionService.can_edit_submission(submission, self.user)
        self.assertFalse(can_edit)


class ScoringServiceTest(TestCase):
    """Test scoring service"""
    
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
    
    def test_get_faculty_scores(self):
        """Test getting faculty scores"""
        # Create approved submission
        Submission.objects.create(
            user=self.user,
            sub_parameter=self.sub_param,
            month=1,
            year=2025,
            status=SubmissionStatus.HOD_APPROVED,
            awarded_points=30
        )
        
        scores = ScoringService.get_faculty_scores(self.user, 1, 2025)
        self.assertEqual(scores['total_awarded_points'], 30)
