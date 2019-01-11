from rest_framework import serializers
from .models import MyUser, Question, Answers, Share_QandA, Share_Answers, Buddi
import pdb
from django.shortcuts import HttpResponse

class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=MyUser
        fields=("username", "password", "email", "galaxy_num")

    def update(self, instance, validated_data):
        pdb.set_trace()
        return HttpResponse('')


class QuestionSerializer(serializers.ModelSerializer):
    # owner=serializers.StringRelatedField(read_only=True)
    owner=MyUserSerializer(required=True)

    class Meta:
        model=Question
        fields=("question_text","question_tags", "pub_date", "owner",)


class AnswersSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    owner=serializers.StringRelatedField(read_only=True)

    class Meta:
        model=Answers
        fields=("owner", "answerimage", "category")


class ShareQnASerializer(serializers.ModelSerializer):
    questions=QuestionSerializer(required=True)

    class Meta:
        model=Share_QandA
        fields=("owner", "questions")


class ShareAnswersSerializer(serializers.ModelSerializer):
    answers=AnswersSerializer(required=True)

    class Meta:
        model=Share_Answers
        fields=("owner", "answers")


class BuddiSerializer(serializers.ModelSerializer):
    class Meta:
        model=Buddi
        fields=("name", "region", "role", "career", "status")
