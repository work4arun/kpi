
"""
ASGI config for RTC KPI System project.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rtc_kpi.settings')
application = get_asgi_application()
