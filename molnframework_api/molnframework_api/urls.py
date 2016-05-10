"""
Definition of urls for molnframework_manager.
"""

from datetime import datetime
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'',admin.site.urls ),
    url(r'^docker/add/',views.add_docker_image),
    url(r'^docker/get/',views.get_docker_image),
    url(r'^docker/build/begin/',views.begin_build_docker_image),
    url(r'^docker/build/end/',views.end_build_docker_image),
    url(r'^docker/build/',views.build_docker_image),
    url(r'^docker/push/begin/',views.begin_push_docker_image),
    url(r'^docker/push/end/',views.end_push_docker_image),
    url(r'^docker/push/',views.push_docker_image),
    url(r'^compute_app/add/',views.add_compute_app),
    url(r'^compute_app/create/',views.create_compute_app),
    url(r'^register_service/',views.register_service,name='register service'),
    url(r'^register_pod/',views.register_pod,name='register pod'),
    url(r'^report_pod_health/',views.report_pod_health,name='report pod health'),
    url(r'^get_app_resources/',views.get_app_resources,name='get app resources')
]
