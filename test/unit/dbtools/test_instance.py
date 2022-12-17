"""
    module_name: test_instance
    module_summary: tests for Instance class
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from unittest.mock import MagicMock, patch
import pytest

from psycopg2.extensions import connection, cursor
from psycopg2.sql import SQL
import psycopg2

from sliceoflife_webservice.exceptions import ServiceNotReachable, SliceOfLifeAPIException
from sliceoflife_webservice.dbtools import Instance
from sliceoflife_webservice.dbtools.queries.statement import PreparedStatement

class MockConnection(connection):
    def __init__(self, dbname, user, password, host, port): pass
    def commit(self): pass
    def rollback(self): pass
    def cursor(self): return MockCursor()

class MockCursor(cursor):
    def __init__(self): pass
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, traceback): pass
    def execute(self, sql, *args): pass
    def fetchall(self): return ('results')

config = {
        'dbname': 'db',
        'user': 'dbuser',
        'password': 'supersecretpassphrase',
        'host': 'http://127.0.0.1',
        'port': '5500'
    }

@pytest.fixture
def mock_database_instance():
    """Test database instance"""
    return Instance(5, **config)

@pytest.fixture
def mock_sql_query():
    """Test sql query"""
    return PreparedStatement(SQL("SELECT 1"))

psycopg2.connect = MagicMock(return_value=MockConnection(**config))

def test_instance_exists(mock_database_instance):
    """Test creation of mocked instance class"""
    assert isinstance(mock_database_instance, Instance)
    assert len(mock_database_instance._pool) == 5

def test_all_connections_initially_available(mock_database_instance):
    """Test that all connection available initially"""
    assert all(c.available for c in mock_database_instance._pool)

def test_borrow_connection_from_pool(mock_database_instance):
    """Test the connection borrowing feature"""
    with mock_database_instance.start_transaction() as conn:
        assert isinstance(conn, MockConnection)
        assert mock_database_instance._pool[0].available is False

    assert mock_database_instance._pool[0].available is True

def test_exception_raised_if_no_more_connections_to_borrow(mock_database_instance):
    """Test exception raised when no connection available"""
    all_borrowed = [mock_database_instance._getconn() for _ in range(5)]
    assert all(c.available is False for c in mock_database_instance._pool)
    with pytest.raises(ServiceNotReachable):
        mock_database_instance._getconn()
    for conn in all_borrowed:
        mock_database_instance._putconn(conn)
    assert all(c.available for c in mock_database_instance._pool)

def test_query_cannot_be_made_with_non_connection_object(mock_sql_query):
    """Test query prohibition without borrowed connection"""
    with pytest.raises(ServiceNotReachable):
        Instance.query('a fake connection', mock_sql_query)

    with pytest.raises(ServiceNotReachable):
        Instance.query_no_fetch('a fake connection', mock_sql_query)

def test_query_made_with_borrowed_connection(mock_database_instance, mock_sql_query):
    """Test proper query with borrowed connection"""
    with mock_database_instance.start_transaction() as conn:
        assert Instance.query(conn, mock_sql_query) == ('results')
        assert Instance.query_no_fetch(conn, mock_sql_query) is None

def test_transaction_committed_when_completed_successfully(mock_database_instance, mock_sql_query):
    with patch('test_instance.MockConnection.commit') as mock_commit:
        with mock_database_instance.start_transaction() as conn:
            assert Instance.query(conn, mock_sql_query) == ('results')

        assert mock_commit.called

def test_transaction_rollback_when_failure(mock_database_instance):
    with patch('test_instance.MockConnection.rollback') as mock_cancel:
        with pytest.raises(SliceOfLifeAPIException):
            with mock_database_instance.start_transaction():
                raise ServiceNotReachable("The database transaction failed")

        assert mock_cancel.called
