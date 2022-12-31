"""
    module_name: test_get_response
    module_summary: tests for the slice of life GET api responses
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import time
from unittest.mock import patch

import pytest

from sliceoflife_webservice.dbtools import Instance
from sliceoflife_webservice.toolkit import SpaceIndex
from sliceoflife_webservice.api.get import SliceOfLifeApiGetResponse
from sliceoflife_webservice import app

from . import lookup_db


def test_greeting_response():
    with app.test_request_context('/api/v1/greeting', method='GET'):
        assert SliceOfLifeApiGetResponse().hello().get_data() == bytes(
            '{"msg":"Welcome to the first endpoint of the slice of life api"}\n',
            'utf-8')
        assert SliceOfLifeApiGetResponse().hello().status == '200 OK'

@pytest.mark.parametrize('limit, offset, result', [
    (4, 0, b'{"next":"http://127.0.0.1:8000/api/v1/slices/latest?limit=4&offset=4","page":[{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Thu, 15 Dec 2022 00:00:00 GMT","free_text":"post text 1","image":"post pic 1","post_id":1,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}},{"completes":{"active":true,"description":"task3 description","task_id":3,"title":"task3"},"created_at":"Thu, 08 Dec 2022 00:00:00 GMT","free_text":"post text 2","image":"post pic 2","post_id":2,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}},{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Tue, 29 Nov 2022 00:00:00 GMT","free_text":"post text 3","image":"post pic 3","post_id":3,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}},{"completes":{"active":true,"description":"task1 description","task_id":1,"title":"task1"},"created_at":"Sat, 19 Nov 2022 00:00:00 GMT","free_text":"post text 4","image":"post pic 4","post_id":4,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}}]}\n'),
    (2, 0, b'{"next":"http://127.0.0.1:8000/api/v1/slices/latest?limit=2&offset=2","page":[{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Thu, 15 Dec 2022 00:00:00 GMT","free_text":"post text 1","image":"post pic 1","post_id":1,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}},{"completes":{"active":true,"description":"task3 description","task_id":3,"title":"task3"},"created_at":"Thu, 08 Dec 2022 00:00:00 GMT","free_text":"post text 2","image":"post pic 2","post_id":2,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}}]}\n'),
    (2, 1, b'{"next":"http://127.0.0.1:8000/api/v1/slices/latest?limit=2&offset=3","page":[{"completes":{"active":true,"description":"task3 description","task_id":3,"title":"task3"},"created_at":"Thu, 08 Dec 2022 00:00:00 GMT","free_text":"post text 2","image":"post pic 2","post_id":2,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}},{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Tue, 29 Nov 2022 00:00:00 GMT","free_text":"post text 3","image":"post pic 3","post_id":3,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}}]}\n'),
    (2, 2, b'{"next":"http://127.0.0.1:8000/api/v1/slices/latest?limit=2&offset=4","page":[{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Tue, 29 Nov 2022 00:00:00 GMT","free_text":"post text 3","image":"post pic 3","post_id":3,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}},{"completes":{"active":true,"description":"task1 description","task_id":1,"title":"task1"},"created_at":"Sat, 19 Nov 2022 00:00:00 GMT","free_text":"post text 4","image":"post pic 4","post_id":4,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}}]}\n'),
    (4, 4, b'{"next":"http://127.0.0.1:8000/api/v1/slices/latest?limit=4&offset=4","page":[]}\n')
])
def test_latest_posts_response(limit, offset, result):
    with app.test_request_context(f'/slices/latest?limit={limit}&offset={offset}', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_latest_posts().get_data() == result
                assert SliceOfLifeApiGetResponse().get_latest_posts().status == '200 OK'

@pytest.mark.parametrize('sliceid, result', [
    (1, b'{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Thu, 15 Dec 2022 00:00:00 GMT","free_text":"post text 1","image":"post pic 1","post_id":1,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}}\n'),
    (2, b'{"completes":{"active":true,"description":"task3 description","task_id":3,"title":"task3"},"created_at":"Thu, 08 Dec 2022 00:00:00 GMT","free_text":"post text 2","image":"post pic 2","post_id":2,"posted_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}}\n'),
    (3, b'{"completes":{"active":true,"description":"task2 description","task_id":2,"title":"task2"},"created_at":"Tue, 29 Nov 2022 00:00:00 GMT","free_text":"post text 3","image":"post pic 3","post_id":3,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}}\n'),
    (4, b'{"completes":{"active":true,"description":"task1 description","task_id":1,"title":"task1"},"created_at":"Sat, 19 Nov 2022 00:00:00 GMT","free_text":"post text 4","image":"post pic 4","post_id":4,"posted_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}}\n')
])
def test_slice_by_id_response(sliceid, result):
    with app.test_request_context(f'/slices/{sliceid}', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_slice_by_id(sliceid).get_data() == result
                assert SliceOfLifeApiGetResponse().get_slice_by_id(sliceid).status == '200 OK'

@pytest.mark.parametrize('postid, result', [
    (1, b'{"threads":[{"comment":{"comment_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"},"comment_id":6,"comment_on":1,"created_id":"Sun, 18 Dec 2022 00:00:00 GMT","free_text":"comment6text","parent":null},"responses":[]}]}\n'),
    (2, b'{"threads":[{"comment":{"comment_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"},"comment_id":4,"comment_on":2,"created_id":"Sat, 10 Dec 2022 00:00:00 GMT","free_text":"comment4text","parent":null},"responses":[{"comment":{"comment_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"},"comment_id":5,"comment_on":2,"created_id":"Mon, 12 Dec 2022 00:00:00 GMT","free_text":"comment5text","parent":4},"responses":[]}]}]}\n'),
    (3, b'{"threads":[{"comment":{"comment_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"},"comment_id":3,"comment_on":3,"created_id":"Wed, 30 Nov 2022 00:00:00 GMT","free_text":"comment3text","parent":null},"responses":[]}]}\n'),
    (4, b'{"threads":[{"comment":{"comment_by":{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"},"comment_id":1,"comment_on":4,"created_id":"Sun, 20 Nov 2022 00:00:00 GMT","free_text":"comment1text","parent":null},"responses":[{"comment":{"comment_by":{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"},"comment_id":2,"comment_on":4,"created_id":"Mon, 21 Nov 2022 00:00:00 GMT","free_text":"comment2text","parent":1},"responses":[]}]}]}\n')
])
def test_comment_tree_building(postid, result):
    with app.test_request_context(f'/slices/{postid}/comments', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_comments_for_slice(postid).get_data() == result
                assert SliceOfLifeApiGetResponse().get_comments_for_slice(postid).status == '200 OK'

@pytest.mark.parametrize('postid, result', [
    (1, b'[{"count":1,"reaction":"code1","reactors":["user2"]}]\n'),
    (2, b'[{"count":1,"reaction":"code2","reactors":["user2"]}]\n'),
    (3, b'[{"count":2,"reaction":"code2","reactors":["user1","user2"]}]\n'),
    (4, b'[{"count":1,"reaction":"code1","reactors":["user1"]},{"count":1,"reaction":"code2","reactors":["user1"]}]\n')
])
def test_gather_reaction_stats(postid, result):
    with app.test_request_context(f'/slices/{postid}/reactions', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_reactions_for_slice(postid).get_data() == result
                assert SliceOfLifeApiGetResponse().get_reactions_for_slice(postid).status == '200 OK'

def test_nonexistant_slice_response():
    with app.test_request_context('/slices/5', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_slice_by_id(5).get_data() == b'Not found'
                assert SliceOfLifeApiGetResponse().get_slice_by_id(5).status == '404 NOT FOUND'

@pytest.mark.parametrize('user, access_token, result', [
    ('user1', SliceOfLifeApiGetResponse().create_auth_token('user1'), b'{"email":"***","first_name":"user1first","handle":"user1","last_name":"user1last","password_hash":"***","profile_pic":"user1.png","salt":"***"}\n'),
    ('user2', SliceOfLifeApiGetResponse().create_auth_token('user2'), b'{"email":"***","first_name":"user2first","handle":"user2","last_name":"user2last","password_hash":"***","profile_pic":"user2.png","salt":"***"}\n')
])
def test_profile_access_with_token(user, access_token, result):
    with app.test_request_context(f'/users/{user}/profile', method='GET', headers={'x-auth-token': access_token}):
        time.sleep(2) # allow token to be activated
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_user_profile(user).get_data() == result
                assert SliceOfLifeApiGetResponse().get_user_profile(user).status == '200 OK'

@pytest.mark.parametrize('user', ['user1', 'user2'])
def test_profile_access_without_token(user):
    with app.test_request_context(f'/users/{user}/profile', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_user_profile(user).get_data() == b'Not authorized'
                assert SliceOfLifeApiGetResponse().get_user_profile(user).status == '401 UNAUTHORIZED'

@pytest.mark.parametrize('user, access_token, result', [
    ('user1', SliceOfLifeApiGetResponse().create_auth_token('user1'), b'{"available":[{"active":true,"description":"task1 description","task_id":1,"title":"task1"}],"completed":[{"active":true,"description":"task2 description","task_id":2,"title":"task2"},{"active":true,"description":"task3 description","task_id":3,"title":"task3"}]}\n'),
    ('user2', SliceOfLifeApiGetResponse().create_auth_token('user2'), b'{"available":[{"active":true,"description":"task3 description","task_id":3,"title":"task3"}],"completed":[{"active":true,"description":"task1 description","task_id":1,"title":"task1"},{"active":true,"description":"task2 description","task_id":2,"title":"task2"}]}\n')
])
def test_tasklist_access_with_token(user, access_token, result):
    with app.test_request_context(f'/users/{user}/tasklist', method='GET', headers={'x-auth-token': access_token}):
        time.sleep(2) # alloww token to be activated
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_user_tasklist(user).get_data() == result
                assert SliceOfLifeApiGetResponse().get_user_tasklist(user).status == '200 OK'

@pytest.mark.parametrize('user', ['user1', 'user2'])
def test_tasklist_access_without_token(user):
    with app.test_request_context(f'/users/{user}/tasklist', method='GET'):
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_user_tasklist(user).get_data() == b'Not authorized'
                assert SliceOfLifeApiGetResponse().get_user_tasklist(user).status == '401 UNAUTHORIZED'

@pytest.mark.parametrize('user, invalid_token', [
    ('user1', SliceOfLifeApiGetResponse().create_auth_token('user2')),
    ('user2', SliceOfLifeApiGetResponse().create_auth_token('user1'))
])
def test_profile_access_with_invalid_token(user, invalid_token):
    with app.test_request_context(f'/users/{user}/profile', method='GET', headers={'x-auth-token': invalid_token}):
        time.sleep(2) # allow token to be activated
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_user_profile(user).get_data() == b'Not authorized'
                assert SliceOfLifeApiGetResponse().get_user_profile(user).status == '401 UNAUTHORIZED'

@pytest.mark.parametrize('user, invalid_token', [
    ('user1', SliceOfLifeApiGetResponse().create_auth_token('user2')),
    ('user2', SliceOfLifeApiGetResponse().create_auth_token('user1'))
])
def test_tasklist_access_with_invalid_token(user, invalid_token):
    with app.test_request_context(f'/users/{user}/tasklist', method='GET', headers={'x-auth-token': invalid_token}):
        time.sleep(2)  # allow token to be activated
        with patch.object(Instance, 'query') as mock_query:
            with patch.object(SpaceIndex, 'get_share_link') as mock_share:
                mock_query.side_effect = lookup_db
                mock_share.side_effect = lambda x: x
                assert SliceOfLifeApiGetResponse().get_user_tasklist(user).get_data() == b'Not authorized'
                assert SliceOfLifeApiGetResponse().get_user_tasklist(user).status == '401 UNAUTHORIZED'

