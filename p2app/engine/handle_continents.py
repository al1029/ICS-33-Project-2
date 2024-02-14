# p2app/engine/handle_continents.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# Handles the processes related to continents

from p2app.events import *
from sqlite3 import Cursor

def get_continent(cursor: Cursor, continent_code: str, continent_name: str) -> ContinentSearchResultEvent | None:
    """A generator function that returns every row that corresponds to the search fields.

    Args:
        cursor: a cursor object used to query the database
        continent_code: the abbreviation of the continent
        continent_name: the name of the continent
    Returns:
        The ContinentSearchResult Event if any rows were found
        No values if no rows were found
    """

    query = 'SELECT continent_id, continent_code, name FROM continent WHERE '
    parameters = []

    if continent_code is not None:
        query += 'continent_code=?'
        parameters.append(continent_code)
    if continent_name is not None:
        if continent_code is not None:
            query += ' AND '
        query += 'name=?'
        parameters.append(continent_name)

    cursor.execute(query, parameters)

    all_rows = cursor.fetchall()
    if all_rows is None:
        yield from ()
    else:
        for row in all_rows:
            yield ContinentSearchResultEvent(Continent(*row))


def load_continent_info(cursor: Cursor, continent_id: int) -> ContinentLoadedEvent:
    """Returns the continent with its information for the view.

    Args:
        cursor: a cursor object used to query the database
        continent_id: the unique id of the continent
    """

    cursor.execute(f"SELECT continent_id, continent_code, name FROM continent WHERE continent_id='{continent_id}'")
    return ContinentLoadedEvent(Continent(*cursor.fetchone()))