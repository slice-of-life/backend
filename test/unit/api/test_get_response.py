"""
    module_name: test_get_response
    module_summary: tests for the slice of life GET api responses
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import json
import time
from datetime import datetime
from unittest.mock import patch

import pytest
from flask import request

from sliceoflife_webservice.dbtools import Instance
from sliceoflife_webservice.toolkit import SpaceIndex
from sliceoflife_webservice.dbtools.queries import paginated_posts, specific_user, specific_task
from sliceoflife_webservice.dbtools.queries.statement import PreparedStatement
from sliceoflife_webservice.api.get import SliceOfLifeApiGetResponse
from sliceoflife_webservice import app

def mock_db():
    return {
        'posts': [
            (1, 'post text 1', 'post pic 1', datetime(2022, 12, 15), 'user1', 2),
            (2, 'post text 2', 'post pic 2', datetime(2022, 12, 8), 'user1', 3),
            (3, 'post text 3', 'post pic 3', datetime(2022, 11, 29), 'user2', 2),
            (4, 'post text 4', 'post pic 4', datetime(2022, 11, 19), 'user2', 1)
        ],
        'users': [
            ('user1', 'hash1', 'user1@mail.com', 'salt1', 'user1first', 'user1last', 'user1.png'),
            ('user2', 'hash2', 'user2@mail.com', 'salt2', 'user2first', 'user2last', 'user2.png')
        ],
        'tasks':[
            (1, 'task1', 'task1 description', True),
            (2, 'task2', 'task2 description', True),
            (3, 'task3', 'task3 description', True)
        ],
        'comments': [
            (1, datetime(2022, 11, 20), 'comment1text', None, 'user1', 4),
            (2, datetime(2022, 11, 21), 'comment2text', 1, 'user2', 4),
            (3, datetime(2022, 11, 30), 'comment3text', None, 'user1', 3),
            (4, datetime(2022, 12, 10), 'comment4text', None, 'user2', 2),
            (5, datetime(2022, 12, 12), 'comment5text', 4, 'user1', 2),
            (6, datetime(2022, 12, 18), 'comment6text', None, 'user2', 1)
        ],
        'reactions': [
            (1, 'code1', 'user2', 1),
            (2, 'code2', 'user2', 2),
            (3, 'code2', 'user1', 3),
            (4, 'code2', 'user2', 3),
            (5, 'code1', 'user1', 4),
            (6, 'code2', 'user1', 4)
        ],
        'completions': [
            ('user1', 2),
            ('user1', 3),
            ('user2', 1),
            ('user2', 2)
        ]

    }

def lookup_db(conn, query):
    if set(query.parameters.keys()) == {'limit', 'offset'}:
        return mock_db()['posts'][query.parameters['offset']:query.parameters['offset'] + query.parameters['limit']]
    if set(query.parameters.keys()) == {'handle'}:
        for user in mock_db()['users']:
            if user[0] == query.parameters['handle']:
                return (user,)
        return tuple()
    if set(query.parameters.keys()) == {'taskid'}:
        for task in mock_db()['tasks']:
            if task[0] == query.parameters['taskid']:
                return (task,)
        return tuple()
    if set(query.parameters.keys()) == {'postid'}:
        for post in mock_db()['posts']:
            if post[0] == query.parameters['postid']:
                return (post,)
        return tuple()
    if set(query.parameters.keys()) == {'commentto'}:
        return tuple([
            comment
            for comment in mock_db()['comments']
            if comment[5] == query.parameters['commentto'] and comment[3] is None
        ])
    if set(query.parameters.keys()) == {'commentto', 'commentid'}:
        return tuple([
            comment
            for comment in mock_db()['comments']
            if comment[5] == query.parameters['commentto'] and comment[3] == query.parameters['commentid']
        ])
    if set(query.parameters.keys()) == {'reactto'}:
        result = []
        seen = set()
        for reaction in mock_db()['reactions']:
            if reaction[3] == query.parameters['reactto'] and reaction[1] not in seen:
               result.append(reaction)
               seen.add(reaction[1])
        return tuple(result)
    if set(query.parameters.keys()) == {'reactto', 'codecount'}:
        count = len([
            reaction
            for reaction in mock_db()['reactions']
            if reaction[3] == query.parameters['reactto'] and reaction[1] == query.parameters['codecount']
        ])
        return ((count,),)
    if set(query.parameters.keys()) == {'reactto', 'codeused'}:
        return tuple([
            (reaction[2],)
            for reaction in mock_db()['reactions']
            if reaction[3] == query.parameters['reactto'] and reaction[1] == query.parameters['codeused']
        ])
    if set(query.parameters.keys()) == {'completes'}:
        return tuple([
            task
            for task in mock_db()['tasks']
            if task[0] in [completion[1]
                           for completion in mock_db()['completions']
                           if completion[0] == query.parameters['completes']
                           ]
        ])
    if set(query.parameters.keys()) == {'incompletes'}:
        return tuple([
            task
            for task in mock_db()['tasks']
            if task[0] not in [completion[1]
                               for completion in mock_db()['completions']
                               if completion[0] == query.parameters['incompletes']
                               ]
        ])

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

