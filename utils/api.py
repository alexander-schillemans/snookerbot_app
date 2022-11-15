from snookerbot.models.players import Player as APIPlayer
from snookerbot.models.matches import Match as APIMatch
from snookerbot.models.events import Event as APIEvent

from models import Player, Match, Event

PLAYER_MAPPINGS = {
    'ID' : 'api_id',
    'FirstName' : 'first_name',
    'LastName' : 'last_name',
    'Nationality' : 'nationality',
    'Sex' : 'sex',
    'Photo' : 'photo_url',
    'FirstSeasonAsPro' : 'first_season_as_pro',
    'LastSeasonAsPro' : 'last_season_as_pro',
    'NumRankingTitles' : 'amount_of_ranking_titles',
    'NumMaximums' : 'amount_of_maximums'
}

MATCH_MAPPINGS = {
    'ID' : 'api_id',
    'EventID' : 'event_id',
    'Round' : 'round',
    'Number' : 'number',
    'Player1ID' : 'player1_id',
    'Score1' : 'score1',
    'Player2ID' : 'player2_id',
    'Score2' : 'score2',
    'WinnerID' : 'winner_id',
    'Unfinished' : 'unfinished',
    'StartDate' : 'start_date',
    'EndDate' : 'end_date',
    'ScheduledDate' : 'scheduled_date'
}

EVENT_MAPPINGS = {
    'ID' : 'api_id',
    'Name' : 'name',
    'StartDate' : 'start_date',
    'EndDate' : 'end_date',
    'Sponsor' : 'sponsor',
    'Season' : 'season',
    'Type' : 'type',
    'Venue' : 'venue',
    'City' : 'city',
    'Country' : 'country',
    'AllRoundsAdded' : 'all_rounds_added',
    'NumCompetitors' : 'amount_of_competitors',
    'NumUpcoming' : 'amount_of_upcoming_matches',
    'NumActive' : 'amount_of_active_matches',
    'NumResults' : 'amount_of_finished_matches',
    'DefendingChampion' : 'defending_champion'
}

def convert_api_object(api_object):
    if isinstance(api_object, APIPlayer):
        mappings = PLAYER_MAPPINGS
        obj = Player()
    elif isinstance(api_object, APIMatch):
        mappings = MATCH_MAPPINGS
        obj = Match()
    elif isinstance(api_object, APIEvent):
        mappings = EVENT_MAPPINGS
        obj = Event()
    else:
        raise ValueError('Type of object not supported.')

    for api_key, obj_key in mappings.items():
        api_value = getattr(api_object, api_key, None)
        if api_value:
            setattr(obj, obj_key, api_value)
    
    return obj