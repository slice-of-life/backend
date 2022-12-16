"""
    :module_name: instance
    :module_summary: utility class for interacting Slice Of Life database
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import threading
from dataclasses import dataclass
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

from ..exceptions import SliceOfLifeAPIException, ServiceNotReachable
from .queries.statement import PreparedStatement

LOGGER = logging.getLogger('gunicorn.error')

@dataclass
class ControlledConnection:
    """
        Connection wrapper with availability attribute
    """
    connection: psycopg2.extensions.connection
    available: bool

class Instance():
    """
        Object that represents a database instance for the Slice Of Life
    """

    def __init__(self, pool_size, **config):
        self._conn_conf = config
        self._pool = self._make_pool(pool_size)
        self._pool_lock = threading.Lock()

    @contextmanager
    def start_transaction(self) -> psycopg2.extensions.connection:
        """
            Acquire a connection from the pool to be used in a transaction. Release when completed
            :returns: A secured sql connection from the connection pool
            :rtype: psycopg2.exceptions.connection
        """
        resource = None
        try:
            resource = self._getconn()
            yield resource
        except SliceOfLifeAPIException as exc:
            LOGGER.error("Exception occurred during transaction: %s", str(exc))
            LOGGER.info("ROLLBACK TRANSACTION")
            resource.rollback()
            raise
        else:
            LOGGER.info("Transaction executed successfully")
            LOGGER.info("COMMIT TRANSACTION")
            resource.commit()
        finally:
            if resource:
                self._putconn(resource)

    @staticmethod
    def query(conn: psycopg2.extensions.connection, query: PreparedStatement) -> tuple:
        """
            Execute the given sql query on the given connection and return results as in iterable
            :arg conn: the connection to execute on
            :arg sql: the query to execute
            :returns: query result if successful
            :rtype: tuple
            :throws: ServiceNotReachable if no connection is established
        """
        if not isinstance(conn, psycopg2.extensions.connection):
            raise ServiceNotReachable("No active connection to execute query on")

        with conn.cursor() as cur:
            LOGGER.debug("Execute query: %s", query.statement.as_string(conn))
            cur.execute(query.statement, query.parameters)
            return cur.fetchall()

    @staticmethod
    def query_no_fetch(conn: psycopg2.extensions.connection, query: PreparedStatement):
        """
            Execute the given sql query and return nothing. Useful for insertion or deletion
            :arg sql: the query to execute
            :returns: nothing
            :rtype: NoneType
            :throws: ServiceNotReachable if no connection is established
        """
        if not isinstance(conn, psycopg2.extensions.connection):
            raise ServiceNotReachable("No active connection ot execute query on")

        with conn.cursor() as cur:
            LOGGER.debug("Execute query: %s", query.statement.as_string(conn))
            cur.execute(query.statement, query.parameters)


    def _connect(self) -> psycopg2.extensions.connection:
        LOGGER.debug(
            "Establishing connection to psql://***@%s:%s",
            self._conn_conf['dbname'],
            self._conn_conf['port']
        )
        _conn = psycopg2.connect(**self._conn_conf)
        _conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        return _conn

    def _make_pool(self, size: int):
        return [
            ControlledConnection(self._connect(), True) for _ in range(size)
        ]

    def _getconn(self):
        with self._pool_lock:
            for conn in self._pool:
                if conn.available:
                    conn.available = False
                    return conn.connection
            raise ServiceNotReachable("No available database connections")

    def _putconn(self, conn: psycopg2.extensions.connection):
        with self._pool_lock:
            for _conn in self._pool:
                if id(_conn.connection) == id(conn):
                    _conn.available = True
