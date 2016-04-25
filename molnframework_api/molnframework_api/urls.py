"""
Definition of urls for molnframework_manager.
"""

from datetime import datetime
from django.conf.urls import url
from django.contrib import admin
from app.forms import BootstrapAuthenticationForm
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register_service/',views.register_service,name='register service'),
    url(r'^register_pod/',views.register_pod,name='register pod'),
    url(r'^report_pod_health/',views.report_pod_health,name='report pod health')
]