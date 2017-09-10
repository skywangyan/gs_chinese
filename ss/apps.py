from django.apps import AppConfig


class SsConfig(AppConfig):
    name = 'ss'

    # def ready(self):
        # from datetime import datetime, timedelta
        # from .models import Question
        # while True:
            # questions = Question.objects.filter(time_out = False)
            # for question in questions:
                # now = datetime.now()
                # dt = now - question.starting_time
                # whole_time = timedelta()
                # whole_time.min = question.whole_time
                # if dt > whole_time:
                    # question.timeout()

            
