
"""
Forms for reviews app
"""
from django import forms
from django.core.validators import MinValueValidator


class ReviewApproveForm(forms.Form):
    """Form for approving a submission"""
    awarded_points = forms.DecimalField(
        label="Awarded Points",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'})
    )
    comment = forms.CharField(
        label="Comment (Optional)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4})
    )
    
    def __init__(self, *args, submission=None, **kwargs):
        super().__init__(*args, **kwargs)
        if submission:
            self.fields['awarded_points'].max_value = submission.sub_parameter.max_points
            self.fields['awarded_points'].help_text = f"Maximum: {submission.sub_parameter.max_points} points"
            self.fields['awarded_points'].initial = submission.sub_parameter.max_points


class ReviewRejectForm(forms.Form):
    """Form for rejecting a submission or requesting revision"""
    comment = forms.CharField(
        label="Comment (Required)",
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4})
    )


class DeanApprovalForm(forms.Form):
    """Form for Dean's final approval"""
    comment = forms.CharField(
        label="Comment (Optional)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4})
    )
