# p2app/engine/handle_continents.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# Handles the processes related to continents


import sqlite3
from p2app.events import *
from sqlite3 import Cursor


def count_rows(cursor: Cursor) ->int:
    cursor.execute('SELECT COUNT(*) FROM continent')
    return int(*cursor.fetchone())


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


def save_continent(cursor: Cursor, continent: Continent) -> ContinentSavedEvent | SaveContinentFailedEvent:
    """Saves the modified continent to the airport database.

    Args:
        cursor: a cursor object used to query the database
        continent: a namedtuple containing a continent's continent_id,
        continent_code, and name

    Returns:
        ContinentSavedEvent if saving the continent succeeded
        SaveContinentFailedEvent if saving the continent failed
    """

    continent_id = continent.continent_id
    continent_code = continent.continent_code.strip()
    name = continent.name.strip()
    parameters = []
    query = 'UPDATE continent SET '

    if continent_code == '':
        query += 'continent_code=NULL, '
    else:
        query += f'continent_code=?, '
        parameters.append(continent_code)
    if name == '':
        query += 'name=NULL '
    else:
        query += f'name=? '
        parameters.append(name)

    query += f'WHERE continent_id={continent_id}'

    try:
        cursor.execute(query, parameters)
    except sqlite3.Error:
        return SaveContinentFailedEvent('Cannot have empty fields')
    else:
        return ContinentSavedEvent(continent)


def save_new_continent(cursor: Cursor, continent: Continent) -> ContinentSavedEvent | SaveContinentFailedEvent:
    """Saves a new continent to the airport database.

    Args:
        cursor: a cursor object used to query the database
        continent: a namedtuple containing a continent's continent_id,
        continent_code, and name

    Returns:
        ContinentSavedEvent if saving the continent succeeded
        SaveContinentFailedEvent if saving the continent failed
    """

    new_id = count_rows(cursor) + 1
    continent_code = continent.continent_code.strip()
    continent_name = continent.name.strip()

    if continent_code == '':
        continent_code = None
    if continent_name == '':
        continent_name = None

    try:
        cursor.execute('INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?)', (new_id, continent_code, continent_name))
    except sqlite3.Error:
        return SaveContinentFailedEvent('Cannot have empty fields')
    else:
        return ContinentSavedEvent(Continent(new_id, continent_code, continent_name))