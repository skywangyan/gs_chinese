# coding=utf8
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from .forms import UserForm, QuestionForm, ChoiceFormset, VoteForm
from .models import Subject, Question, Answer_choice, Account_money, Vote
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import timezone
from datetime import datetime


BREAKER_RETURN = 0.6
ADJUST_RETURN = 0.8
PLAYER_DEDUCTION_RATE = 0.1
QUESTIONER_DEDUCTION_RATE = 0.4
QUESTIONER_DEDUCTION_RETURN_TIME = 24*60*60*1000



def index(request):
        subject_by_user = Subject.objects.all()
        return render(request, 'ss/index.html', {'subject_by_user': subject_by_user})

def g_s_ratio(request, pk):
    question=Question.objects.get(pk=pk)
    print(pk, ":", question.ratio)
    return HttpResponse(question.ratio)

def g_s_answer(request):
    # if request.user.is_active:
    if request.method == 'POST':
        form = VoteForm(request.POST)
        pk=request.POST['question']
        question = Question.objects.get(pk=pk)
        if form.is_valid():
            vote=form.save(commit=False)
            vote.user = request.user
            vote.question = question
            vote.save()
            question.payQuestionDeduction(vote.num_tickets, datetime.now())
        return redirect('/global_intelligence/g_s/answer/')

    question_list_working = Question.objects.all()

    refine_search = 0
    refine_filter = 0
    refine_result = 0

    if request.method == "GET":
        query_search = request.GET.get("q")
        query_subject_living = request.GET.get(u'生活')
        query_subject_working = request.GET.get(u'工作')
        query_subject_society = request.GET.get(u'社会')
        query_money_0 = request.GET.get("q_money_0")
        query_money_1 = request.GET.get("q_money_1")
        query_money_2 = request.GET.get("q_money_2")
        query_money_3 = request.GET.get("q_money_3")
        query_money_4 = request.GET.get("q_money_4")

        question_ids_working = []

        if query_search:
            refine_search = 1
            question_list_working = question_list_working.filter(
                Q(question_title__icontains=query_search) |
                Q(question_description__icontains=query_search)
            ).distinct()

        for question in question_list_working:
            if query_subject_living is not None:
                refine_filter = 1
                if question.subject.subject_title == query_subject_living:
                    question_ids_working.append(question.id)

            if query_subject_working is not None:
                refine_filter = 1
                if question.subject.subject_title == query_subject_working:
                    question_ids_working.append(question.id)

            if query_subject_society is not None:
                refine_filter = 1
                if question.subject.subject_title == query_subject_society:
                    question_ids_working.append(question.id)

            if query_money_0 is not None:
                refine_filter = 1
                if question.price_per_ticket == 0.0:
                    question_ids_working.append(question.id)

            if query_money_1 is not None:
                refine_filter = 1
                if question.price_per_ticket > 0.0 and question.price_per_ticket <= 1.0:
                    question_ids_working.append(question.id)

            if query_money_2 is not None:
                refine_filter = 1

                if question.price_per_ticket > 1.0 and question.price_per_ticket <= 10.0:
                   question_ids_working.append(question.id)

            if query_money_3 is not None:
                refine_filter = 1
                if question.price_per_ticket > 10.0 and question.price_per_ticket <= 100.0:
                   question_ids_working.append(question.id)

            if query_money_4 is not None:
                refine_filter = 1
               if question.price_per_ticket > 100.0 and question.price_per_ticket <= 1000.0:
                   question_ids_working.append(question.id)

        if len(question_ids_working) > 0:
            refine_result = 1
            question_list = question_list_working.filter(pk__in=question_ids_working).order_by('-tickets_sold')

        else:
            if refine_search == 1 and refine_filter == 0:
                if len(question_list_working) > 0:
                    refine_result = 1
                    question_list = question_list_working.order_by('-tickets_sold')
                else:
                    question_list = Question.objects.all().order_by('-tickets_sold')

            if refine_search == 1 and refine_filter == 1:
                    question_list = Question.objects.all().order_by('-tickets_sold')

            if refine_search == 0 and refine_filter == 0:
                    question_list = Question.objects.all().order_by('-tickets_sold')

            if refine_search == 0 and refine_filter == 1:
                    question_list = Question.objects.all().order_by('-tickets_sold')


    refine_action = refine_search or refine_filter
    form = VoteForm()

    if not request.user.is_active:
        context = {
            'refine_action': refine_action,
            'refine_result': refine_result,
            'question_list': question_list[:15],
            'subject_list': Subject.objects.all(),
            'form': form,
        }

        return render(request, 'ss/g_s_answer.html', context)
    else:
        user_voted={}
        for question in question_list[:30]:
            my_answer_votes = Vote.objects.all().filter(user=request.user, question=question)
            tickets=0
            for answer in my_answer_votes:
                tickets += answer.num_tickets
            user_voted[question.pk]=tickets

        context = {
            'refine_action': refine_action,
            'refine_result': refine_result,
            'question_list': question_list[:30],
            'user_voted': user_voted,
            'subject_list': Subject.objects.all(),
            'form': form,
        }

        return render(request, 'ss/g_s_answer.html', context)

