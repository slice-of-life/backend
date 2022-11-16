"""
    :module_name: instance
    :module_summary: utility class for interacting Slice Of Life database
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import psycopg2

from ..exceptions import DatabaseNotConnectedError

class Instance:
    """
        Object that represents a database instance for the Slice Of Life
    """

    def __init__(self, **config):
        self._dbname = config.get("dbname", None)
        self._dbuser = config.get("dbuser", None)
        self._dbpass = config.get("dbpass", None)
        self._dbhost = config.get("dbhost", None)
        self._dbport = config.get("dbport", 5432) # postgresql default port
        self._connection = None

    def connect(self) -> None:
        """
            Establish a connection the database specified by **config in __init__
        """
        if self._connection:
            return
        self._connection = psycopg2.connect(dbname=self._dbname,
                                            user=self._dbuser,
                                            password=self._dbpass,
                                            host=self._dbhost,
                                            port=self._dbport
                                            )

    def query(self, sql: str) -> psycopg2.extensions.cursor:
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
            conn.execute(sql)
            return conn.fetchmany()

    def query_one_row(self, sql: str) -> tuple:
        """
            Execute the given sql query and return a single tuple as the result
            :arg sql: the query to execute
            :arg type: str
            :returns: query result if successful
            :rtype: tuple
            :throws: DatabaseNotConnectedError if no connection is established
        """
        if not self._connection:
            raise DatabaseNotConnectedError("No active connection to execute query on")

        with self._connection.cursor() as conn:
            conn.execute(sql)
            return conn.fetchone()
