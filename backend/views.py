from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from backend.models import AuthRefreshToken, Question, UserResponseToQuestion, Answer
from quiz.serializers import (UserCrudSerializer, AuthLoginSerializer, LoginResponseSerializer, QuestionSerializer,
                              UserResponseToQuestionSerializer)


class UserRegistrationView(generics.CreateAPIView):
    """
    Ro'yxatdan o'tish
    """
    serializer_class = UserCrudSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User()
        user.set_password(serializer.validated_data['password'])
        user.username = serializer.validated_data['username']
        user.first_name = serializer.validated_data.get('first_name')
        user.last_name = serializer.validated_data.get('last_name')
        user.email = serializer.validated_data.get('email')
        user.save()
        return Response({"status": "created", 'user': {'user_id': user.id,
                                                       'username': user.username}}, status=status.HTTP_201_CREATED)


class AuthLoginView(generics.CreateAPIView):
    """
    Kirish
    """
    serializer_class = AuthLoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        user = User.objects.filter(username=username).first()
        refresh = RefreshToken.for_user(user)
        serializer = LoginResponseSerializer(
            AuthRefreshToken(refresh=str(refresh), access=str(refresh.access_token), user=user),
            context={'request': request})
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(request_body=AuthLoginSerializer(), responses={201: LoginResponseSerializer()})
    def post(self, request, *args, **kwargs):
        return super().post(request, args, kwargs)


class BaseQuestion(generics.ListAPIView):
    queryset = None
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)


class RandomQuestionView(BaseQuestion):
    queryset = Question.objects.order_by('?')[:1]


class QuestionListView(BaseQuestion):
    queryset = Question.objects.all()


class UserResponseToQuestionSerializerView(generics.CreateAPIView):
    serializer_class = UserResponseToQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user.id
        question = serializer.validated_data['question']
        answer = serializer.validated_data['answer']
        if UserResponseToQuestion.objects.filter(user=user, question=question).exists():
            response = {"status": "you have answered this question before"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            question_title = Question.objects.get(title=question)
            answer__text = question_title.answer.get(answer_text=answer)
            if answer__text.is_right:
                UserResponseToQuestion.objects.create(
                    user_id=user,
                    question=question,
                    answer=answer,
                    is_correct=True
                )
                return Response({'status': 'true'})
            else:
                UserResponseToQuestion.objects.create(
                    user_id=user,
                    question=question,
                    answer=answer,
                    is_correct=False
                )
                return Response(
                    {'status': 'false',
                     'correct answer': Answer.objects.filter(is_right=True, question=question).values('id',
                                                                                                      'answer_text')}
                )


class UserResult(generics.GenericAPIView):
    serializer_class = None

    def get(self, request, *args, **kwargs):
        user = request.user.id
        correct_count = UserResponseToQuestion.objects.filter(user_id=user, is_correct=True).count()
        in_correct_count = UserResponseToQuestion.objects.filter(user_id=user, is_correct=False).count()
        all_response = UserResponseToQuestion.objects.filter(user_id=user).count()
        user_r = UserResponseToQuestion.objects.filter(user_id=user)
        s = []
        for j in user_r:
            question_data = {
                'quiz': {
                    'quiz_title': j.question.quiz.title,
                    'question': {
                        'question_id': j.question.id,
                        'question_title': j.question.title,
                    },
                    'answers': {
                        'your_answer': j.answer.answer_text,
                        'correct_answer': Answer.objects.filter(is_right=True, question=j.question).values(
                            'answer_text')[0]['answer_text'],
                        'response_status':
                            (j.answer.answer_text == Answer.objects.filter(is_right=True, question=j.question).values(
                                'answer_text')[0]['answer_text'])
                    },
                }
            }
            s.append(question_data)
        result = {
            'result': {
                'all question': all_response,
                'correct response count': correct_count,
                'in_correct response count': in_correct_count,
                'interest rate': f'{round((100 * correct_count / all_response), 1)} %'
            }
        }
        s.append(result)

        return Response(s)


class AllUserResults(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        s = []
        lst = UserResponseToQuestion.objects.all()
        unique_questions = set()
        for ques in lst:
            question_title = ques.question.title
            if question_title in unique_questions:
                continue
            unique_questions.add(question_title)
            response = {
                'question': ques.question.title,
                'answers': []
            }
            for i in Answer.objects.filter(question__title=question_title):
                answer_data = {
                    'answer_text': i.answer_text,
                    'user': list(
                        UserResponseToQuestion.objects.filter(
                            answer=Answer.objects.get(answer_text=i.answer_text)).values_list('user_id', flat=True))
                }
                response['answers'].append(answer_data)

            s.append(response)
        print(s)
        return Response(s)
