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
        url(r'^register/',views.register,name='register')
]