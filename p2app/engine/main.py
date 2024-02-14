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

        return_event = None

        if isinstance(event, OpenDatabaseEvent):
            return_event = self.open_database(event.path())
        elif isinstance(event, QuitInitiatedEvent):
            if self.cursor is not None and self.connection is not None:
                self.close_database()
            return_event = EndApplicationEvent()
        elif isinstance(event, CloseDatabaseEvent):
            self.close_database()
            return_event = DatabaseClosedEvent()

        yield return_event


    def open_database(self, path: Path) -> DatabaseOpenedEvent:
        """Opens a sql database from the specified path.

        Args:
            path: the path to a sql database.

        Returns:
              The DatabaseOpenedEvent with the path to the database.
        """

        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        return DatabaseOpenedEvent(path)


    def close_database(self):
        """Closes the cursor and database."""

        self.cursor.close()
        self.cursor = None
        self.connection.close()
        self.connection = None