"""
    :module_name: instance
    :module_summary: utility class for interacting Slice Of Life database
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

from ..exceptions import ServiceNotReachable

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
        self._connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

    def query(self, query: sql.SQL) -> psycopg2.extensions.cursor:
        """
            Execute the given sql query and return an iterable containing the results
            :arg sql: the query to execute
            :returns: query result if successful
            :rtype: psycopg2.extensions.cursor
            :throws: ServiceNotReachable if no connection is established
        """
        if not self._connection:
            raise ServiceNotReachable("No active connection to execute query on")

        with self._connection.cursor() as conn:
            LOGGER.debug("Execute query: %s", query.as_string(self._connection))
            conn.execute(query)
            return conn.fetchall()

    def query_no_fetch(self, query: sql.SQL) -> None:
        """
            Execute the given sql query and return nothing. Useful for insertion or deletion
            :arg sql: the query to execute
            :returns: nothing
            :rtype: NoneType
            :throws: ServiceNotReachable if no connection is established
        """
        if not self._connection:
            raise ServiceNotReachable("No active connection ot execute query on")

        with self._connection.cursor() as conn:
            LOGGER.debug("Execute query: %s", query.as_string(self._connection))
            conn.execute(query)

    def __enter__(self):
        if not self._connection:
            self.connect()
        LOGGER.debug("BEGIN TRANSACTION")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_value:
            self._connection.rollback()
            LOGGER.debug("Exception occured durring transaction: %s", str(exc_value))
            LOGGER.debug("TRANSACTION CANCELLED")
        else:
            self._connection.commit()
            LOGGER.debug("TRANSACTION COMMITTED")
