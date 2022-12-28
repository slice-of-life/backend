"""
    module_name: test_base_response
    module_summary: tests for the base slice of life response class
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import json
import datetime
import time
from unittest.mock import patch

import pytest
from freezegun import freeze_time
from flask import Response

from sliceoflife_webservice import app
from sliceoflife_webservice.api import BaseSliceOfLifeApiResponse, DBCONNECTIONS
from sliceoflife_webservice.dbtools import Instance
from sliceoflife_webservice.toolkit import SpaceIndex
from sliceoflife_webservice.exceptions import ContentNotFoundError, AuthorizationError, \
                                              ServiceNotReachable, SliceOfLifeAPIException

@pytest.fixture
def mock_auth_token():
    return BaseSliceOfLifeApiResponse().create_auth_token('user')

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

@pytest.mark.parametrize('outcome', [0, 1, 2, 3, 4, 5])
def test_safe_callback_decorator(outcome):
    @BaseSliceOfLifeApiResponse.safe_api_callback
    def mock_response_function(res: int):
        if res == 0:
            return {
                'key': 'value'
            }
        if res == 1:
            raise ContentNotFoundError()
        if res == 2:
            raise AuthorizationError()
        if res == 3:
            raise KeyError()
        if res == 4:
            raise ServiceNotReachable()
        raise SliceOfLifeAPIException()
    outcomes = {
        0: Response(response='{"key":"value"}\n', status=200),
        1: Response(response="Not found", status=404),
        2: Response(response="Not authorized", status=401),
        3: Response(response="Bad request", status=400),
        4: Response(response="Bad gateway", status=504),
        5: Response(response="Internal server error", status=500)
    }
    with app.test_request_context('/', method='GET'):
        assert mock_response_function(outcome).get_data() == outcomes[outcome].get_data()
        assert mock_response_function(outcome).status == outcomes[outcome].status

def test_create_JWTs(mock_auth_token):
    assert isinstance(mock_auth_token, str)

def test_validated_JWT(mock_auth_token):
    with app.test_request_context('api/users/authenticate',
                                  method='POST',
                                  headers={'x-auth-token': mock_auth_token}):
        time.sleep(2) # Allow token to mature (likely not an issue over a network)
        assert BaseSliceOfLifeApiResponse().verify_auth_token('user')

def test_immature_JWT(mock_auth_token):
    with app.test_request_context('api/users/authenticate',
                                  method='POST',
                                  headers={'x-auth-token': mock_auth_token}):
        assert not BaseSliceOfLifeApiResponse().verify_auth_token('user')

def test_expired_JWT(mock_auth_token):
    with app.test_request_context('api/users/authenticate',
                                  method='POST',
                                  headers={'x-auth-token': mock_auth_token}):
        with freeze_time(datetime.datetime.utcnow() + datetime.timedelta(days=14)):
            assert not BaseSliceOfLifeApiResponse().verify_auth_token('user')

def test_missing_JWT():
    with app.test_request_context('/api/users/authenticate', method='POST'):
        with pytest.raises(AuthorizationError):
            BaseSliceOfLifeApiResponse().verify_auth_token('user')
