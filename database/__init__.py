from decouple import config
import psycopg2
import datetime
import sys

from models import Player, Match, Event

db_conn = None
TABLE_PLAYERS = 'players'
TABLE_MATCHES = 'matches'
TABLE_EVENTS = 'events'
TABLE_EMAILS = 'emails'

def connect():
    """ Connect to the PostgreSQL database server """

    global db_conn

    DB_HOST = config('DB_HOST')
    DB_NAME = config('DB_NAME')
    DB_USER = config('DB_USER')
    DB_PASSWD = config('DB_PASSWD')

    try:
        db_conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWD
        )
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    return db_conn

def disconnect():
    """ Disconnects the PostgreSQL database server """
    
    global db_conn
    db_conn.close()
    db_conn = None

def format_value(value):
    """ Formats a given value to one that can be passed into an SQL query. """
    if value is None: return value

    if type(value) == str: 
        value = value.replace("'", "''") # Escape the ' character
        value = "'{value}'".format(value=value)

    if type(value) == datetime.datetime: 
        value = "'{value}'".format(value=value.strftime('%Y-%m-%d %H:%M:%S'))

    if type(value) == datetime.date: 
        value = "'{value}'".format(value=value.strftime('%Y-%m-%d'))

    return str(value)

def retrieve_from_table(table, where=None, parse_to_object=None, fields=None, order=None, limit=None):
    """ 
        Retrieves data from a specific table and parses all the rows to the given object.
        If no object is given, no parsing is done and a list of tuples is returned.

        where = {
            'id' : '=1',
            'event_id' : 'IN (1,2,3)',
            'first_name' : '<>Mark',
            ...
        }
    """

    global db_conn
    if db_conn is None: raise ValueError('Database connection has not been established.')

    fields = ['*'] if fields is None else fields
    order = 'id' if order is None else order

    select_query = 'SELECT {fields} FROM {table}'.format(
        fields=",".join(fields),
        table=table
    )

    if where:
        if(type(where) != dict): raise ValueError('Where must be a dictionary')
        where_clause = []
        for key, value in where.items():
            if value is not None:
                where_clause.append('{0} {1}'.format(key, value))

        if len(where_clause) > 0:
            select_query = '{query} WHERE {where}'.format(
                query=select_query,
                where=" AND ".join(where_clause)
            )
    
    select_query = '{query} ORDER BY {order}'.format(
        query=select_query,
        order=order
    )

    if limit:
        select_query = '{query} LIMIT {limit}'.format(
            query=select_query,
            limit=limit
        )

    try:
        cur = db_conn.cursor()
        cur.execute(select_query)
        column_names = [desc[0] for desc in cur.description]
        data = cur.fetchall()

        if parse_to_object:
            data_objects = []
            for row in data:
                obj = parse_to_object()

                index = 0
                for value in row:
                    setattr(obj, column_names[index], value)
                    index += 1
                
                data_objects.append(obj)
            data = data_objects
        
        return data

    except (psycopg2.DatabaseError) as error:
        raise psycopg2.DatabaseError('Error has occured: {0}'.format(error))

def insert_into_table(table, object):
    """ Pushes an object to the specified table, creates a new row. """
    global db_conn

    cur = db_conn.cursor()

    try:
        query_get_column_names = 'SELECT * FROM {table} LIMIT 0'.format(table=table)
        cur.execute(query_get_column_names)
        column_names = [desc[0] for desc in cur.description]
        used_column_names = []
    except (psycopg2.DatabaseError) as error:
        raise psycopg2.DatabaseError('Error has occured: {0}'.format(error))

    insert_values = []
    for column_name in column_names:
        value = getattr(object, column_name, None)
        if value is not None:
            value = format_value(value)
            insert_values.append(value)
            
            if column_name not in used_column_names: 
                used_column_names.append(column_name)

    if len(used_column_names) > 0:

        try:
            insert_query = 'INSERT INTO {table}({columns}) VALUES({values}) RETURNING id'.format(
                table=table,
                columns=", ".join(used_column_names),
                values=", ".join(insert_values)
            )

            cur.execute(insert_query)
            returned_id = cur.fetchone()[0]
            object.id = returned_id

            db_conn.commit()
            return object
        except (psycopg2.DatabaseError) as error:
            raise psycopg2.DatabaseError('Error has occured: {0}'.format(error))

    else:
        raise ValueError('Object attributes does not match any of the columns in table "{table}"'.format(table=table))

