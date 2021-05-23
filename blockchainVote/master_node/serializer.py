from rest_framework import serializers
from .models import *


class questionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class choiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class voterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voter
        fields = '__all__'

