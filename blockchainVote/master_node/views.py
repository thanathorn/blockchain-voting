from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializer import *


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
                    "address": answer.address
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
