from django.urls import path
from . import views

urlpatterns = [
    path('', views.start, name='start'),
    path('result/', views.result, name='result'),

]
