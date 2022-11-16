"""
    :module_name: routes
    :module_summary: functions that defines the api routes for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

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
