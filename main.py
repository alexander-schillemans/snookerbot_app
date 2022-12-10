from snookerbot.api import SnookerOrgAPI
from decouple import config
import datetime

from models import Match, Event, Email
import database as db

from utils.email import send_template_email

class SnookerBot:

    def __init__(self):
        self.admin_email = config('ADMIN_EMAIL')
        self.api = None

    def start(self):
        self.api = SnookerOrgAPI(self.admin_email)
        db.connect()
    
    def shutdown(self):
        db.disconnect()

    def send_yesterday_results(self):
        template_name = 'yesterday_results.html'

        today = datetime.datetime.today().date()
        today_str = today.strftime('%Y-%m-%d')
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        yesterday_matches = db.retrieve_from_table(db.TABLE_MATCHES, where={ "end_date": "= '{0}'".format(yesterday_str)}, parse_to_object=Match)
        for match in yesterday_matches: 
            match.retrieve_players(connect_db=False)
            match.retrieve_event(connect_db=False)

        today_matches = db.retrieve_from_table(db.TABLE_MATCHES, where={ "scheduled_date": "= '{0}'".format(today_str)}, parse_to_object=Match)
        for match in today_matches: 
            match.retrieve_players(connect_db=False)
            match.retrieve_event(connect_db=False)

        # Only send the mail of there are matches to be sent
        if len(yesterday_matches) > 0 or len(today_matches) > 0:
            upcoming_events = db.retrieve_from_table(db.TABLE_EVENTS, where={ "start_date": "> '{0}'".format(today_str)}, parse_to_object=Event, order='start_date', limit=3)
            for event in upcoming_events:
                event.start_date = event.start_date.strftime('%d/%m/%Y')
                event.end_date = event.end_date.strftime('%d/%m/%Y')

            context = {}

            if(len(yesterday_matches) > 0):
                subject = 'The results are in!'
            elif(len(today_matches) > 0):
                subject = 'Ready for a day of action?'
            else:
                subject = 'Your daily Snooker dose'
            
            context['title'] = subject
            context['yesterday_matches'] = yesterday_matches
            context['today_matches'] = today_matches
            context['upcoming_events'] = upcoming_events

            emails = db.retrieve_from_table(db.TABLE_EMAILS, parse_to_object=Email)
            
            for email in emails:
                context['unsubscribe_link'] = email.get_unsubscribe_link()
                send_template_email(
                    email.email,
                    subject,
                    template_name,
                    context
                )

if __name__ == '__main__':
    bot = SnookerBot()

    bot.start()
    bot.send_yesterday_results()
    bot.shutdown()