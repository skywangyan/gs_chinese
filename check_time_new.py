from __future__ import division
from datetime import datetime, timedelta
import time
import MySQLdb
import pytz
import math
import random

SECURITY_DEPOSIT_RATE = 0.1  # no refund on this part
QUESTIONER_DEDUCTION_ON_VOTE = 0.1
whole_tickets_we_set_for_case_two = 1000
Rate_raiser = 0.1
Rate_platform = 0.2
Rate_voter = 0.7



while True:
    time.sleep(3)
    db = MySQLdb.connect(host='localhost',
                     user='gsdb',
                     passwd='passw0rd',
                     db='GS')

    cur = db.cursor()

    cur.execute("select id, date_format(starting_time, '%Y-%m-%d %h:%i:%s'), whole_time, whole_tickets, tickets_sold, choice_number, price_per_ticket, user_id, time_ticket_switch from ss_question where time_out=False")
    tmpset = cur.fetchall()
    for index in range(len(tmpset)):
        row = tmpset[index]
        pk = row[0]
        starting_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        whole_time = timedelta(minutes=int(row[2]))
        whole_tickets = row[3]
        tickets_sold = row[4]
        num_choices = row[5]
        price_per_ticket = row[6]
        host_id = row[7]
        time_ticket_switch = row[8]
        ratio_final = 0

        if time_ticket_switch == 1:
            if ((datetime.now(pytz.utc) - starting_time.replace(tzinfo=pytz.utc)).total_seconds() > whole_time.total_seconds()) or (tickets_sold >= whole_tickets):
                cur.execute("update ss_question set time_out=True where id=%s", (pk,))
                db.commit()

                cur.execute(
                    "select id, chosen_times from ss_answer_choice where question_id=%s order by chosen_times desc",
                    (pk,))
                choice_id = []
                chosen_time = []
                choiceSet = cur.fetchall()

                for choice_index in range(len(choiceSet)):
                    choice = choiceSet[choice_index]
                    choice_id.append(choice[0])
                    chosen_time.append(choice[1])
                    cur.execute("update ss_answer_choice set win=False where id=%s", (choice_id[-1],))
                    db.commit()

                # max tickers win, if all of them are equal and positive, they all lose
                win_index = []
                lose_index = []

                if chosen_time[0] == chosen_time[-1]:
                    lose_index = choice_id
                else:
                    win_index.append(choice_id[0])
                    for i in range(1, num_choices):
                        if chosen_time[i] == chosen_time[0]:
                            win_index.append(choice_id[i])
                        else:
                            lose_index.append(choice_id[i])

                for i in win_index:
                    cur.execute("update ss_answer_choice set win=True where id=%s", (i,))
                    db.commit()

                win_money = 0
                lose_money = tickets_sold*price_per_ticket

                ratio_final = 0
                if len(win_index) > 0:
                    for item in chosen_time[:len(win_index)]:
                        win_money += price_per_ticket * item
                        lose_money -= price_per_ticket * item
                    ratio_final = lose_money * Rate_voter / win_money
                    ratio_final = round(ratio_final, 2)
                    ratio_final = ratio_final + 1
                cur.execute("update ss_question set ratio=%s where id=%s", (ratio_final, pk))
                db.commit()

                host_raising_return = lose_money * Rate_raiser
                host_return = host_raising_return + QUESTIONER_DEDUCTION_ON_VOTE*tickets_sold*price_per_ticket + SECURITY_DEPOSIT_RATE*whole_tickets*price_per_ticket

                cur.execute("update ss_account_money set balance = balance + %s where user_id = %s",
                            (host_return, host_id,))
                cur.execute("update ss_account_money set raise_vote_income = raise_vote_income + %s where user_id = %s",
                            (host_raising_return, host_id,))
                cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (host_return, 1,))
                db.commit()

                if len(win_index) > 0:
                    win_index_string = '('
                    for win_i in win_index:
                        win_index_string+=str(win_i)
                        win_index_string+=','
                    win_index_string = win_index_string[:-1]+')'


                    sql = "select num_tickets, user_id" + (" from ss_vote where choice_id in (%s)" % win_index_string)
                    cur.execute(sql)
                    winners = cur.fetchall()
                    for winners_info in winners:
                        winner_id = winners_info[1]
                        winner_tickets = winners_info[0]
                        winner_return = winner_tickets*price_per_ticket*(ratio_final)
                        winner_answering_return = winner_tickets*price_per_ticket*(ratio_final-1)
                        cur.execute("update ss_account_money set balance = balance + %s where user_id = %s",
                                    (winner_return, winner_id,))
                        cur.execute(
                            "update ss_account_money set answer_vote_income = answer_vote_income + %s where user_id = %s",
                            (winner_answering_return, winner_id,))
                        cur.execute("update ss_account_money set balance = balance - %s where user_id = %s",
                                    (winner_return, 1,))

                        db.commit()

        elif time_ticket_switch == 2:
            if ((datetime.now(pytz.utc) - starting_time.replace(tzinfo=pytz.utc)).total_seconds() > whole_time.total_seconds()):
                cur.execute("update ss_question set time_out=True where id=%s", (pk,))
                db.commit()

                cur.execute(
                    "select id, chosen_times from ss_answer_choice where question_id=%s order by chosen_times desc",
                    (pk,))
                choice_id = []
                chosen_time = []
                choiceSet = cur.fetchall()

                for choice_index in range(len(choiceSet)):
                    choice = choiceSet[choice_index]
                    choice_id.append(choice[0])
                    chosen_time.append(choice[1])
                    cur.execute("update ss_answer_choice set win=False where id=%s", (choice_id[-1],))
                    db.commit()

                win_index = []
                lose_index = []

                if chosen_time[0] == chosen_time[-1]:
                    lose_index = choice_id
                else:
                    win_index.append(choice_id[0])
                    for i in range(1, num_choices):
                        if chosen_time[i] == chosen_time[0]:
                            win_index.append(choice_id[i])
                        else:
                            lose_index.append(choice_id[i])

                for i in win_index:
                    cur.execute("update ss_answer_choice set win=True where id=%s", (i,))
                    db.commit()

                win_money = 0
                lose_money = tickets_sold * price_per_ticket
                ratio_final = 0
                if len(win_index) > 0:
                    for item in chosen_time[:len(win_index)]:
                        win_money += price_per_ticket * item
                        lose_money -= price_per_ticket * item
                    ratio_final = lose_money * Rate_voter / win_money
                    ratio_final = ratio_final + 1
                cur.execute("update ss_question set ratio=%s where id=%s", (ratio_final, pk))
                db.commit()

                host_raising_return = lose_money * Rate_raiser
                host_return = host_raising_return + QUESTIONER_DEDUCTION_ON_VOTE * tickets_sold * price_per_ticket + SECURITY_DEPOSIT_RATE * whole_tickets_we_set_for_case_two * price_per_ticket

                cur.execute("update ss_account_money set balance = balance + %s where user_id = %s",
                            (host_return, host_id,))
                cur.execute("update ss_account_money set raise_vote_income = raise_vote_income + %s where user_id = %s",
                            (host_raising_return, host_id,))
                cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (host_return, 1,))
                db.commit()

                if len(win_index) > 0:
                    win_index_string = '('
                    for win_i in win_index:
                        win_index_string += str(win_i)
                        win_index_string += ','
                    win_index_string = win_index_string[:-1] + ')'

                    sql = "select num_tickets, user_id" + (" from ss_vote where choice_id in (%s)" % win_index_string)
                    cur.execute(sql)
                    winners = cur.fetchall()

                    for winners_info in winners:
                        winner_id = winners_info[1]
                        winner_tickets = winners_info[0]
                        winner_return = winner_tickets * price_per_ticket * (ratio_final)
                        winner_answering_return = winner_tickets * price_per_ticket * (ratio_final - 1)
                        cur.execute("update ss_account_money set balance = balance + %s where user_id = %s",
                                    (winner_return, winner_id,))
                        cur.execute(
                            "update ss_account_money set answer_vote_income = answer_vote_income + %s where user_id = %s",
                            (winner_answering_return, winner_id,))
                        cur.execute("update ss_account_money set balance = balance - %s where user_id = %s",
                                    (winner_return, 1,))

                        db.commit()

        elif time_ticket_switch == 3:
            if tickets_sold >= whole_tickets:
                cur.execute("update ss_question set time_out=True where id=%s", (pk,))
                db.commit()

                cur.execute(
                    "select id, chosen_times from ss_answer_choice where question_id=%s order by chosen_times desc",
                    (pk,))
                choice_id = []
                chosen_time = []
                choiceSet = cur.fetchall()

                for choice_index in range(len(choiceSet)):
                    choice = choiceSet[choice_index]
                    choice_id.append(choice[0])
                    chosen_time.append(choice[1])
                    cur.execute("update ss_answer_choice set win=False where id=%s", (choice_id[-1],))
                    db.commit()

                win_index = []
                lose_index = []

                if chosen_time[0] == chosen_time[-1]:
                    lose_index = choice_id
                else:
                    win_index.append(choice_id[0])
                    for i in range(1, num_choices):
                        if chosen_time[i] == chosen_time[0]:
                            win_index.append(choice_id[i])
                        else:
                            lose_index.append(choice_id[i])

                for i in win_index:
                    cur.execute("update ss_answer_choice set win=True where id=%s", (i,))
                    db.commit()

                win_money = 0
                lose_money = tickets_sold * price_per_ticket
                ratio_final = 0
                if len(win_index) > 0:
                    for item in chosen_time[:len(win_index)]:
                        win_money += price_per_ticket * item
                        lose_money -= price_per_ticket * item
                    ratio_final = lose_money * Rate_voter / win_money
                    ratio_final = ratio_final + 1
                cur.execute("update ss_question set ratio=%s where id=%s", (ratio_final, pk))
                db.commit()

                host_raising_return = lose_money * Rate_raiser
                host_return = host_raising_return + QUESTIONER_DEDUCTION_ON_VOTE * tickets_sold * price_per_ticket + SECURITY_DEPOSIT_RATE*whole_tickets*price_per_ticket

                cur.execute("update ss_account_money set balance = balance + %s where user_id = %s",
                            (host_return, host_id,))
                cur.execute("update ss_account_money set raise_vote_income = raise_vote_income + %s where user_id = %s",
                            (host_raising_return, host_id,))
                cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (host_return, 1,))
                db.commit()

                if len(win_index) > 0:
                    win_index_string = '('
                    for win_i in win_index:
                        win_index_string += str(win_i)
                        win_index_string += ','
                    win_index_string = win_index_string[:-1] + ')'

                    sql = "select num_tickets, user_id" + (" from ss_vote where choice_id in (%s)" % win_index_string)
                    cur.execute(sql)
                    winners = cur.fetchall()

                    for winners_info in winners:
                        winner_id = winners_info[1]
                        winner_tickets = winners_info[0]
                        winner_return = winner_tickets * price_per_ticket * (ratio_final)
                        winner_answering_return = winner_tickets * price_per_ticket * (ratio_final - 1)
                        cur.execute("update ss_account_money set balance = balance + %s where user_id = %s",
                                    (winner_return, winner_id,))
                        cur.execute(
                            "update ss_account_money set answer_vote_income = answer_vote_income + %s where user_id = %s",
                            (winner_answering_return, winner_id,))
                        cur.execute("update ss_account_money set balance = balance - %s where user_id = %s",
                                    (winner_return, 1,))

                        db.commit()

    db.close()
