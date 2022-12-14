"""
    module_name: test_templates
    module_summary: tests for sql templates
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import datetime
import pytest
import psycopg2

import sliceoflife_webservice.dbtools.queries as templates
from sliceoflife_webservice.dbtools.schema import User, Post, Completion

@pytest.fixture
def mock_query_context():
    """Mock connect to covert sql composables to strings"""
    return psycopg2.connect()

def test_paginated_posts_templates_with_no_offset(mock_query_context):
    """Test the paginated_posts template with no offset"""
    template = templates.paginated_posts(20)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'limit': 20, 'offset': 0}

def test_paginated_posts_templates_with_offset(mock_query_context):
    """Test the paginated_posts template with offset"""
    template = templates.paginated_posts(20, 5)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'limit': 20, 'offset': 5}

def test_specific_user_templates(mock_query_context):
    """Test the specific_user template"""
    template = templates.specific_user('handle')
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'handle': 'handle'}

def test_specific_task_template(mock_query_context):
    """Test the specific_task template"""
    template = templates.specific_task(1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'taskid': 1}

def test_specific_post_template(mock_query_context):
    """Test the specific_post template"""
    template = templates.specific_post(1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'postid': 1}

def test_top_level_comments_template(mock_query_context):
    """Test the top_level_comments template"""
    template = templates.top_level_comments(1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'postid': 1}

def test_comments_responding_to_template(mock_query_context):
    template = templates.comments_responding_to(1, 1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'postid': 1, 'commentid': 1}

def test_reaction_by_groups_template(mock_query_context):
    template = templates.reactions_by_group(1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'postid': 1}

def test_reaction_counts_template(mock_query_context):
    template = templates.reaction_counts('code', 1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'postid': 1, 'code': 'code'}

def test_reactors_by_emoji_template(mock_query_context):
    template = templates.reactors_by_emoji('code', 1)
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'postid': 1, 'code': 'code'}

def test_insert_user_account_template(mock_query_context):
    template = templates.insert_user_account(User('handle',
                                                  'pass',
                                                  'email',
                                                  'salt',
                                                  'first',
                                                  'last',
                                                  'avatar')
                                             )
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {
        'handle': 'handle',
        'password': 'pass',
        'email': 'email',
        'salt': 'salt',
        'first': 'first',
        'last': 'last',
        'avatar': 'avatar'
    }

def test_insert_post_template(mock_query_context):
    template = templates.insert_post(Post(1,
                                          'freetext',
                                          'post/image.png',
                                          datetime.datetime(2022, 12, 15),
                                          1,
                                          1)
                                     )
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {
        'freetext': 'freetext',
        'image': 'post/image.png',
        'date': datetime.datetime(2022, 12, 15),
        'author': 1,
        'completes': 1
    }

def test_insert_completion_template(mock_query_context):
    template = templates.insert_completion(Completion(1, 1))
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'user': 1, 'task': 1}

def test_available_tasks_template(mock_query_context):
    template = templates.available_tasks('handle')
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'handle': 'handle'}

def test_completed_tasks_template(mock_query_context):
    template = templates.completed_tasks('handle')
    assert template.statement.as_string(mock_query_context)
    assert template.parameters == {'handle': 'handle'}
