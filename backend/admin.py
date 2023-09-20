from django.contrib import admin
from .models import Category, Answer, Question, UserResponseToQuestion, Quizzes


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = ['name']


class AnswerInlineModel(admin.TabularInline):
    model = Answer
    fields = ['answer_text', 'is_right']


@admin.register(Question)
class AdminQuestion(admin.ModelAdmin):
    fields = ['title', 'difficulty', 'quiz']
    list_display = ['title', 'date_updated']
    inlines = [AnswerInlineModel]


@admin.register(Answer)
class AdminAnswer(admin.ModelAdmin):
    list_display = (['answer_text', 'is_right', 'question'])


@admin.register(UserResponseToQuestion)
class AdminUserResponseToQuestion(admin.ModelAdmin):
    list_display = ['user', 'answer', 'question', 'is_correct']


@admin.register(Quizzes)
class AdminQuizzes(admin.ModelAdmin):
    list_display = ['title', 'category']
