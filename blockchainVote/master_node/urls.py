from django.urls import path

from . import views

urlpatterns = [
    path('voter/question', views.voterQuestion.as_view(), name='voterQuestion'),
]