"""
    :module_name: get
    :module_summary: functions that defines the GET methods for the slice of life api
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
    LOGGER.debug("Generated response: %s", str(response))
    return response
