"""
    module_name: test_get_response
    module_summary: tests for the slice of life GET api responses
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import json
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
        ]

    }

def lookup_db(conn, query):
    if set(query.parameters.keys()) == {'limit', 'offset'}:
        return mock_db()['posts'][query.parameters['offset']:query.parameters['offset'] + query.parameters['limit']]
    if set(query.parameters.keys()) == {'handle'}:
        for user in mock_db()['users']:
            if user[0] == query.parameters['handle']:
                return (user,)
    if set(query.parameters.keys()) == {'taskid'}:
        for task in mock_db()['tasks']:
            if task[0] == query.parameters['taskid']:
                return (task,)

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