def g_s_ask(request):
    if request.user.is_active:
        if request.method == 'POST':
            form = QuestionForm(request.POST, request.FILES)
            formset = ChoiceFormset(request.POST)
            if form.is_valid() and formset.is_valid():
                question=form.save(commit=False)
                question.user = request.user
                question.remaining_tickets = question.whole_tickets
                question.tickets_sold = 0
                question.choice_number = formset.total_form_count()
                question.case_name()
                question.payQuestionDeposit()
                choices=formset.save(commit=False)

                for obj in formset.deleted_objects:
                    obj.delete()
                for choice in choices:
                    choice.question = question
                    choice.chosen_times = 0
                    choice.save()
                return redirect('/global_intelligence/g_s/answer')
        else:
            form = QuestionForm()
            formset = ChoiceFormset()
        return render(request, 'ss/g_s_ask.html', {'form': form, 'formset': formset})

    else:
        return render(request, 'ss/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                account_money = Account_money()

                account_money.user = user
                account_money.answer_vote_income = 0
                account_money.raise_vote_income = 0
                account_money.red_packet_balance = 0
                account_money.balance = 0
                account_money.save()
                login(request, user)
                subject_by_user = Subject.objects.all()
                return render(request, 'ss/index.html', {'subject_by_user': subject_by_user})
    context = {
        "form": form,
    }
    return render(request, 'ss/register.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                subject_by_user = Subject.objects.all()
                return render(request, 'ss/index.html', {'subject_by_user': subject_by_user})
            else:
                return render(request, 'ss/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'ss/login.html', {'error_message': 'Invalid login'})
    return render(request, 'ss/login.html')


def logout_user(request):
    logout(request)
    subject_by_user = Subject.objects.all()
    return render(request, 'ss/index.html', {'subject_by_user': subject_by_user})


def g_s_account(request):
    if request.user.is_active:
        account = Account_money.objects.get(user=request.user)
        balance = account.balance
        raise_vote_income = account.raise_vote_income
        answer_vote_income = account.answer_vote_income
        red_packet_balance = account.red_packet_balance
        context = {
            'balance': balance,
            'raise_vote_income': raise_vote_income,
            'answer_vote_income': answer_vote_income,
            'red_packet_balance': red_packet_balance,
        }
    return render(request, 'ss/account.html', context)


def g_s_my_vote(request):
    if request.user.is_active:
        my_answer_votes = Vote.objects.all().filter(user=request.user).order_by('-question')
        my_raise_votes = Question.objects.all().filter(user=request.user)
        context = {
            'my_answer_votes': my_answer_votes,
            'my_raise_votes': my_raise_votes,
        }
    return render(request, 'ss/my_vote.html', context)


# def g_s_history(request):
#     if request.user.is_active:
#         my_answer_votes = Vote.objects.all().filter(user=request.user)
#         my_raise_votes = Question.objects.all().filter(user=request.user)
#         context = {
#             'my_answer_votes': my_answer_votes,
#             'my_raise_votes': my_raise_votes,
#         }
#     return render(request, 'ss/history.html', context)
