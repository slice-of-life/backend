"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from flask import Flask

from .api import hello

LOGGER = logging.getLogger('gunicorn.error')

app = Flask(__name__)

LOGGER.info("Created an API application instance")

LOGGER.info("Added the route: GET /api/v1/greeting")
@app.route('/api/v1/greeting', methods=['GET'])
def greeting():
    """
       The first API method of the Slice Of Life API
    """
    LOGGER.info("Responding to GET /api/v1/greeting")

    return hello()
