from __future__ import division
import time
import MySQLdb

WIN_MAX = 1.0
WIN_MIN_2 = 0.0
WIN_MIN_3 = 0.0
WIN_MIN_4 = 0.0
WIN_MIN_5 = 0.0

while True:
    time.sleep(10)
    db = MySQLdb.connect(host='localhost',
                         user='testuser',
                         passwd='test',
                         db='GI')

    cur = db.cursor()
    cur.execute("select id, whole_tickets, choice_number from ss_question where time_out=False")
    for row in cur.fetchall():
        qid = row[0]
        whole_tickets = row[1]
        num_choices = row[2]
        cur.execute("select id, chosen_times from ss_answer_choice where question_id=%s order by chosen_times desc", (qid,))
        choice_id = []
        chosen_time = []
        ratio = []
        for choice in cur.fetchall():
            choice_id.append(choice[0])
            chosen_time.append(choice[1])
            ratio.append(choice[1]/whole_tickets)
            cur.execute("update ss_answer_choice set win=False where id=%s", (choice_id[-1],))
            print("haha")
        low_vote = False
        for i in range(0, num_choices):
            if ratio[i] > 0:
                if num_choices == 2 and ratio[i] < WIN_MIN_2:
                    low_vote = True
                    cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                    db.commit()
                elif num_choices == 3 and ratio[i] < WIN_MIN_3:
                    low_vote = True
                    cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                    db.commit()
                elif num_choices == 4 and ratio[i] < WIN_MIN_4:
                    low_vote = True
                    cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                    db.commit()
                elif num_choices > 4 and ratio[i] < WIN_MIN_5:
                    low_vote = True
                    cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                    db.commit()
        if not low_vote:
            max_ticket_diff = 0
            max_ticket_id = - 1
            for i in range(0, num_choices-1):
                if ratio[i] < WIN_MAX:
                    if chosen_time[i+1] > 0:
                        rdiff = chosen_time[i]-chosen_time[i+1]
                        if max_ticket_diff < rdiff:
                            max_ticket_id = i
                            max_ticket_diff = rdiff
                            print(max_ticket_id, max_ticket_diff)
            if max_ticket_id > -1:
                for i in range(0, max_ticket_id+1):
                    if ratio[i] < WIN_MAX:
                        cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                        db.commit()
            else:
                for i in range(0, num_choices):
                    if 0 < ratio[i] < WIN_MAX:
                        cur.execute("update ss_answer_choice set win=True where id=%s", (choice_id[i],))
                        db.commit()
    db.close()
