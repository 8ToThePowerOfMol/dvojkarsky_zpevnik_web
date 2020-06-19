from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='homepage-home'),
    path('download/', views.download, name='homepage-download'),
]