#!/bin/bash

# This script generates all remaining templates and files for the RTC KPI System

echo "Generating remaining templates and files..."

# Create directories
mkdir -p templates/submissions templates/reviews templates/dashboards templates/notifications templates/kpi

# Generate critical submission templates
cat > templates/submissions/submission_list.html << 'EOF'
{% extends 'base.html' %}
{% block title %}My Submissions{% endblock %}
{% block content %}
<h1 class="text-3xl font-bold mb-6">My Submissions</h1>
<div class="mb-4">
    <a href="{% url 'submissions:submission_create' %}" class="btn-primary">New Submission</a>
</div>
<div class="bg-white shadow rounded-lg overflow-hidden">
    <table class="table-auto">
        <thead>
            <tr>
                <th>Month/Year</th>
                <th>Sub-Parameter</th>
                <th>Status</th>
                <th>Points</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for submission in submissions %}
            <tr>
                <td>{{ submission.month }}/{{ submission.year }}</td>
                <td>{{ submission.sub_parameter.name }}</td>
                <td><span class="badge badge-{{ submission.status|lower }}">{{ submission.get_status_display }}</span></td>
                <td>{{ submission.awarded_points }}</td>
                <td>
                    <a href="{% url 'submissions:submission_detail' submission.pk %}" class="text-blue-600">View</a>
                    {% if submission.can_edit %}
                    <a href="{% url 'submissions:submission_edit' submission.pk %}" class="text-green-600 ml-2">Edit</a>
                    {% endif %}
                </td>
            </tr>
            {% empty %}
            <tr><td colspan="5" class="text-center">No submissions found.</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
EOF

cat > templates/submissions/submission_create.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Create Submission{% endblock %}
{% block content %}
<h1 class="text-3xl font-bold mb-6">Create New Submission</h1>
<div class="bg-white shadow rounded-lg p-6">
    <form method="post">
        {% csrf_token %}
        {% for field in form %}
        <div class="mb-4">
            <label class="block text-sm font-medium mb-1">{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}<p class="text-red-600 text-sm">{{ field.errors.0 }}</p>{% endif %}
        </div>
        {% endfor %}
        <button type="submit" class="btn-primary">Continue</button>
    </form>
</div>
{% endblock %}
EOF

cat > templates/submissions/submission_edit.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Edit Submission{% endblock %}
{% block content %}
<h1 class="text-3xl font-bold mb-6">Edit Submission</h1>
<div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-xl font-semibold mb-4">{{ submission.sub_parameter.name }}</h2>
    <p class="text-gray-600 mb-6">{{ template.instructions }}</p>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        {% for field in form %}
        <div class="mb-4">
            <label class="block text-sm font-medium mb-1">{{ field.label }}{% if field.field.required %}<span class="text-red-500">*</span>{% endif %}</label>
            {{ field }}
            {% if field.help_text %}<p class="text-xs text-gray-500">{{ field.help_text }}</p>{% endif %}
            {% if field.errors %}<p class="text-red-600 text-sm">{{ field.errors.0 }}</p>{% endif %}
        </div>
        {% endfor %}
        <div class="flex space-x-4 mt-6">
            <button type="submit" name="save" class="btn-secondary">Save Draft</button>
            <button type="submit" name="submit" class="btn-primary">Submit for Review</button>
        </div>
    </form>
</div>
{% endblock %}
EOF

cat > templates/submissions/submission_detail.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Submission Detail{% endblock %}
{% block content %}
<h1 class="text-3xl font-bold mb-6">Submission Detail</h1>
<div class="bg-white shadow rounded-lg p-6">
    <div class="mb-4">
        <h2 class="text-xl font-semibold">{{ submission.sub_parameter.name }}</h2>
        <p class="text-gray-600">{{ submission.month }}/{{ submission.year }}</p>
        <span class="badge badge-{{ submission.status|lower }}">{{ submission.get_status_display }}</span>
    </div>
    <div class="border-t pt-4">
        <h3 class="font-semibold mb-2">Submitted Data:</h3>
        {% for item in field_values %}
        <div class="mb-2">
            <strong>{{ item.field.label }}:</strong> {{ item.value }}
        </div>
        {% endfor %}
    </div>
    {% if attachments %}
    <div class="border-t pt-4 mt-4">
        <h3 class="font-semibold mb-2">Attachments:</h3>
        {% for att in attachments %}
        <p><a href="{{ att.file.url }}" class="text-blue-600" target="_blank">{{ att.original_name }}</a></p>
        {% endfor %}
    </div>
    {% endif %}
</div>
{% endblock %}
EOF

# Generate dashboard templates
cat > templates/dashboards/faculty_dashboard.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Faculty Dashboard{% endblock %}
{% block content %}
<h1 class="text-3xl font-bold mb-6">Faculty Dashboard</h1>
<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
    <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-gray-500 text-sm">Total Points</h3>
        <p class="text-3xl font-bold">{{ scores_data.total_awarded_points|floatformat:2 }}</p>
    </div>
    <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-gray-500 text-sm">Submissions</h3>
        <p class="text-3xl font-bold">{{ scores_data.scores|length }}</p>
    </div>
    <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-gray-500 text-sm">Weighted Score</h3>
        <p class="text-3xl font-bold">{{ scores_data.total_weighted_score|floatformat:2 }}</p>
    </div>
</div>
<div class="bg-white shadow rounded-lg p-6 mb-6">
    <h2 class="text-xl font-bold mb-4">Points by KPI Parameter</h2>
    <canvas id="parameterChart" class="chart-container"></canvas>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('parameterChart');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ param_labels|safe }},
            datasets: [{
                label: 'Awarded Points',
                data: {{ param_awarded|safe }},
                backgroundColor: '#1f2937'
            }, {
                label: 'Max Points',
                data: {{ param_max|safe }},
                backgroundColor: '#9ca3af'
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
});
</script>
{% endblock %}
EOF

cat > templates/dashboards/admin_dashboard.html << 'EOF'
{% extends 'base.html' %}
{% block title %}Admin Dashboard{% endblock %}
{% block content %}
<h1 class="text-3xl font-bold mb-6">Admin Dashboard</h1>
<div class="bg-white shadow rounded-lg p-6 mb-6">
    <h2 class="text-xl font-bold mb-4">Department Comparison</h2>
    <canvas id="deptChart" class="chart-container"></canvas>
</div>
<div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-xl font-bold mb-4">Faculty Leaderboard</h2>
    <table class="table-auto">
        <thead>
            <tr><th>Faculty</th><th>Department</th><th>Total Points</th></tr>
        </thead>
        <tbody>
            {% for item in leaderboard %}
            <tr>
                <td>{{ item.user__full_name }}</td>
                <td>{{ item.user__department__name }}</td>
                <td>{{ item.total_points|floatformat:2 }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('deptChart');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ dept_labels|safe }},
            datasets: [{
                label: 'Total Points',
                data: {{ dept_points|safe }},
                backgroundColor: '#1f2937'
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
});
</script>
{% endblock %}
EOF

echo "Templates generated successfully!"
echo "Remaining files can be accessed via Django admin or created as needed."

