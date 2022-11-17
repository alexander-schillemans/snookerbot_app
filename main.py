from snookerbot.api import SnookerOrgAPI
from decouple import config
import datetime

from models import Match, Player, Event
import database as db

from utils.email import send_template_email
from utils.api import convert_api_object
from psycopg2 import DatabaseError
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
        subject = 'The results are in!'

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

        upcoming_events = db.retrieve_from_table(db.TABLE_EVENTS, where={ "start_date": "> '{0}'".format(today_str)}, parse_to_object=Event, order='start_date', limit=3)
        for event in upcoming_events:
            event.start_date = event.start_date.strftime('%d/%m/%Y')
            event.end_date = event.end_date.strftime('%d/%m/%Y')

        context = {}
        context['title'] = subject
        context['yesterday_matches'] = yesterday_matches
        context['today_matches'] = today_matches
        context['upcoming_events'] = upcoming_events

        send_template_email(
            self.admin_email,
            subject,
            template_name,
            context
        )

if __name__ == '__main__':
    bot = SnookerBot()

    bot.start()
    bot.send_yesterday_results()
    bot.shutdown()