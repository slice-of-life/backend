"""
    :module_name: get
    :module_summary: functions that defines the GET methods for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from dotenv import dotenv_values

from ..dbtools import Instance
from ..dbtools.queries import paginated_posts
from ..dbtools.schema import Post

LOGGER = logging.getLogger('gunicorn.error')

def hello() -> dict:
    """
        A simple GET API route that introduces the Slice Of Life API
        :returns: A static JSON response
        :rtype: dict
    """
    response = {
        'msg': 'Welcome to the first endpoint of the slice of life api'
    }
    return response

def get_latest_posts(limit: int, offset: int) -> dict:
    """
        A GET route that returns the most recently posted slices of life. Pages results by offset
        :arg limit: the size of the page of results
        :arg offset: the location where to start the next page of results.
        :returns: a JSON object of posts and their associated information
        :rtype: dict
    """
    dbinstance = Instance(**dotenv_values())
    dbinstance.connect()
    query = paginated_posts(limit, offset)
    results = dbinstance.query(query)
    return [Post(*r) for r in results]
