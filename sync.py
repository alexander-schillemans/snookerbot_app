import logging
from psycopg2 import DatabaseError
import datetime

from snookerbot.api import SnookerOrgAPI
from decouple import config

from models import Match, Player, Event
from utils.api import convert_api_object
import database as db

class SyncManager:

    def __init__(self):
        self.logger = None
        self.admin_email = config('ADMIN_EMAIL')
        self.api = SnookerOrgAPI(self.admin_email)

    def start_sync(self):
        self.init_logger()
        self.logger.info('Starting sync...')

        self.logger.info('Connecting to database...')
        db.connect()

        self.logger.info('--- SYNCING UPCOMING MATCHES ---')
        self.sync_upcoming_matches()
        self.logger.info('--- END SYNCING UPCOMING MATCHES ---')
        
        self.logger.info('--- SYNCING YESTERDAY MATCHES ---')
        self.sync_yesterdays_matches()
        self.logger.info('--- END YESTERDAY UPCOMING MATCHES ---')

        self.logger.info('Disconnecting database...')
        db.disconnect()

    def init_logger(self):
        logger = logging.getLogger('sync_logger')
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('./logs/sync_logger.log')
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.logger = logger

    def sync_upcoming_matches(self):
        ## Set the column for all matches 'was_in_last_sync' to False
        self.logger.info("Updating field 'was_in_last_sync' for all matches in database...")
        try:
            db.update_all_rows_in_table(db.TABLE_MATCHES, { 'was_in_last_sync' : False })
        except (DatabaseError, ValueError) as error:
            self.logger.error(error)
        
        ## Vars we need below
        player_ids = []
        event_ids = []

        ## Get all upcoming matches and create/update them in the database
        self.logger.info('Retrieving all upcoming matches from API and create or updating them in the database...')
        matches = self.api.matches.get_upcoming()
        for match in matches.items():
            match_obj = convert_api_object(match)
            match_obj.was_in_last_sync = True # Set the flag so we know this match has been updated in the last sync

            # We save the returned player IDs, so we can update their information later
            if match_obj.player1_id not in player_ids: player_ids.append(match_obj.player1_id)
            if match_obj.player2_id not in player_ids: player_ids.append(match_obj.player2_id)

            # We save the returned event IDs, so we can update their information later
            if match_obj.event_id not in event_ids: event_ids.append(match_obj.event_id)

            # Check if we have a match in the database already
            db_match = db.retrieve_from_table(db.TABLE_MATCHES, 
                where={
                    'event_id' : '={0}'.format(match_obj.event_id),
                    'round' : '={0}'.format(match_obj.round),
                    'number' : '={0}'.format(match_obj.number),
                },
                parse_to_object=Match
            )
            
            # If we found a match in the database, update the row
            # Else, create a new row
            try:
                if len(db_match) > 0:
                    db_match = db_match[0]
                    match_obj.id = db_match.id
                    db.update_row_in_table(db.TABLE_MATCHES, match_obj)
                else:
                    db.insert_into_table(db.TABLE_MATCHES, match_obj)
            except (DatabaseError, ValueError) as error:
                self.logger.error(error)

        ## Get all returned player IDs and create/update them in the database
        self.logger.info('Retrieving all returned players from API and create or updating them in the database...')
        for player_id in player_ids:
            player = self.api.players.get(player_id)
            player_obj = convert_api_object(player)
            db_player = db.retrieve_from_table(db.TABLE_PLAYERS, where={'api_id' : '={0}'.format(player_obj.api_id)}, parse_to_object=Player)

            try:
                if len(db_player) > 0:
                    db_player = db_player[0]
                    player_obj.id = db_player.id
                    db.update_row_in_table(db.TABLE_PLAYERS, player_obj)
                else:
                    db.insert_into_table(db.TABLE_PLAYERS, player_obj)
            except (DatabaseError, ValueError) as error:
                self.logger.error(error)

        ## Get all returned event IDs and create/update them in the database
        self.logger.info('Retrieving all returned events from API and create or updating them in the database...')
        for event_id in event_ids:
            event = self.api.events.get(event_id)
            event_obj = convert_api_object(event)
            db_event = db.retrieve_from_table(db.TABLE_EVENTS, where={'api_id' : '={0}'.format(event_obj.api_id)}, parse_to_object=Event)

            try:
                if len(db_event) > 0:
                    db_event = db_event[0]
                    event_obj.id = db_event.id
                    db.update_row_in_table(db.TABLE_EVENTS, event_obj)
                else:
                    db.insert_into_table(db.TABLE_EVENTS, event_obj)
            except (DatabaseError, ValueError) as error:
                self.logger.error(error)

    def sync_yesterdays_matches(self):
        today = datetime.datetime.today().date()
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime('%Y-%m-%d')

        matches = db.retrieve_from_table(db.TABLE_MATCHES, where={ "scheduled_date": "= '{0}'".format(yesterday_str)}, parse_to_object=Match)
        
        for match in matches:
            api_match = self.api.matches.get(match.event_id, match.round, match.number)
            match_obj = convert_api_object(api_match)
            match_obj.id = match.id
            db.update_row_in_table(db.TABLE_MATCHES, match_obj)
        
if __name__ == '__main__':
    manager = SyncManager()
    manager.start_sync()