from __future__ import division
from datetime import datetime, timedelta
import time
import MySQLdb
import math
import random

MAX_RETURN_RATE = 50
BETA = 0.9
SECURIT_DEPOSIT_RATE = 0.1
QUESTIONER_DEDUCTION_ON_VOTE = 0.1
TAX_PLAYER = 0.01
TAX_HOST = 0.03
WIN_MAX = 1.0
WIN_MIN_2 = 0.0
WIN_MIN_3 = 0.0
WIN_MIN_4 = 0.0
WIN_MIN_5 = 0.0

while True:
    time.sleep(2)
    db = MySQLdb.connect(host='localhost',
                     user='testuser',
                     passwd='test',
                     db='GI')

    cur = db.cursor()
    cur.execute("select id, date_format(starting_time, '%Y-%m-%d %h:%i:%s'), whole_time, whole_tickets, tickets_sold, choice_number, price_per_ticket, user_id from ss_question where time_out=False")
    for row in cur.fetchall():
        pk = row[0]
        starting_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
        whole_time = timedelta(minutes=int(row[2]))
        whole_tickets = row[3]
        tickets_sold = row[4]
        num_choices = row[5]
        price_per_ticket = row[6]
        host_id = row[7]
        print("lalalalalala")
        print(datetime.now())
        print(starting_time)
        print((datetime.now() - starting_time).total_seconds()-8*3600)
        print(whole_time.total_seconds())

        if (datetime.now() - starting_time).total_seconds() - 8*3600 > whole_time.total_seconds():
            cur.execute("update ss_question set time_out=True where id=%s", (pk,))
            db.commit()
            total_red_packet = 0.0
            cur.execute("select id, chosen_times from ss_answer_choice where question_id=%s order by chosen_times desc", (pk,))
            choice_id = []
            chosen_time = []
            ratio = []
            win_choices = []
            for choice in cur.fetchall():
                choice_id.append(choice[0])
                chosen_time.append(choice[1])
                ratio.append(choice[1]/whole_tickets)
                cur.execute("update ss_answer_choice set win=False where id=%s", (choice_id[-1],))
                print("choice id, chosentime and ratio:", choice_id[-1], chosen_time[-1], ratio[-1])
            low_vote = False
            for i in range(0, num_choices):
                if ratio[i] > 0:
                    if num_choices == 2 and ratio[i] < WIN_MIN_2:
                        low_vote = True
                        cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                        win_choices.append(choice_id[i])
                        db.commit()
                    elif num_choices == 3 and ratio[i] < WIN_MIN_3:
                        low_vote = True
                        cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                        win_choices.append(choice_id[i])
                        db.commit()
                    elif num_choices == 4 and ratio[i] < WIN_MIN_4:
                        low_vote = True
                        cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                        win_choices.append(choice_id[i])
                        db.commit()
                    elif num_choices > 4 and ratio[i] < WIN_MIN_5:
                        low_vote = True
                        cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                        win_choices.append(choice_id[i])
                        db.commit()
            print("low_vote: ", low_vote)
            print("win_choices1: ", win_choices)
            if not low_vote:
                print("haha")
                max_ticket_diff = 0
                max_ticket_id = -1
                for i in range(0, num_choices-1):
                    if ratio[i] < WIN_MAX:
                        if chosen_time[i+1] > 0:
                            rdiff = chosen_time[i]-chosen_time[i+1]
                            if max_ticket_diff < rdiff:
                                max_ticket_id = i
                                max_ticket_diff = rdiff
                if max_ticket_id > -1:
                    for i in range(0, max_ticket_id+1):
                        if ratio[i] < WIN_MAX:
                            cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                            win_choices.append(choice_id[i])
                            db.commit()
                else:
                    for i in range(0, num_choices):
                        if 0 < ratio[i] < WIN_MAX:
                            cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                            win_choices.append(choice_id[i])
                            db.commit()
            print("win_choices2: ", win_choices)
            if low_vote:
                cur.execute("select sum(chosen_times) from ss_answer_choice where win=True and question_id=%s", (pk,))
                total_win_tickets = cur.fetchall()[0][0]
                print("total_win_tickets: ", total_win_tickets)
                player_return_rate = min(BETA * (float(tickets_sold) - float(total_win_tickets)) / float(total_win_tickets), MAX_RETURN_RATE)
                print("player_return_rate: ", player_return_rate)
                host_return = max((1-BETA)*(float(tickets_sold) - float(total_win_tickets))*price_per_ticket, (float(tickets_sold) - float(total_win_tickets))* price_per_ticket - MAX_RETURN_RATE * float(total_win_tickets) * price_per_ticket)*(1-TAX_HOST)
                host_return += float(tickets_sold)*price_per_ticket*QUESTIONER_DEDUCTION_ON_VOTE + float(whole_tickets)*price_per_ticket*QUESTIONER_DEDUCTION_ON_VOTE
                print("host_return: ", host_return)

                host_raising_return = max((1-BETA)*(float(tickets_sold) - float(total_win_tickets))*price_per_ticket, (float(tickets_sold) - float(total_win_tickets))* price_per_ticket - MAX_RETURN_RATE * float(total_win_tickets) * price_per_ticket)*(1-TAX_HOST)
                print("host_raising_return: ", host_raising_return)
                cur.execute("update ss_account_money set balance = balance + %s where user_id = %s", (host_return, host_id,))
                cur.execute("update ss_account_money set raise_vote_income = raise_vote_income + %s where user_id = %s", (host_raising_return, host_id,))
                cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (host_return, 1,))

                db.commit()
                dt = timedelta(minutes=15)
                nslots = whole_time.total_seconds() // dt.total_seconds() + 1
                print("nslots: ", nslots)
                win_choices_in = ', '.join(list(map(lambda x: '%s'%x, win_choices)))
                sql="select num_tickets, user_id, date_format(vote_time, '%Y-%m-%d %h:%i:%s')"+(" from ss_vote where choice_id in (%s)"%win_choices_in)
                cur.execute(sql)
                winners = cur.fetchall()
                for winners_info in winners:
                    winner_id = winners_info[1]
                    winner_tickets = winners_info[0]
                    vote_time = datetime.strptime(winners_info[2], '%Y-%m-%d %H:%M:%S')
                    time_slot = math.floor((vote_time - starting_time).total_seconds()/dt.total_seconds())
                    print("time_slot: ", time_slot)
                    red_packet_rate = player_return_rate * (1-math.sqrt(1-0.75*time_slot**2/nslots**2))
                    total_red_packet = price_per_ticket * winner_tickets * red_packet_rate
                    player_return_rate *= math.sqrt(1-0.75*time_slot**2/nslots**2)
                    winner_return = price_per_ticket * winner_tickets * (1+player_return_rate*(1-TAX_PLAYER)) + total_red_packet
                    winner_answer_return = price_per_ticket * winner_tickets * (player_return_rate*(1-TAX_PLAYER))
                    print("winner_return: ", winner_return)
                    cur.execute("update ss_account_money set balance = balance + %s where user_id = %s", (winner_return, winner_id,))
                    cur.execute("update ss_account_money set answer_vote_income = answer_vote_income + %s where user_id = %s", (winner_answer_return, winner_id,))
                    cur.execute("update ss_account_money set red_packet_balance = red_packet_balance + %s where user_id = %s", (total_red_packet, winner_id,))
                    cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (winner_return, 1,))

                    db.commit()

            else:
                cur.execute("select sum(chosen_times), sum(chosen_times*chosen_times) from ss_answer_choice where win=True and question_id=%s", (pk,))
                total_win_tickets, total_win_tickets_sqsum = cur.fetchall()[0]
                host_return = float(tickets_sold)*price_per_ticket
                dt = timedelta(minutes=15)
                nslots = whole_time.total_seconds() // dt.total_seconds() + 1
                for choice in win_choices:
                    cur.execute("select chosen_times from ss_answer_choice where id=%s", (choice,))
                    choice_chosen_time = cur.fetchall()[0][0]
                    player_return_rate = min(BETA*float(choice_chosen_time) * (float(tickets_sold) - float(total_win_tickets))/float(total_win_tickets_sqsum) , MAX_RETURN_RATE)
                    print("player_return_rate: ", player_return_rate, float(choice_chosen_time), float(tickets_sold), float(total_win_tickets), float(total_win_tickets_sqsum))
                    sql="select num_tickets, user_id, date_format(vote_time, '%Y-%m-%d %h:%i:%s')"+" from ss_vote where choice_id=%s"%choice
                    cur.execute(sql)
                    for winners_info in cur.fetchall():
                        winner_id = winners_info[1]
                        winner_tickets = winners_info[0]
                        vote_time = datetime.strptime(winners_info[2], '%Y-%m-%d %H:%M:%S')
                        time_slot = math.floor((vote_time - starting_time).total_seconds()/dt.total_seconds())
                        print("time_slot: ", time_slot, nslots)
                        red_packet_rate = player_return_rate * (1-math.sqrt(1-0.75 * time_slot ** 2 / nslots ** 2))
                        total_red_packet += price_per_ticket * winner_tickets * red_packet_rate
                        player_return_rate *= math.sqrt(1-0.75*time_slot**2/nslots**2)
                        winner_return = price_per_ticket * winner_tickets * (1+player_return_rate*(1-TAX_PLAYER))
                        host_return -= price_per_ticket * winner_tickets * (1+player_return_rate)
                        cur.execute("update ss_account_money set balance = balance + %s where user_id = %s", (winner_return, winner_id,))

                        winner_answer_return = price_per_ticket * winner_tickets * (player_return_rate * (1 - TAX_PLAYER))

                        cur.execute("update ss_account_money set answer_vote_income = answer_vote_income + %s where user_id = %s", (winner_answer_return, winner_id,))
                        cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (winner_return, 1,))

                        db.commit()
                host_return *= (1-TAX_HOST)
                host_raising_return = host_return
                host_return += float(tickets_sold) * price_per_ticket * QUESTIONER_DEDUCTION_ON_VOTE + float(whole_tickets) * price_per_ticket * QUESTIONER_DEDUCTION_ON_VOTE
                cur.execute("update ss_account_money set raise_vote_income = raise_vote_income + %s where user_id = %s", (host_raising_return, host_id,))
                cur.execute("update ss_account_money set balance = balance + %s where user_id = %s", (host_return, host_id,))
                cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (host_return, 1,))

                db.commit()

            cur.execute("select user_id from ss_vote where question_id=%s", (pk,))
            players = cur.fetchall()
            num_players = len(players)
            random_red_packet = random.sample([1, 2, 3, 4, 5], num_players)
            total = sum(random_red_packet)
            random_red_packet = [x/total for x in random_red_packet]
            i = 0
            for user in players:
                cur.execute("update ss_account_money set red_packet_balance=red_packet_balance + %s where user_id = %s", (random_red_packet[i] * total_red_packet, user))
                cur.execute("update ss_account_money set balance = balance + %s where user_id = %s", (random_red_packet[i] * total_red_packet, user))
                cur.execute("update ss_account_money set balance = balance - %s where user_id = %s", (random_red_packet[i] * total_red_packet, 1))
                db.commit()
                i=i+1
    db.close()

