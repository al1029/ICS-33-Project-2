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