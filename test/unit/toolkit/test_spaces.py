"""
    module_name: test_spaces
    module_summary: test the SpaceIndex class from toolkit module
    module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import pytest
from botocore.exceptions import EndpointConnectionError

from sliceoflife_webservice.toolkit import SpaceIndex
from sliceoflife_webservice.exceptions import ServiceNotReachable

@pytest.fixture
def mock_space_config():
    """Mock config settings for space index testing"""
    return {
        'SPACES_REGION': 'local',
        'SPACES_ENDPOINT': 'http://127.0.0.1:3200',
        'SPACES_KEY': 'access key',
        'SPACES_SECRET': 'shh... it\'s a secret!'
    }

def test_space_index_is_created_without_session(mock_space_config):
    """Test for checking initial session status of SpaceIndex objects"""
    msi = SpaceIndex(**mock_space_config)
    assert msi.has_active_session() is False

def test_space_index_has_active_session_after_creation(mock_space_config):
    """Test for existing session after creating one"""
    msi = SpaceIndex(**mock_space_config)
    msi.create_session()
    assert msi.has_active_session() is True

def test_cannot_get_share_link_if_no_active_session(mock_space_config):
    """Test obtaining share link prohibited without active session"""
    msi = SpaceIndex(**mock_space_config)
    with pytest.raises(ServiceNotReachable):
        msi.get_share_link('postauthor/taskimage.png')

def test_can_get_share_link_with_active_session(mock_space_config):
    """Test share link obtainable with active session"""
    msi = SpaceIndex(**mock_space_config)
    msi.create_session()
    assert msi.get_share_link('postauthor/taskimage.png').startswith(
        f"{mock_space_config['SPACES_ENDPOINT']}/{SpaceIndex.SPACES_BUCKET}/postauthor/taskimage.png"
    )

def test_cannot_save_file_if_no_active_session(mock_space_config):
    """Test file saving prohibited without active session"""
    msi = SpaceIndex(**mock_space_config)
    with pytest.raises(ServiceNotReachable):
        msi.save_file("postimage_copy.jpeg", "postimage.jpeg")

def test_can_save_file_with_active_session(mock_space_config):
    """Test file saving available with active session"""
    msi = SpaceIndex(**mock_space_config)
    msi.create_session()
    with pytest.raises(EndpointConnectionError):
        msi.save_file("postimage_copy.jpeg", open("test/files/postimage.jpeg", 'rb'))
