"""
    :module_name: test_api
    :module_summary: test data for api test suite
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from datetime import datetime

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

def update_db(conn, query):
    if set(query.parameters.keys()) == {'handle', 'password', 'email', 'salt', 'first', 'last', 'avatar'}:
        new_user = (
            query.parameters['handle'],
            query.parameters['password'],
            query.parameters['email'],
            query.parameters['salt'],
            query.parameters['first'],
            query.parameters['last'],
            query.parameters['avatar']
        )
        new_db_state = mock_db()
        new_db_state['users'].append(new_user)
        return new_db_state
    if set(query.parameters.keys()) == {'freetext', 'image', 'date', 'author', 'completes'}:
        new_post = (
            max(post[0] for post in mock_db()['posts']) + 1,
            query.parameters['freetext'],
            query.parameters['image'],
            query.parameters['date'],
            query.parameters['author'],
            query.parameters['completes']
        )
        new_db_state = mock_db()
        new_db_state['posts'].append(new_post)
        return new_db_state
    if set(query.parameters.keys()) == {'user', 'task'}:
        new_completion = (query.parameters['user'], query.parameters['task'])
        new_db_state = mock_db()
        new_db_state['completions'].append(new_completion)
        return new_db_state
