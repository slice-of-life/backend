"""
    module_name: test_dbschema
    module_summary: Tests for slice of life data schema classes
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import pytest

from sliceoflife_webservice.dbtools.schema import User, Task, Post, \
                                                  Reaction, Completion, Comment


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
