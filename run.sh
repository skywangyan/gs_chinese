#!/bin/sh
python3 manage.py runserver 0:80 &
python3 win_ratio.py &
python3 check_time_new.py &
