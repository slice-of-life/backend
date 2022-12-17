"""
    module_name: test_dbschema
    module_summary: Tests for slice of life data schema classes
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import datetime

import pytest

from sliceoflife_webservice.dbtools.schema import User, Task, Post, \
                                                  Reaction, Completion, Comment, \
                                                  interpret_as


@pytest.mark.parametrize("datatype, exists", [
                                                ('User', True),
                                                ('Task', True),
                                                ('Post', True),
                                                ('Reaction', True),
                                                ('Completion', True),
                                                ('Comment', True),
                                                ('SomeOtherClass', False)
                                             ])
def test_data_schema_is_defined(datatype, exists):
    """Test that the dataclasses defining app dataschema are defined"""
    assert (datatype in globals()) is exists

@pytest.mark.parametrize("datatype, datarow", [
    (User, ('handle', 'pass', 'email', 'salt', 'first', 'last', 'profile pic')),
    (Task, (1, 'title', 'description', True)),
    (Post, (1, 'free text', 'image', datetime.datetime.utcnow(), 'user', 1)),
    (Reaction, (1, 'emoji', 'user', 1)),
    (Completion, ('user', 1)),
    (Comment, (1, datetime.datetime.utcnow(), 'free text', None, 'user', 1))
])
def test_data_interpretation(datatype, datarow):
    """Test that the interpret_as function convert a data tuple to the specified type"""
    datainstance = interpret_as(datatype, datarow)
    assert isinstance(datainstance, datatype)

@pytest.mark.parametrize("datatype, datarow", [
    (Comment, ('handle', 'pass', 'email', 'salt', 'first', 'last', 'profile pic')),
    (User, (1, 'title', 'description', True)),
    (Task, (1, 'free text', 'image', datetime.datetime.utcnow(), 'user', 1)),
    (Post, (1, 'emoji', 'user', 1)),
    (Reaction, ('user', 1)),
    (Completion, (1, datetime.datetime.utcnow(), 'free text', None, 'user', 1))
])
def test_data_interpretation_misuse(datatype, datarow):
    """Test that misusing interpret_as throws a TypeError"""
    with pytest.raises(TypeError):
        interpret_as(datatype, datarow)
