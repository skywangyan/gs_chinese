from datetime import datetime, timedelta
import time
import MySQLdb

SECURITY_DEPOSIT_RATE = 0.1
QUESTIONER_DEDUCTION_ON_VOTE = 0.0
_hmin = 48
_hmax = 72
while True:
    time.sleep(60)
    now = datetime.now();
    if now.hour == 0 and now.minutes == 0:
        db = MySQLdb.connect(host='localhost',
                             user='testuser',
                             password='test',
                             db='GI')

        cur = db.cursor()
        cur.execute("select id, date_format(starting_time, '%Y-%m-%d %h:%i:%s'), whole_time, user_id, whole_tickets, price_per_ticket, tickets_sold from ss_question where time_out=True")
        for row in cur.fetchall():
            pk = row[0];
            starting_time = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            whole_time = timedelta(minutes=int(row[2]))
            hmin = timedelta(hours=_hmin)
            hmax = timedelta(hours=_hmax)
            user_id = row[3]
            whole_tickets = row[4]
            price_per_ticket = row[5]
            tickets_sold = row[6]
            time_end = now - starting_time - whole_time
            if  time_end > hmin and time_end < hmax:
                return_money = SECURITY_DEPOSIT_RATE * price_per_ticket * whole_tickets + QUESTIONER_DEDUCTION_ON_VOTE * price_per_ticket * tickets_sold 
                print(return_money)
                cur.execute("update ss_account_money set balance=balance+%s where user_id=%s", (return_money, user_id,))
                db.commit()
        db.close()

        
