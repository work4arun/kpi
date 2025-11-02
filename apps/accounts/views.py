
"""
Views for accounts app - Authentication and user management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from apps.accounts.models import User
from apps.accounts.forms import LoginForm, UserCreateForm, UserUpdateForm, ProfileUpdateForm
from apps.common.decorators import admin_required
from apps.common.utils import log_activity
from apps.common.constants import ActivityAction
import csv
from django.http import HttpResponse


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboards:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.full_name}!')
                    return redirect('dashboards:dashboard')
                else:
                    messages.error(request, 'Your account is inactive.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """User profile"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)


@admin_required
def user_list(request):
    """List all users (Admin only)"""
    users = User.objects.select_related('department').order_by('full_name')
    
    # Filters
    role = request.GET.get('role')
    department = request.GET.get('department')
    is_active = request.GET.get('is_active')
    search = request.GET.get('search')
    
    if role:
        users = users.filter(role=role)
    if department:
        users = users.filter(department_id=department)
    if is_active:
        users = users.filter(is_active=(is_active == 'true'))
    if search:
        users = users.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    context = {
        'users': users,
        'role_filter': role,
        'department_filter': department,
        'is_active_filter': is_active,
        'search_query': search
    }
    return render(request, 'accounts/user_list.html', context)


@admin_required
def user_create(request):
    """Create new user (Admin only)"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_activity(
                actor=request.user,
                action=ActivityAction.CREATED,
                target=user,
                description=f"Created user: {user.full_name}",
                request=request
            )
            messages.success(request, f'User {user.full_name} created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserCreateForm()
    
    context = {'form': form}
    return render(request, 'accounts/user_form.html', context)


@admin_required
def user_update(request, pk):
    """Update user (Admin only)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            log_activity(
                actor=request.user,
                action=ActivityAction.UPDATED,
                target=user,
                description=f"Updated user: {user.full_name}",
                request=request
            )
            messages.success(request, f'User {user.full_name} updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserUpdateForm(instance=user)
    
    context = {'form': form, 'user_obj': user}
    return render(request, 'accounts/user_form.html', context)


@admin_required
def user_delete(request, pk):
    """Delete user (Admin only)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user_name = user.full_name
        log_activity(
            actor=request.user,
            action=ActivityAction.DELETED,
            target=user,
            description=f"Deleted user: {user_name}",
            request=request
        )
        user.delete()
        messages.success(request, f'User {user_name} deleted successfully.')
        return redirect('accounts:user_list')
    
    context = {'user_obj': user}
    return render(request, 'accounts/user_confirm_delete.html', context)


@admin_required
def user_import_csv(request):
    """Import users from CSV (Admin only)"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            error_count = 0
            
            for row in reader:
                try:
                    # Create user from CSV row
                    User.objects.create_user(
                        email=row['email'],
                        password=row.get('password', 'rtc@123'),  # Default password
                        full_name=row['full_name'],
                        role=row['role'],
                        department_id=row.get('department_id'),
                        phone=row.get('phone', ''),
                        employee_id=row.get('employee_id', ''),
                    )
                    created_count += 1
                except Exception as e:
                    error_count += 1
                    continue
            
            messages.success(request, f'Created {created_count} users. Errors: {error_count}')
        except Exception as e:
            messages.error(request, f'Error importing CSV: {str(e)}')
        
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_import_csv.html')
