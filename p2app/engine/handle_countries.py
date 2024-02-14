# p2app/engine/handle_continents.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# Handles the processes related to countries

import sqlite3
from p2app.events import *
from sqlite3 import Cursor


def find_max_id_in_col(cursor: Cursor) ->int:
    """Finds the maximum id in the country table column.

    Args:
        cursor: a cursor object used to query the database

    Returns:
        the maximum id
    """

    cursor.execute('SELECT MAX(country_id) FROM country')
    return int(cursor.fetchone()[0])


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


def load_country_info(cursor: Cursor, country_id: int) -> CountryLoadedEvent:
    """Returns the country with the info for the view.

    Args:
        cursor: a cursor object used to query the database
        country_id: the id of the country

    Returns:
        CountryLoadedEvent with the information of the country
    """

    cursor.execute(f'SELECT country_id, country_code, name, continent_id, wikipedia_link, keywords FROM country WHERE country_id={country_id}')
    return CountryLoadedEvent(Country(*cursor.fetchone()))


def save_country(cursor: Cursor, country: Country) -> CountrySavedEvent | SaveCountryFailedEvent:
    """Saves the modified country to the airport database.

    Args:
        cursor: a cursor object used to query the database
        country: a namedtuple containing information about the country

    Returns:
        CountrySavedEvent if saving the country succeeded
        SaveCountryFailedEvent if saving the country failed
    """

    country_code = country.country_code.strip()
    name = country.name.strip()
    continent_id = country.continent_id
    wikipedia_link = country.wikipedia_link if country.wikipedia_link is None else country.wikipedia_link.strip()
    keywords = country.keywords if country.keywords is None else country.keywords.strip()
    parameters = []
    query = 'UPDATE country SET '

    if country_code == '':
        query += 'country_code=NULL, '
    else:
        query += 'country_code=?, '
        parameters.append(country_code)
    if name == '':
        query += 'name=NULL, '
    else:
        query += 'name=?, '
        parameters.append(name)
    if continent_id == '':
        query += 'continent_id=NULL, '
    else:
        query += 'continent_id=?, '
        parameters.append(continent_id)
    if wikipedia_link is None:
        query += 'wikipedia_link=NULL, '
    else:
        query += 'wikipedia_link=?, '
        parameters.append(wikipedia_link)
    if keywords is None:
        query += 'keywords=NULL '
    else:
        query += 'keywords=? '
        parameters.append(keywords)

    query += f'WHERE country_id={country.country_id}'

    try:
        cursor.execute(query, parameters)
    except sqlite3.Error as e:
        return SaveCountryFailedEvent('Error adding specified fields')
    else:
        return CountrySavedEvent(Country(country.country_id, country_code, name, continent_id, wikipedia_link, keywords))


def save_new_country(cursor: Cursor, country: Country) -> CountrySavedEvent | SaveCountryFailedEvent:
    """Saves a new country to the airport database.

    Args:
        cursor: a cursor object used to query the database
        country: a namedtuple containing information about the country

    Returns:
        CountrySavedEvent if saving the country succeeded
        SaveCountryFailedEvent if saving the country failed
    """

    new_id = find_max_id_in_col(cursor) + 1
    country_code = country.country_code.strip()
    name = country.name.strip()
    continent_id = country.continent_id
    wikipedia_link = country.wikipedia_link if country.wikipedia_link is None else country.wikipedia_link.strip()
    keywords = country.keywords if country.keywords is None else country.keywords.strip()

    if country_code == '':
        country_code = None
    if name == '':
        name = None

    try:
        cursor.execute('INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords)'
                       'VALUES (?,?,?,?,?,?)', (new_id, country_code, name, continent_id, wikipedia_link, keywords))
    except sqlite3.Error as e:
        return SaveCountryFailedEvent(f'Error: {e}')
    else:
        return CountrySavedEvent(Country(new_id, country_code, name, continent_id, wikipedia_link, keywords))