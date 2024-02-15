# p2app/engine/handle_regions.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# Handles the processes related to regions

import sqlite3
from p2app.events import *
from sqlite3 import Cursor


def get_region(cursor: Cursor, region_code: str, local_code: str, name: str) -> RegionSearchResultEvent | None:
    """A generator function that returns the region that corresponds to the search field.

    Args:
        cursor: a cursor object used to query the database
        region_code: the region code
        local_code: the local code
        name: the name of the region

    Returns:
        RegionSearchResultEvent if a region is found
        No events if no region was found
    """

    query = 'SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE '
    parameters = []

    if region_code is not None:
        query += 'region_code=?'
        parameters.append(region_code)
    if local_code is not None:
        if region_code is not None:
            query += ' AND '
        query += 'local_code=?'
        parameters.append(local_code)
    if name is not None:
        if region_code is not None or local_code is not None:
            query += ' AND '
        query += 'name=?'
        parameters.append(name)

    cursor.execute(query, parameters)

    all_rows = cursor.fetchall()
    if all_rows is None:
        yield from ()
    else:
        for row in all_rows:
            yield RegionSearchResultEvent(Region(*row))


def load_region_info(cursor: Cursor, region_id: int) -> RegionLoadedEvent:
    """Returns the region with the info for the view.

    Args:
        cursor: a cursor object used to the query the database
        region_id: the region id

    Returns:
        RegionLoadedEvent containing the loaded information about the region
    """

    cursor.execute(f'SELECT region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords FROM region WHERE region_id={region_id}')
    return RegionLoadedEvent(Region(*cursor.fetchone()))


def save_region(cursor: Cursor, region: Region) -> RegionSavedEvent | SaveRegionFailedEvent:
    """Saves the modified region to the airport database.

    Args:
        cursor: a cursor object used to query the database
        region: a namedtuple that holds info about the region

    Returns:
        RegionSavedEvent if saving the region succeeded
        SaveRegionFailedEvent if saving the region failed
    """

    region_code = region.region_code.strip()
    local_code = region.local_code.strip()
    name = region.name.strip()
    continent_id = region.continent_id
    country_id = region.country_id
    wikipedia_link = region.wikipedia_link if region.wikipedia_link is None else region.wikipedia_link.strip()
    keywords = region.keywords if region.keywords is None else region.keywords.strip()

    if region_code == '':
        region_code = None
    if local_code == '':
        local_code = None
    if name == '':
        name = None

    parameters = (region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords)
    query = f'UPDATE region SET region_code=? ,local_code=?, name=?, continent_id=?, country_id=?, wikipedia_link=?, keywords=? WHERE region_id={region.region_id}'

    try:
        cursor.execute(query, parameters)
    except sqlite3.Error:
        return SaveRegionFailedEvent('Error adding specified fields')
    else:
        return RegionSavedEvent(Region(region.region_id, *parameters))