"""
    :module_name: routes
    :module_summary: functions that defines the api routes for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

LOGGER = logging.getLogger('gunicorn.error')

def hello():
    response = {
        'msg': 'Welcome to the first endpoint of the slice of life api'
    }

    LOGGER.info("Responding to GET /api/v1/greet")
    LOGGER.info("sent: %s", str(response))

    return response
