# p2app/engine/handle_continents.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# Handles the processes related to countries

import sqlite3
from p2app.events import *
from sqlite3 import Cursor


def get_country(cursor: Cursor, country_code: str, country_name: str) -> CountrySearchResultEvent | None:
    """A generator function that returns the country that corresponds to the search field.

    Args:
        cursor: a cursor object used to query the database
        country_code: the country code
        country_name: the name of the country

    Returns:
        CountrySearchResultEvent if a country is found
        No values if no country is found
    """

    query = 'SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE '
    parameters = []

    if country_code is not None:
        query += 'country_code=?'
        parameters.append(country_code)
    if country_name is not None:
        if country_code is not None:
            query += ' AND '
        query += 'name=?'
        parameters.append(country_name)

    cursor.execute(query, parameters)

    all_rows = cursor.fetchall()
    if all_rows is None:
        yield from ()
    else:
        for row in all_rows:
            yield CountrySearchResultEvent(Country(*row))