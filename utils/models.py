import inspect

from models import Match, Player, Event
import database as db

def get_object(model, **kwargs):
    connect_db = kwargs.pop('connect_db', False)
    for key, value in kwargs.items(): kwargs[key] = '={0}'.format(value)
    
    model_obj = model()
    if connect_db: db.connect()

    if isinstance(model_obj, Player):
        table = db.TABLE_PLAYERS
    elif isinstance(model_obj, Match):
        table = db.TABLE_MATCHES
    elif isinstance(model_obj, Event):
        table = db.TABLE_EVENTS
    else:
        if connect_db: db.disconnect()
        raise ValueError('Type of object is not supported.')

    db_object = db.retrieve_from_table(table, where=kwargs, parse_to_object=model)
    if connect_db: db.disconnect()

    if len(db_object) < 1: raise ValueError("Could not retrieve any object from table '{table}' with the given kwargs".format(table=table))
    elif len(db_object) > 1: raise ValueError("Multiple objects returned in table '{table}' with the given kwargs".format(id=id, table=table))
    
    return db_object[0]