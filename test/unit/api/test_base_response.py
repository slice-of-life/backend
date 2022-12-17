"""
    module_name: test_base_response
    module_summary: tests for the base slice of life response class
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from unittest.mock import patch

import pytest
import psycopg2

from sliceoflife_webservice.api import BaseSliceOfLifeApiResponse, DBCONNECTIONS
from sliceoflife_webservice.dbtools import Instance
from sliceoflife_webservice.toolkit import SpaceIndex
from sliceoflife_webservice.exceptions import ContentNotFoundError, AuthorizationError, \
                                              ServiceNotReachable, SliceOfLifeAPIException

def test_shared_service_classes_not_defined_initially():
    """Test shared resources created lazily"""
    res = BaseSliceOfLifeApiResponse()
    assert res._instance is None
    assert res._space is None
    assert res._conn is None

def test_shared_instance_created_on_demand():
    res = BaseSliceOfLifeApiResponse()
    with patch('psycopg2.connect') as mock_connect:
        assert isinstance(res.instance, Instance)
        assert len(res.instance._pool) == DBCONNECTIONS

def test_shared_spaces_created_on_demand():
    res = BaseSliceOfLifeApiResponse()
    assert isinstance(res.spaces, SpaceIndex)
    assert res.spaces.has_active_session()

@pytest.mark.parametrize('outcome', [0, 1, 2, 3, 4])
def test_safe_callback_decorator(outcome):
    @BaseSliceOfLifeApiResponse.safe_api_callback
    def mock_response_function(res: int):
        if res == 0:
            return {}
        if res == 1:
            raise ContentNotFoundError()
        if res == 2:
            raise AuthorizationError()
        if res == 3:
            raise ValueError()
        raise SliceOfLifeAPIException()
    outcomes = {
        0: {},
        1: ("Not found", 404),
        2: ("Not authorized", 401),
        3: ("Bad request", 400),
        4: ("Internal Server Error", 500)
    }
    assert mock_response_function(outcome) == outcomes[outcome]
