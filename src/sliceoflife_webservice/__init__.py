"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from flask import Flask

from .api import hello

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(
    logging.Formatter("[%(asctime)s]:[%(levelname)s] -- %(message)s")
)
LOGGER.addHandler(
    HANDLER
)

def app():
    """
        declares an instance of the sliceoflife api
        :returns: API instance
        :rtype: FlaskApp
    """
    api = Flask(__name__)
    LOGGER.info("Creating an api instance")
    api.add_url_rule('/api/v1/greet', endpoint='greet', view_func=hello)
    LOGGER.info("Added endpoint: 'GET /api/v1/greet'")

    return api
