
"""
Forms for accounts app
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.accounts.models import User
from apps.departments.models import Department


class LoginForm(forms.Form):
    """Login form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class UserCreateForm(UserCreationForm):
    """Form for creating new users"""
    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'department', 'dean_departments', 
                  'phone', 'employee_id', 'joining_date', 'is_active', 'can_override_deadlines']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'


class UserUpdateForm(forms.ModelForm):
    """Form for updating existing users"""
    class Meta:
        model = User
        fields = ['full_name', 'role', 'department', 'dean_departments', 
                  'phone', 'employee_id', 'joining_date', 'is_active', 'can_override_deadlines']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'


class ProfileUpdateForm(forms.ModelForm):
    """Form for users to update their own profile"""
    class Meta:
        model = User
        fields = ['full_name', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-input'
