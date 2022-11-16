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

app.add_url_rule('/api/v1/greet', endpoint='greet', view_func=hello)
app.logger.info("Added the route: GET /api/v1/greet")
