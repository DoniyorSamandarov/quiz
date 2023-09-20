from django.urls import path, include
from .views import UserRegistrationView, AuthLoginView, QuestionListView, RandomQuestionView, \
    UserResponseToQuestionSerializerView, UserResult, AllUserResults
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
urlpatterns = [

    # API routes
    path("api/", include([
        path("auth/", include([
            path("signup/", UserRegistrationView.as_view(), name='register'),
            path("login/", AuthLoginView.as_view(), name='login')

        ])),
        path('all_questions/', QuestionListView.as_view(), name='question'),
        path('random-question/', RandomQuestionView.as_view(), name='random_question'),
        path('give-response/', UserResponseToQuestionSerializerView.as_view(), name='random_question'),
        path('my-results/', UserResult.as_view(), name='my_result'),
        path('all-results/', AllUserResults.as_view(), name='all_result')

    ]))

]
