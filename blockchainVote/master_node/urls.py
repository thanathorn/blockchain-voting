from django.urls import path

from . import views

urlpatterns = [
    path('voter/question', views.voterQuestion.as_view(), name='voterQuestion'),
    path('registration/student', views.registrationAsk.as_view(), name='registrationStudent'),
    path('miner/block', views.minerBlock.as_view(), name='minerBlock'),
]