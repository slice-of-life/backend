"""
    :module_name: instance
    :module_summary: utility class for interacting Slice Of Life database
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os

import psycopg2
from psycopg2 import sql

from ..exceptions import DatabaseNotConnectedError

LOGGER = logging.getLogger('gunicorn.error')

class Instance:
    """
        Object that represents a database instance for the Slice Of Life
    """

    def __init__(self, **config):
        self._dbname = config.get("DBNAME", os.getenv("DBNAME"))
        self._dbuser = config.get("DBUSER", os.getenv("DBUSER"))
        self._dbpass = config.get("DBPASS", os.getenv("DBPASS"))
        self._dbhost = config.get("DBHOST", os.getenv("DBHOST"))
        self._dbport = config.get("DBPORT", os.getenv("DBPORT", '5432')) # postgresql default port
        self._connection = None

    def connect(self) -> None:
        """
            Establish a connection the database specified by **config in __init__
        """
        if self._connection:
            return
        LOGGER.debug("Establishing connection to psql://***@%s:%s", self._dbhost, self._dbport)
        self._connection = psycopg2.connect(dbname=self._dbname,
                                            user=self._dbuser,
                                            password=self._dbpass,
                                            host=self._dbhost,
                                            port=self._dbport
                                            )

    def query(self, query: sql.SQL) -> psycopg2.extensions.cursor:
        """
            Execute the given sql query and return an iterable containing the results
            :arg sql: the query to execute
            :arg type: str
            :returns: query result if successful
            :rtype: psycopg2.extensions.cursor
            :throws: DatabaseNotConnectedError if no connection is established
        """
        if not self._connection:
            raise DatabaseNotConnectedError("No active connection to execute query on")

        with self._connection.cursor() as conn:
            LOGGER.debug("Execute query: %s", query.as_string(self._connection))
            conn.execute(query)
            return conn.fetchall()
