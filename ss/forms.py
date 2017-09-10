from django import forms
from django.contrib.auth.models import User

from .models import Subject, Question, Answer_choice, Vote


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class QuestionForm(forms.ModelForm):
    
    class Meta:
        model = Question
        fields = ('subject', 
                'question_title', 
                'question_description', 
                'question_images',
                'question_videos',
                'price_per_ticket',
                'time_ticket_switch',
                'whole_tickets',
                'whole_time',
                )

ChoiceFormset = forms.inlineformset_factory(Question, 
                                            Answer_choice, 
                                            extra=2, 
                                            fields= ('answer_description',),
                                            can_delete=True )

class VoteForm(forms.ModelForm):

    class Meta:
        model = Vote
        fields = ('choice', 'num_tickets',)


