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
    else:
        query += 'continent_code=?'
        parameters.append('')
    query += ' AND '
    if continent_name is not None:
        query += 'name=?'
        parameters.append(continent_name)
    else:
        query += 'name=?'
        parameters.append('')

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


def save_continent(cursor: Cursor, continent: Continent, mode: str) -> ContinentSavedEvent | SaveContinentFailedEvent:
    """Saves the continent to the airport database.

    Args:
        cursor: a cursor object used to query the database
        continent: a namedtuple containing a continent's continent_id,
        continent_code, and name
        mode: either modify existing continent or add a new one

    Returns:
        ContinentSavedEvent if saving the continent succeeded
        SaveContinentFailedEvent if saving the continent failed
    """

    new_id = count_rows(cursor) + 1
    continent_id = continent.continent_id
    continent_code = continent.continent_code.strip()
    continent_name = continent.name.strip()
    parameters = (continent_code, continent_name)
    query = f'UPDATE continent SET continent_code=?, name=? WHERE continent_id={continent_id}'

    try:
        if mode == 'modify':
            cursor.execute(query, parameters)
        elif mode == 'new':
            cursor.execute('INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?)',
                (new_id, continent_code, continent_name))
    except sqlite3.Error:
        return SaveContinentFailedEvent('Error modifying specified fields')
    else:
        if mode == 'modify':
            return ContinentSavedEvent(Continent(continent_id, *parameters))
        elif mode == 'new':
            return ContinentSavedEvent(Continent(new_id, continent_code, continent_name))