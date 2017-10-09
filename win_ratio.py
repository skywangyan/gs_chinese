from __future__ import division
import time
import MySQLdb

Rate_raiser = 0.1
Rate_platform = 0.2
Rate_voter = 0.7

print("Running...")
while True:
    time.sleep(3)
    db = MySQLdb.connect(host='localhost',
                         user='gsdb',
                         passwd='passw0rd',
                         db='GS')

    cur = db.cursor()
    cur.execute("select id, tickets_sold, choice_number, price_per_ticket from ss_question where time_out=False")
    for row in cur.fetchall():
        qid = row[0]
        tickets_sold = row[1]
        num_choices = row[2]
        price = row[3]
        cur.execute("select id, chosen_times from ss_answer_choice where question_id=%s order by chosen_times desc", (qid,))
        choice_id = []
        chosen_time = []
        for choice in cur.fetchall():
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

        if len(win_index) > 0:
            win_money = 0
            lose_money = 0
            for item in chosen_time[:len(win_index)]:
                win_money += price * item
            for item in chosen_time[len(win_index):]:
                lose_money += price * item
            ratio_temperate = lose_money * Rate_voter / win_money
            ratio_temperate = round(ratio_temperate, 2)
            ratio_temperate = ratio_temperate + 1
            #print(ratio_temperate)
            cur.execute("update ss_question set ratio=%s where id=%s", (ratio_temperate, qid,))
            db.commit()


    db.close()
