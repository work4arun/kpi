
"""
Service layer for dashboard data aggregation and scoring
"""
from django.db.models import Sum, Avg, Count, Q
from apps.submissions.models import Submission
from apps.common.constants import SubmissionStatus, RoleOwner
from apps.kpi.models import MainParameter, HodSubParamMapping
from apps.departments.models import Department
from decimal import Decimal


class ScoringService:
    """
    Service for calculating scores and aggregating data for dashboards
    """
    
    @staticmethod
    def get_faculty_scores(faculty, month, year):
        """
        Calculate faculty scores by main parameter for a given window
        """
        submissions = Submission.objects.filter(
            user=faculty,
            month=month,
            year=year,
            status__in=[SubmissionStatus.HOD_APPROVED, SubmissionStatus.DEAN_APPROVED]
        ).select_related('sub_parameter', 'sub_parameter__main_parameter')
        
        # Group by main parameter
        scores = {}
        for submission in submissions:
            main_param = submission.sub_parameter.main_parameter
            if main_param.name not in scores:
                scores[main_param.name] = {
                    'main_parameter': main_param,
                    'awarded_points': 0,
                    'max_points': 0,
                    'submissions': []
                }
            
            scores[main_param.name]['awarded_points'] += float(submission.awarded_points)
            scores[main_param.name]['max_points'] += submission.sub_parameter.max_points
            scores[main_param.name]['submissions'].append(submission)
        
        # Calculate weighted scores
        total_weighted_score = 0
        for param_name, data in scores.items():
            weighted_score = data['awarded_points'] * float(data['main_parameter'].weightage)
            data['weighted_score'] = weighted_score
            total_weighted_score += weighted_score
        
        # Calculate totals with defaults for empty scores
        total_awarded_points = sum(s['awarded_points'] for s in scores.values()) if scores else 0
        total_max_points = sum(s['max_points'] for s in scores.values()) if scores else 0
        
        return {
            'scores': scores,
            'total_weighted_score': total_weighted_score,
            'total_awarded_points': total_awarded_points,
            'total_max_points': total_max_points
        }
    
    @staticmethod
    def get_hod_scores(hod, month, year):
        """
        Calculate HoD scores including team average for mapped parameters
        """
        # Get HoD's own submissions
        hod_submissions = Submission.objects.filter(
            user=hod,
            month=month,
            year=year,
            status__in=[SubmissionStatus.HOD_APPROVED, SubmissionStatus.DEAN_APPROVED]
        ).select_related('sub_parameter', 'sub_parameter__main_parameter')
        
        scores = {}
        
        for submission in hod_submissions:
            main_param = submission.sub_parameter.main_parameter
            sub_param = submission.sub_parameter
            
            if main_param.name not in scores:
                scores[main_param.name] = {
                    'main_parameter': main_param,
                    'awarded_points': 0,
                    'max_points': 0,
                    'submissions': []
                }
            
            # Base points
            awarded_points = float(submission.awarded_points)
            
            # Check for team average mapping
            mappings = HodSubParamMapping.objects.filter(
                hod_subparam=sub_param,
                is_active=True
            ).select_related('faculty_subparam')
            
            if mappings.exists():
                # Calculate team average for mapped faculty parameter
                mapping = mappings.first()
                faculty_avg = ScoringService.get_department_average_for_subparam(
                    hod.department,
                    mapping.faculty_subparam,
                    month,
                    year
                )
                
                # Add team average to HoD's points (capped at max)
                total_points = awarded_points + faculty_avg
                awarded_points = min(total_points, sub_param.max_points)
            
            scores[main_param.name]['awarded_points'] += awarded_points
            scores[main_param.name]['max_points'] += sub_param.max_points
            scores[main_param.name]['submissions'].append(submission)
        
        # Calculate weighted scores
        total_weighted_score = 0
        for param_name, data in scores.items():
            weighted_score = data['awarded_points'] * float(data['main_parameter'].weightage)
            data['weighted_score'] = weighted_score
            total_weighted_score += weighted_score
        
        # Calculate totals with defaults for empty scores
        total_awarded_points = sum(s['awarded_points'] for s in scores.values()) if scores else 0
        total_max_points = sum(s['max_points'] for s in scores.values()) if scores else 0
        
        return {
            'scores': scores,
            'total_weighted_score': total_weighted_score,
            'total_awarded_points': total_awarded_points,
            'total_max_points': total_max_points
        }
    
    @staticmethod
    def get_department_average_for_subparam(department, sub_parameter, month, year):
        """
        Calculate average points for a sub-parameter across faculty in a department
        """
        avg = Submission.objects.filter(
            user__department=department,
            user__role=RoleOwner.FACULTY,
            sub_parameter=sub_parameter,
            month=month,
            year=year,
            status__in=[SubmissionStatus.HOD_APPROVED, SubmissionStatus.DEAN_APPROVED]
        ).aggregate(avg_points=Avg('awarded_points'))
        
        return float(avg['avg_points'] or 0)
    
    @staticmethod
    def get_department_comparison(month, year):
        """
        Get department-wise comparison of total scores
        """
        departments = Department.objects.filter(is_active=True)
        comparison = []
        
        for dept in departments:
            # Get all faculty submissions for this department
            total_points = Submission.objects.filter(
                user__department=dept,
                user__role=RoleOwner.FACULTY,
                month=month,
                year=year,
                status__in=[SubmissionStatus.HOD_APPROVED, SubmissionStatus.DEAN_APPROVED]
            ).aggregate(total=Sum('awarded_points'))['total'] or 0
            
            faculty_count = dept.users.filter(role=RoleOwner.FACULTY, is_active=True).count()
            
            comparison.append({
                'department': dept,
                'total_points': float(total_points),
                'faculty_count': faculty_count,
                'average_points': float(total_points) / faculty_count if faculty_count > 0 else 0
            })
        
        return sorted(comparison, key=lambda x: x['total_points'], reverse=True)
    
    @staticmethod
    def get_main_parameter_breakdown(department, month, year):
        """
        Get breakdown by main parameter for a department
        """
        main_params = MainParameter.objects.filter(is_active=True)
        breakdown = []
        
        for param in main_params:
            total_points = Submission.objects.filter(
                user__department=department,
                sub_parameter__main_parameter=param,
                month=month,
                year=year,
                status__in=[SubmissionStatus.HOD_APPROVED, SubmissionStatus.DEAN_APPROVED]
            ).aggregate(total=Sum('awarded_points'))['total'] or 0
            
            breakdown.append({
                'main_parameter': param,
                'total_points': float(total_points)
            })
        
        return breakdown
    
    @staticmethod
    def get_submission_status_counts(user=None, department=None, month=None, year=None):
        """
        Get counts of submissions by status.
        Returns a SimpleNamespace object with status counts as attributes for template access.
        """
        from types import SimpleNamespace
        
        queryset = Submission.objects.all()
        
        if user:
            queryset = queryset.filter(user=user)
        if department:
            queryset = queryset.filter(user__department=department)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        counts = queryset.values('status').annotate(count=Count('id'))
        raw_counts = {item['status']: item['count'] for item in counts}
        
        # Normalize status counts for template access
        # Combine HOD_APPROVED and DEAN_APPROVED into APPROVED
        normalized_counts = {
            'DRAFT': raw_counts.get(SubmissionStatus.DRAFT, 0),
            'SUBMITTED': raw_counts.get(SubmissionStatus.SUBMITTED, 0),
            'NEEDS_REVISION': raw_counts.get(SubmissionStatus.NEEDS_REVISION, 0),
            'APPROVED': raw_counts.get(SubmissionStatus.HOD_APPROVED, 0) + raw_counts.get(SubmissionStatus.DEAN_APPROVED, 0),
            'REJECTED': raw_counts.get(SubmissionStatus.REJECTED, 0),
            'HOD_APPROVED': raw_counts.get(SubmissionStatus.HOD_APPROVED, 0),
            'DEAN_APPROVED': raw_counts.get(SubmissionStatus.DEAN_APPROVED, 0),
        }
        
        # Return as a simple namespace object that supports dot notation
        return SimpleNamespace(**normalized_counts)
    
    @staticmethod
    def get_faculty_leaderboard(department=None, month=None, year=None, limit=10):
        """
        Get top faculty by total points
        """
        queryset = Submission.objects.filter(
            user__role=RoleOwner.FACULTY,
            status__in=[SubmissionStatus.HOD_APPROVED, SubmissionStatus.DEAN_APPROVED]
        )
        
        if department:
            queryset = queryset.filter(user__department=department)
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        
        leaderboard = queryset.values('user__id', 'user__full_name', 'user__department__name').annotate(
            total_points=Sum('awarded_points'),
            submission_count=Count('id')
        ).order_by('-total_points')[:limit]
        
        return list(leaderboard)
