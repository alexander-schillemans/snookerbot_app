from snookerbot.api import SnookerOrgAPI
from decouple import config
import datetime

from models import Match, Player, Event
import database as db

from utils.email import send_template_email
from utils.models import get_object_by_id

class SnookerBot:

    def __init__(self):
        self.admin_email = config('ADMIN_EMAIL')
        self.api = None
    
    def start(self):
        self.api = SnookerOrgAPI(self.admin_email)
        db.connect()
    
    def shutdown(self):
        db.disconnect()

    def main(self):
        pass

    def send_yesterday_results(self):
        template_name = 'yesterday_results.html'
        subject = 'The results are in!'

        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        matches = db.retrieve_from_table(db.TABLE_MATCHES, where={ "end_date": "= '{0}'".format(yesterday_str)}, parse_to_object=Match)
        for match in matches: 
            match.retrieve_players()
            match.retrieve_event()

        context = {}
        context['title'] = subject
        context['matches'] = matches

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