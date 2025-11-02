
"""
Forms for submissions app
"""
from django import forms
from apps.kpi.models import SubParameter
from apps.kpi.services import KPIService
from apps.common.constants import MONTHS
from datetime import datetime


class SubmissionCreateForm(forms.Form):
    """Form for creating a new submission (selecting sub-parameter and month/year)"""
    sub_parameter = forms.ModelChoiceField(
        queryset=SubParameter.objects.none(),
        label="KPI Sub-Parameter",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    month = forms.ChoiceField(
        choices=MONTHS,
        label="Month",
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    year = forms.IntegerField(
        label="Year",
        min_value=2020,
        max_value=2030,
        widget=forms.NumberInput(attrs={'class': 'form-input'}),
        initial=datetime.now().year
    )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter sub-parameters based on user role
            role_owner = user.role if user.role in ['FACULTY', 'HOD'] else 'FACULTY'
            self.fields['sub_parameter'].queryset = SubParameter.objects.filter(
                main_parameter__role_owner=role_owner,
                is_active=True
            ).select_related('main_parameter').order_by('main_parameter__name', 'name')
        
        # Set default month to current month
        self.fields['month'].initial = datetime.now().month
