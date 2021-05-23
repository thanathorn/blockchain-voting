from django.db import models


class Voter(models.Model):
    student_id = models.BigIntegerField(null=False, blank=False, unique=True)
    name = models.CharField(null=False, blank=False, max_length=100)
    already_get_credit = models.BooleanField(null=False, blank=False, default=False)


class Question(models.Model):
    question = models.CharField(null=False, blank=False, unique=True, max_length=100)
    credit_required = models.IntegerField(null=False, blank=False, default=1)


class Choice(models.Model):
    choice = models.CharField(null=False, blank=False, max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
