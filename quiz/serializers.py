from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from backend.models import Answer, Question, UserResponseToQuestion, Quizzes


class UserCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name',)


class LoginResponseSerializer(TokenRefreshSerializer):
    ...


class AuthLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = User.objects.filter(username=attrs['username']).first()
        if not user:
            raise serializers.ValidationError({
                'username': ErrorDetail("User not found", code='not_found')

            })

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError({
                'password': ErrorDetail("Password is incorrect", code='incorrect')
            })

        return attrs


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizzes
        fields = ['title', 'category']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer_text']


class QuestionSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True, read_only=True)
    quiz = QuizSerializer(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'quiz', 'answer']


class UserResponseToQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponseToQuestion
        fields = ['question', 'answer']
        read_only_fields = ('user',)
