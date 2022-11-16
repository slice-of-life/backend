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

if __name__ != "__main__": #This is weird, but it is definitely suppose to be like this
    app.logger.handlers = LOGGER.handlers
    app.logger.setLevel(LOGGER.level)

app.logger.info("Created an API application instance")

app.logger.info("Added the route: GET /api/v1/greeting")
@app.route('/api/v1/greeting', methods=['GET'])
def greeting():
    """
       The first API method of the Slice Of Life API
    """
    app.logger.info("Responding to GET /api/v1/greeting")
    app.logger.info("Sent: %s", str(hello()))

    return hello()
