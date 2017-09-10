from django.contrib import admin
from .models import Subject, Question, Answer_choice, Account_money, Vote, Favorite

admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Answer_choice)
admin.site.register(Account_money)
admin.site.register(Vote)
admin.site.register(Favorite)
