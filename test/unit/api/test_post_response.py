"""
    :module_name: test_post_response
    :module_summary: tests for POST responses
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import time
import secrets
from unittest.mock import patch
from io import BytesIO

import pytest
import jwt

from sliceoflife_webservice.dbtools import Instance
from sliceoflife_webservice.toolkit import SpaceIndex
from sliceoflife_webservice.api.post import SliceOfLifeApiPostResponse
from sliceoflife_webservice import app

from . import update_db, lookup_db, mock_db

def test_create_new_user_with_available_handle():
    form ={
        "handle": "user3",
        "email": "user3@mail.com",
        "password": "pass3",
        "first_name": "user3first",
        "last_name": "user3last"
    }
    with app.test_request_context('/users/account/new', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().create_user().get_data() == b'"CREATED user3"\n'
                    assert SliceOfLifeApiPostResponse().create_user().status == '200 OK'

def test_create_new_user_with_unavailable_handle():
    form ={
        "handle": "user1",
        "email": "user1@mail.com",
        "password": "pass1",
        "first_name": "user1first",
        "last_name": "user1last"
    }
    with app.test_request_context('/users/account/new', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().create_user().get_data() == b'Not authorized'
                    assert SliceOfLifeApiPostResponse().create_user().status == '401 UNAUTHORIZED'

@patch('secrets.compare_digest', return_value=True)
@patch('jwt.encode', return_value="testtoken")
def test_successful_authentication(mock_digest, mock_jwt):
    form = {
        "handle": "user1",
        "password": "pass1"
    }
    with app.test_request_context('/users/authenticate', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().authenticate_user().get_data() == b'{"token":"testtoken"}\n'
                    assert SliceOfLifeApiPostResponse().authenticate_user().status == '200 OK'

@patch('secrets.compare_digest', return_value=False)
def test_incorrect_credentials_authentication(mock_digest):
    form = {
        "handle": "user1",
        "password": "pass1"
    }
    with app.test_request_context('/users/authenticate', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().authenticate_user().get_data() == b'Not authorized'
                    assert SliceOfLifeApiPostResponse().authenticate_user().status == '401 UNAUTHORIZED'

def test_fake_credentials_authentication():
    form = {
        "handle": "user10",
        "password": "pass10"
    }
    with app.test_request_context('/users/authenticate', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().authenticate_user().get_data() == b'Not authorized'
                    assert SliceOfLifeApiPostResponse().authenticate_user().status == '401 UNAUTHORIZED'

@patch.object(SliceOfLifeApiPostResponse, 'verify_auth_token', return_value=True)
def test_authorized_post_creation(mock_auth):
    form = {
        'handle': 'user1',
        'free_text': 'new post text',
        'task_id': 1,
        'slice_image': (BytesIO(b'Slice Image'), 'slice_image.png')
    }
    with app.test_request_context('/slices/new', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().create_new_post().get_data() == b'"CREATED"\n'
                    assert SliceOfLifeApiPostResponse().create_new_post().status == '200 OK'

@patch.object(SliceOfLifeApiPostResponse, 'verify_auth_token', return_value=False)
def test_unauthorized_post_creation(mock_auth):
    form = {
        'handle': 'user1',
        'free_text': 'new post text',
        'task_id': 1,
        'slice_image': (BytesIO(b'Slice Image'), 'slice_image.png')
    }
    with app.test_request_context('/slices/new', method='POST', data=form):
        with patch.object(Instance, 'query_no_fetch') as mock_query_no_fetch:
            with patch.object(Instance, 'query') as mock_query:
                with patch.object(SpaceIndex, 'save_file') as mock_save:
                    mock_query_no_fetch.side_effect = update_db
                    mock_query.side_effect = lookup_db
                    mock_save.side_effect = lambda x, y: time.sleep(3)
                    assert SliceOfLifeApiPostResponse().create_new_post().get_data() == b'Not authorized'
                    assert SliceOfLifeApiPostResponse().create_new_post().status == '401 UNAUTHORIZED'
