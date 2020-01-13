from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('packageview/<str:name>', views.packageView, name='packageView'),
]