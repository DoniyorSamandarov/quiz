from django.contrib.auth.models import User
from django.db import models


class DateCreatedUpdatedMixin(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_updated = models.DateTimeField(verbose_name="Last Updated", auto_now=True)

    class Meta:
        abstract = True


class QuestionDegree(models.TextChoices):
    FUNDAMENTAL = "FUNDAMENTAL", 'Fundamental'
    BEGINNER = "BEGINNER", 'Beginner',
    INTERMEDIATE = "INTERMEDIATE", 'Intermediate'
    ADVANCED = "ADVANCED", 'Advanced'
    EXPERT = "EXPERT", 'Expert'


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Quizzes(DateCreatedUpdatedMixin, models.Model):
    title = models.CharField(max_length=255, verbose_name="Quiz Title")
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"


class Question(DateCreatedUpdatedMixin, models.Model):
    quiz = models.ForeignKey(Quizzes, related_name='question', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=255, verbose_name="question title")
    difficulty = models.CharField(choices=QuestionDegree.choices,max_length=255, verbose_name="Difficulty",
                                  default=QuestionDegree.BEGINNER)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title


class Answer(DateCreatedUpdatedMixin, models.Model):
    question = models.ForeignKey(Question, related_name='answer', on_delete=models.DO_NOTHING)
    answer_text = models.CharField(max_length=255, verbose_name="Answer Text")
    is_right = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.answer_text


class UserResponseToQuestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Question')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Answer')
    is_correct = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'User response to question'
        verbose_name_plural = 'User responses to questions'


class AuthRefreshToken:
    def __init__(self, refresh, access, user):
        self.refresh = refresh
        self.access = access
        self.user = user
