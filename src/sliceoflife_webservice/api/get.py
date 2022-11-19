"""
    :module_name: get
    :module_summary: functions that defines the GET methods for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from dotenv import dotenv_values

from ..dbtools import Instance
from ..dbtools.queries import paginated_posts, specific_user, specific_task
from ..dbtools.schema import interpret_as, Post, User, Task

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
    results = [interpret_as(Post, r) for r in results]
    for res in results:
        if not isinstance(res.posted_by, User):
            res.posted_by = _get_basic_post_author_info(res.posted_by)
        if not isinstance(res.completes, Task):
            res.completes = _get_task_info(res.completes)
    return results

def _get_basic_post_author_info(author_handle: str) -> User:
    dbinstance = Instance(**dotenv_values())
    dbinstance.connect()
    query = specific_user(author_handle)
    uinfo = interpret_as(User, dbinstance.query(query)[0]) #should only be one anyway
    # hide sensitive information
    uinfo.password_hash = "***"
    uinfo.salt = "***"
    uinfo.email = "***"
    return uinfo

def _get_task_info(task_id: int) -> Task:
    dbinstance = Instance(**dotenv_values())
    dbinstance.connect()
    query = specific_task(task_id)
    tinfo = interpret_as(Task, dbinstance.query(query)[0]) #should only be one anyway
    return tinfo
