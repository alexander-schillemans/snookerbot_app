class Player:

    def __init__(self,
        id=None,
        api_id=None,
        first_name=None,
        last_name=None,
        nationality=None,
        sex=None,
        photo_url=None,
        first_season_as_pro=None,
        last_season_as_pro=None,
        amount_of_ranking_titles=None,
        amount_of_maximums=None
    ):
        self.id = id
        self.api_id = api_id
        self.first_name = first_name
        self.last_name = last_name
        self.nationality = nationality
        self.sex = sex
        self.photo_url = photo_url
        self.first_season_as_pro = first_season_as_pro
        self.last_season_as_pro = last_season_as_pro
        self.amount_of_ranking_titles = amount_of_ranking_titles
        self.amount_of_maximums = amount_of_maximums

class Match:

    def __init__(self,
        id=None,
        api_id=None,
        event=None,
        event_id=None,
        round=None,
        number=None,
        player1_id=None,
        player1=None,
        score1=None,
        player2_id=None,
        player2=None,
        score2=None,
        winner_id=None,
        winner=None,
        unfinished=None,
        start_date=None,
        end_date=None,
        scheduled_date=None,
        was_in_last_sync=None
    ):
        self.id = id
        self.api_id = api_id
        self.event = event
        self.event_id = event_id
        self.round = round
        self.number = number
        self.player1_id = player1_id
        self.player1 = player1
        self.player2_id = player2_id
        self.score1 = score1
        self.player2 = player2
        self.score2 = score2
        self.winner_id = winner_id
        self.winner = winner
        self.unfinished = unfinished if unfinished else False
        self.start_date = start_date
        self.end_date = end_date
        self.scheduled_date = scheduled_date
        self.was_in_last_sync = was_in_last_sync if was_in_last_sync else False

    def retrieve_players(self, connect_db=True):
        from utils.models import get_object
        if self.player1_id: self.player1 = get_object(Player, connect_db=connect_db, api_id=self.player1_id)
        if self.player2_id: self.player2 = get_object(Player, connect_db=connect_db, api_id=self.player2_id)
        if self.winner_id: self.winner = get_object(Player, connect_db=connect_db, api_id=self.winner_id)
    
    def retrieve_event(self, connect_db=True):
        from utils.models import get_object
        if self.event_id: self.event = get_object(Event, connect_db=connect_db, api_id=self.event_id)

class Event:

    def __init__(self,
        id=None,
        api_id=None,
        name=None,
        start_date=None,
        end_date=None,
        sponsor=None,
        season=None,
        type=None,
        venue=None,
        city=None,
        country=None,
        all_rounds_added=None,
        amount_of_competitors=None,
        amount_of_upcoming_matches=None,
        amount_of_active_matches=None,
        amount_of_finished_matches=None,
        defending_champion=None
    ):
        self.id = id
        self.api_id = api_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.sponsor = sponsor
        self.season = season
        self.type = type
        self.venue = venue
        self.city = city
        self.country = country
        self.all_rounds_added = all_rounds_added
        self.amount_of_competitors = amount_of_competitors
        self.amount_of_upcoming_matches = amount_of_upcoming_matches
        self.amount_of_active_matches = amount_of_active_matches
        self.amount_of_finished_matches = amount_of_finished_matches
        self.defending_champion = defending_champion

class Email:

    def __init__(self,
        id=None,
        email=None,
        unsubscribe_token=None
    ):

        self.id = id
        self.email = email
        self.unsubscribe_token = unsubscribe_token

    def get_unsubscribe_link(self):
        from decouple import config
        unsubscribe_link = '{0}/unsubscribe?&email={1}&token={2}'.format(
            config('WEBSITE_URL'),
            self.email,
            self.unsubscribe_token
        )
        return unsubscribe_link