def delete_from_table(table, object=None, id=None):
    """ 
        Deletes a row from a table. 
        If given an object, the id attribute on the object is used to determine the row.
        If given an id, the row id is used.
    """
    global db_conn

    if (object is None) and (id is None): raise ValueError('Object or id is not provided. Choose one.')
    if object and id: raise ValueError('Only object OR id can be provided, not both. Choose one.')

    if object:
        id = getattr(object, 'id', None)
        if not id: raise ValueError("Can't find attribute 'id' on object.")

    cur = db_conn.cursor()

    try:
        delete_query = 'DELETE FROM {table} WHERE id = {id}'.format(table=table, id=id)
        cur.execute(delete_query)
        rows_deleted = cur.rowcount
        db_conn.commit()
        return rows_deleted
    except (psycopg2.DatabaseError) as error:
        raise psycopg2.DatabaseError('Error has occured: {0}'.format(error))

def update_all_rows_in_table(table, fields):
    """
        Updates all rows in a table.
        Fields is a dict with the key being the column name and the value that has to be set on all rows.
    """

    global db_con

    cur = db_conn.cursor()

    update_fields = []
    for field, value in fields.items():
        value = format_value(value)
        update_fields.append('{field} = {value}'.format(field=field, value=value))

    try:
        update_query = "UPDATE {table} SET {update_fields}".format(
            table=table,
            update_fields=", ".join(update_fields),
        )

        cur.execute(update_query)
        rows_updated = cur.rowcount
        db_conn.commit()
        return rows_updated
    except (psycopg2.DatabaseError) as error:
        raise psycopg2.DatabaseError('Error has occured: {0}'.format(error))

def update_row_in_table(table, object, id=None):
    """
        Updates a row in a table.
        Only updates the fields if the value has changed.
        The id attribute on the object is used to determine the row. Optionally, you can pass an id yourself.
    """
    global db_conn

    if isinstance(object, Player):
        model = Player
    elif isinstance(object, Match):
        model = Match
    elif isinstance(object, Event):
        model = Event
    else:
        raise ValueError('Type of object not supported.')

    if id: object.id = id
    if not object.id: raise ValueError("Can't fetch an object with no id.")

    # Retrieve the current object from the database
    query = retrieve_from_table(table, where={'id' : '={0}'.format(object.id)}, parse_to_object=model)
    if len(query) < 1: raise ValueError("Object with id '{id}' does not exist in table '{table}'".format(id=object.id, table=table))
    elif len(query) > 1: raise ValueError("Multiple objects returned for id '{id}' in table '{table}'".format(id=id, table=table))
    db_object = query[0]

    # Get the changed fields
    compare_fields = (db_object.__dict__.items() ^ object.__dict__.items())
    changed_fields = list(dict.fromkeys([field[0] for field in compare_fields])) # list(dict.fromkeys(...)) --> Removes all the duplicate fields

    update_fields = []
    for field in changed_fields:
        value = getattr(object, field, None)
        if value is not None:
            value = format_value(value)
            update_fields.append('{field} = {value}'.format(field=field, value=value))

    if len(update_fields) > 0:
        # Only hit the db if we have to update any fields
        # Construct the query and execute
        cur = db_conn.cursor()
        try:
            update_query = "UPDATE {table} SET {update_fields} WHERE id = {id}".format(
                table=table,
                update_fields=", ".join(update_fields),
                id=object.id
            )

            cur.execute(update_query)
            rows_updated = cur.rowcount
            db_conn.commit()
            return rows_updated
        except (psycopg2.DatabaseError) as error:
            raise psycopg2.DatabaseError('Error has occured: {0}'.format(error))
    else:
        # 0 rows updated, so we return 0
        return 0

def create_or_update(table, object):

    try:
        update_row_in_table(table, object)
    except (psycopg2.DatabaseError, ValueError):
        insert_into_table(table, object)