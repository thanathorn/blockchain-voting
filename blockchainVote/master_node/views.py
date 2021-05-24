import hashlib

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializer import *
from django.core.exceptions import *

class voterQuestion(APIView):
    def get(self, request):
        resp = []
        questions = Question.objects.all()
        questionSerialized = questionSerializer(questions, many=True).data
        for question in questions:
            answers = question.choice_set.all()
            answers_list = []
            for answer in answers:
                answers_list.append({
                    "answer": answer.choice,
                    "address": hashlib.sha224(answer.choice.encode()).hexdigest()
                })
            toAppend = {
                "question": {
                    "question_id": question.id,
                    "question": question.question,
                    "vote_accepted": question.credit_required
                },
                "answers": answers_list
            }
            resp.append(toAppend)

        for question in questions:
            question.choice_set.all().values()
        return Response(resp)


class registrationAsk(APIView):
    def post(self, request, *args, **kwargs):
        student_id = request.data.get("student_id", None)
        try:
            voter = Voter.objects.get(student_id=student_id)
            return Response({
                "already_get_credit": 1 == voter.already_get_credit
            })
        except:
            return Response({
                "result": 0,
                "data": "NOT_EXIST"
            })


class minerBlock(APIView):
    def get(self, request):
        try:
            with open('../currentBlock.txt', 'rb') as f:
                x = f.read()
                return Response({"block": x})
        except:
            return Response("", 404)

