#!/usr/bin/env python
"""
Test script to verify dashboard functions work correctly
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtc_kpi.settings')
django.setup()

from apps.dashboards.services import ScoringService
from apps.accounts.models import User
from apps.common.utils import get_current_month_year

def test_status_counts():
    """Test that status counts return proper SimpleNamespace"""
    print("\n=== Testing Status Counts ===")
    month, year = get_current_month_year()
    
    # Test with no filters (should work even with no data)
    status_counts = ScoringService.get_submission_status_counts(month=month, year=year)
    
    print(f"Status counts type: {type(status_counts)}")
    print(f"DRAFT: {status_counts.DRAFT}")
    print(f"SUBMITTED: {status_counts.SUBMITTED}")
    print(f"APPROVED: {status_counts.APPROVED}")
    print(f"REJECTED: {status_counts.REJECTED}")
    print(f"HOD_APPROVED: {status_counts.HOD_APPROVED}")
    print(f"DEAN_APPROVED: {status_counts.DEAN_APPROVED}")
    print(f"NEEDS_REVISION: {status_counts.NEEDS_REVISION}")
    print("✓ Status counts work correctly!")
    return True

def test_faculty_scores():
    """Test that faculty scores return proper structure"""
    print("\n=== Testing Faculty Scores ===")
    month, year = get_current_month_year()
    
    # Get any faculty user
    try:
        faculty = User.objects.filter(role='FACULTY', is_active=True).first()
        if not faculty:
            print("⚠ No faculty users found, skipping test")
            return True
            
        scores_data = ScoringService.get_faculty_scores(faculty, month, year)
        
        print(f"Scores data keys: {scores_data.keys()}")
        print(f"Total awarded points: {scores_data.get('total_awarded_points', 0)}")
        print(f"Total max points: {scores_data.get('total_max_points', 0)}")
        print(f"Total weighted score: {scores_data.get('total_weighted_score', 0)}")
        print(f"Number of parameters: {len(scores_data.get('scores', {}))}")
        
        # Verify required keys exist
        assert 'scores' in scores_data
        assert 'total_weighted_score' in scores_data
        assert 'total_awarded_points' in scores_data
        assert 'total_max_points' in scores_data
        
        print("✓ Faculty scores work correctly!")
        return True
    except Exception as e:
        print(f"✗ Error testing faculty scores: {e}")
        return False

def test_hod_scores():
    """Test that HoD scores return proper structure"""
    print("\n=== Testing HoD Scores ===")
    month, year = get_current_month_year()
    
    # Get any HoD user
    try:
        hod = User.objects.filter(role='HOD', is_active=True).first()
        if not hod:
            print("⚠ No HoD users found, skipping test")
            return True
            
        scores_data = ScoringService.get_hod_scores(hod, month, year)
        
        print(f"Scores data keys: {scores_data.keys()}")
        print(f"Total awarded points: {scores_data.get('total_awarded_points', 0)}")
        print(f"Total max points: {scores_data.get('total_max_points', 0)}")
        print(f"Total weighted score: {scores_data.get('total_weighted_score', 0)}")
        
        # Verify required keys exist
        assert 'scores' in scores_data
        assert 'total_weighted_score' in scores_data
        assert 'total_awarded_points' in scores_data
        assert 'total_max_points' in scores_data
        
        print("✓ HoD scores work correctly!")
        return True
    except Exception as e:
        print(f"✗ Error testing HoD scores: {e}")
        return False

def test_department_comparison():
    """Test department comparison"""
    print("\n=== Testing Department Comparison ===")
    month, year = get_current_month_year()
    
    try:
        dept_comparison = ScoringService.get_department_comparison(month, year)
        print(f"Number of departments: {len(dept_comparison)}")
        if dept_comparison:
            print(f"First department keys: {dept_comparison[0].keys()}")
        print("✓ Department comparison works correctly!")
        return True
    except Exception as e:
        print(f"✗ Error testing department comparison: {e}")
        return False

def test_faculty_leaderboard():
    """Test faculty leaderboard"""
    print("\n=== Testing Faculty Leaderboard ===")
    month, year = get_current_month_year()
    
    try:
        leaderboard = ScoringService.get_faculty_leaderboard(month=month, year=year, limit=20)
        print(f"Number of faculty in leaderboard: {len(leaderboard)}")
        print("✓ Faculty leaderboard works correctly!")
        return True
    except Exception as e:
        print(f"✗ Error testing faculty leaderboard: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("DASHBOARD FUNCTIONS TEST SUITE")
    print("=" * 60)
    
    tests = [
        test_status_counts,
        test_faculty_scores,
        test_hod_scores,
        test_department_comparison,
        test_faculty_leaderboard,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED!")
        sys.exit(1)
