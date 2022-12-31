"""
    :module_name: test_sliceoflife_webservice
    :module_summary: tests for webservice endpoints
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from unittest.mock import patch

from sliceoflife_webservice import app
from sliceoflife_webservice.api import BaseSliceOfLifeApiResponse
from sliceoflife_webservice.api.get import SliceOfLifeApiGetResponse
from sliceoflife_webservice.api.post import SliceOfLifeApiPostResponse
from sliceoflife_webservice.api.options import SliceOfLifeApiOptionsResponse

import pytest
from flask import request

@pytest.fixture
def test_client():
    return app.test_client()

@patch.object(SliceOfLifeApiGetResponse, 'hello')
def test_greeting_endpoint(mock_get, test_client):
    response = test_client.get('/api/v1/greeting')
    assert response.request.path == '/api/v1/greeting'
    assert response.request.method == 'GET'
    assert mock_get.called

@patch.object(SliceOfLifeApiGetResponse, 'get_latest_posts')
def test_latest_posts_endpoint(mock_get, test_client):
    response = test_client.get('/api/v1/slices/latest')
    assert response.request.path == '/api/v1/slices/latest'
    assert response.request.method == 'GET'
    assert mock_get.called

@pytest.mark.parametrize('test_post_id', range(1, 10))
@patch.object(SliceOfLifeApiGetResponse, 'get_slice_by_id')
def test_specific_post_endpoint(mock_get, test_post_id, test_client):
    response = test_client.get(f'/api/v1/slices/{test_post_id}')
    assert response.request.path == f'/api/v1/slices/{test_post_id}'
    assert response.request.method == 'GET'
    assert mock_get.called_once_with(test_post_id)

@pytest.mark.parametrize('test_post_id', range(1, 10))
@patch.object(SliceOfLifeApiGetResponse, 'get_reactions_for_slice')
def test_specific_reactions_endpoint(mock_get, test_post_id, test_client):
    response = test_client.get(f'/api/v1/slices/{test_post_id}/reactions')
    assert response.request.path == f'/api/v1/slices/{test_post_id}/reactions'
    assert response.request.method == 'GET'
    assert mock_get.called_once_with(test_post_id)

@pytest.mark.parametrize('test_post_id', range(1, 10))
@patch.object(SliceOfLifeApiGetResponse, 'get_comments_for_slice')
def test_specific_comments_endpoint(mock_get, test_post_id, test_client):
    response = test_client.get(f'/api/v1/slices/{test_post_id}/comments')
    assert response.request.path == f'/api/v1/slices/{test_post_id}/comments'
    assert response.request.method == 'GET'
    assert mock_get.called_once_with(test_post_id)

@pytest.mark.parametrize('test_handle', ['user1', 'user2'])
@patch.object(SliceOfLifeApiGetResponse, 'get_user_profile')
def test_authorized_profile_view_endpoint(mock_get, test_handle, test_client):
    response = test_client.get(f'/api/v1/users/{test_handle}/profile')
    assert response.request.path == f'/api/v1/users/{test_handle}/profile'
    assert response.request.method == 'GET'
    assert mock_get.called_once_with(test_handle)

@pytest.mark.parametrize('test_handle', ['user1', 'user2'])
@patch.object(SliceOfLifeApiGetResponse, 'get_user_tasklist')
def test_authorized_tasklist_view_endpoint(mock_get, test_handle, test_client):
    response = test_client.get(f'/api/v1/users/{test_handle}/tasklist')
    assert response.request.path == f'/api/v1/users/{test_handle}/tasklist'
    assert response.request.method == 'GET'
    assert mock_get.called_once_with(test_handle)

@patch.object(SliceOfLifeApiPostResponse, 'create_user')
def test_account_creation_endpoint(mock_post, test_client):
    response = test_client.post('/api/v1/users/account/new')
    assert response.request.path == '/api/v1/users/account/new'
    assert response.request.method == 'POST'
    assert mock_post.called

@patch.object(SliceOfLifeApiPostResponse, 'authenticate_user')
def test_authentication_endpoint(mock_post, test_client):
    response = test_client.post('/api/v1/users/authenticate')
    assert response.request.path == '/api/v1/users/authenticate'
    assert response.request.method == 'POST'
    assert mock_post.called

@patch.object(SliceOfLifeApiPostResponse, 'create_new_post')
def test_post_creation_endpoint(mock_post, test_client):
    response = test_client.post('/api/v1/slices/new')
    assert response.request.path == '/api/v1/slices/new'
    assert response.request.method == 'POST'
    assert mock_post.called
