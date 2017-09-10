# coding=utf8
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
import datetime
from datetime import datetime, timedelta
import time

import time
# New added
from django.contrib.auth.models import Permission, User
from django.db import models
from django.utils import timezone

SECURIT_DEPOSIT_RATE = 0.1
QUESTIONER_DEDUCTION_ON_VOTE = 0.1
ADMIN_ID = 1
DEFAULT_WHOLE_TICKETS_NUM = 1000

# Create your models here.

@python_2_unicode_compatible
class Subject(models.Model):
    subject_title = models.CharField(max_length=100)
    subject_logo = models.FileField()

    def __str__(self):
        return self.subject_title

@python_2_unicode_compatible
class Question(models.Model):


    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    question_title = models.CharField(max_length=1000)
    question_description = models.CharField(max_length=10000)
    question_images = models.ImageField(upload_to='upload', blank=True, null=True)
    question_videos = models.CharField(max_length=1000, blank=True, null=True)
    choice_number = models.IntegerField(default=0)
    price_per_ticket = models.FloatField()
    # Switch Value - 1:time and ticket; 2:time; 3:ticket
    time_ticket_switch = models.IntegerField(default=1)
    whole_tickets = models.IntegerField(default=-1)
    remaining_tickets = models.IntegerField(default=0)
    tickets_sold = models.IntegerField(default=0)
    starting_time = models.DateTimeField(default=datetime.now, blank=True)
    whole_time = models.IntegerField(default=-1)
    time_out = models.BooleanField(default=False)
    ratio = models.FloatField(default=0.0)
    time_ticket_switch_title = models.CharField(max_length=30, null=True)

    def case_name(self):
        if self.time_ticket_switch == 1:
            self.time_ticket_switch_title = "有限时间*有限票数"
        elif self.time_ticket_switch == 2:
            self.time_ticket_switch_title = "有限时间*不限票数"
        elif self.time_ticket_switch == 3:
            self.time_ticket_switch_title = "有限票数*不限时间"
        self.save()

    def __str__(self):
        return self.question_title

    def payQuestionDeduction(self, tickets, current_time):

        deltaTime = current_time.replace(tzinfo=None) - self.starting_time.replace(tzinfo=None)
        if self.time_ticket_switch == 1:
            if deltaTime.total_seconds() < self.whole_time*60 and self.remaining_tickets >= tickets:
                self.remaining_tickets -= tickets
                self.tickets_sold += tickets
                moneyToTrans = QUESTIONER_DEDUCTION_ON_VOTE * self.price_per_ticket * tickets
                self.transferMoney(ADMIN_ID, moneyToTrans)
                self.save()

        elif self.time_ticket_switch == 2:
            if deltaTime.total_seconds() < self.whole_time*60:
                self.tickets_sold += tickets
                moneyToTrans = QUESTIONER_DEDUCTION_ON_VOTE * self.price_per_ticket * tickets
                self.transferMoney(ADMIN_ID, moneyToTrans)
                self.save()
        elif self.time_ticket_switch == 3:
            if self.remaining_tickets >= tickets:
                self.remaining_tickets -= tickets
                self.tickets_sold += tickets
                moneyToTrans = QUESTIONER_DEDUCTION_ON_VOTE * self.price_per_ticket * tickets
                self.transferMoney(ADMIN_ID, moneyToTrans)
                self.save()
        else:
            print("Error Switch Value")
            # Send a error message in the future
            return(False)
        return(True)

    def payQuestionDeposit(self):
        if self.time_ticket_switch == 1 or self.time_ticket_switch == 3:
            moneyToTrans = SECURIT_DEPOSIT_RATE * self.price_per_ticket * self.whole_tickets
            self.transferMoney(ADMIN_ID, moneyToTrans)
            self.save()
        elif self.time_ticket_switch == 2:

            moneyToTrans = SECURIT_DEPOSIT_RATE * self.price_per_ticket * DEFAULT_WHOLE_TICKETS_NUM
            self.transferMoney(ADMIN_ID, moneyToTrans)
            self.save()
        else:
            print("Error paying question deposit")
    """
    def timeout(self):
        self.time_out = True
        self.save()
        account_money = self.user.account_money_set.get()
        account_money.balance += 100
        account_money.save()
        votes = self.vote_set.all()
        for vote in votes:
            account_money = vote.user.account_money_set.get()
            account_money.balance +=100
            account_money.save()
    """

    def transferMoney(self, receiverId, money):
        account_money = self.user.account_money_set.get()
        account_money.balance -= money
        account_money.save()
        account_receiver = Account_money.objects.get(id=receiverId)
        account_receiver.balance += money
        account_receiver.save()

@python_2_unicode_compatible
class Answer_choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_description = models.CharField(max_length=10000)
    chosen_times = models.IntegerField(default=0)
    win = models.BooleanField(default=False)
    def __str__(self):
        return self.answer_description

class Account_money(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    balance = models.FloatField(default=0.0)
    raise_vote_income = models.FloatField(default=0.0)
    answer_vote_income = models.FloatField(default=0.0)
    red_packet_balance = models.FloatField(default=0.0)

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)
    choice = models.ForeignKey(Answer_choice, on_delete=models.DO_NOTHING)
    num_tickets = models.IntegerField(default=0)
    vote_time = models.DateTimeField(default=datetime.now, blank=True)

    def save(self, *args, **kwargs):

        ValidToContinue = False

        deltaTime = self.vote_time.replace(tzinfo=None) - self.question.starting_time.replace(tzinfo=None)
        if self.question.time_ticket_switch == 1:
            if deltaTime.total_seconds() < self.question.whole_time*60 and self.question.remaining_tickets >= self.num_tickets:
                ValidToContinue = True
        elif self.question.time_ticket_switch == 2:
            if deltaTime.total_seconds() < self.question.whole_time*60:
                ValidToContinue = True
        elif self.question.time_ticket_switch == 3:
            if self.question.remaining_tickets >= self.num_tickets:
                ValidToContinue = True
        else:
            print("Error Switch Value in Vote Class")
            # Send an error message in the future

        if ValidToContinue:
            moneyToTrans = self.question.price_per_ticket * self.num_tickets
            self.transferMoney(ADMIN_ID, moneyToTrans)
            self.choice.chosen_times += self.num_tickets
            self.choice.save()
            super(Vote, self).save(*args, **kwargs)
        return(ValidToContinue)


    def transferMoney(self, receiverId, money):
        account_money = self.user.account_money_set.get()
        account_money.balance -= money
        account_money.save()
        account_receiver = Account_money.objects.get(id=receiverId)
        account_receiver.balance += money
        account_receiver.save()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    question = models.ForeignKey(Question, on_delete=models.DO_NOTHING)

