# p2app/engine/main.py
#
# ICS 33 Winter 2024
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.


import sqlite3
from p2app.events import *
from .handle_continents import get_continent
from .handle_continents import load_continent_info
from .handle_continents import save_continent


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.

    Attributes:
        connection: the sql connection
        cursor: the sql cursor
    """

    def __init__(self):
        """Initializes the engine"""

        self.connection = None
        self.cursor = None


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.

        if isinstance(event, OpenDatabaseEvent):
            yield self.open_database(event.path())
        elif isinstance(event, QuitInitiatedEvent):
            if self.cursor is not None and self.connection is not None:
                self.close_database()
            yield EndApplicationEvent()
        elif isinstance(event, CloseDatabaseEvent):
            self.close_database()
            yield DatabaseClosedEvent()
        elif isinstance(event, StartContinentSearchEvent):
            yield from get_continent(self.cursor, event.continent_code(), event.name())
        elif isinstance(event, LoadContinentEvent):
            yield load_continent_info(self.cursor, event.continent_id())
        elif isinstance(event, SaveContinentEvent):
            yield save_continent(self.cursor, event.continent())
        else:
            yield from ()

        #self.commit_changes()


    def open_database(self, path: Path) -> DatabaseOpenedEvent | DatabaseOpenFailedEvent:
        """Opens a sql database from the specified path.

        Args:
            path: the path to a sql database.

        Returns:
              The DatabaseOpenedEvent with the path to the database.
              DatabaseOpenFailedEvent with a user-friendly error message
        """

        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.execute('PRAGMA foreign_keys = ON;')

        # Checks if the file is a database
        try:
            self.connection.execute('PRAGMA integrity_check')
        except sqlite3.DatabaseError:
            self.cursor.close()
            self.connection.close()
            return DatabaseOpenFailedEvent('Not a database file')

        # Checks if the database is an airport database
        correct_tables_list = [('continent',), ('country',), ('region',),
                               ('airport',), ('airport_frequency',), ('runway',), ('navigation_aid',)]
        list_of_tables = self.cursor.execute(
            """SELECT name 
               FROM sqlite_master 
               WHERE type='table'""").fetchall()
        for table in correct_tables_list:
            if table not in list_of_tables:
                self.cursor.close()
                self.connection.close()
                return DatabaseOpenFailedEvent('Not an airport database')

        return DatabaseOpenedEvent(path)


    def close_database(self):
        """Closes the cursor and database."""

        self.cursor.close()
        self.cursor = None
        self.connection.close()
        self.connection = None


    def commit_changes(self):
        """Commits to memory changes made to the database."""

        #self.connection.commit()
        pass