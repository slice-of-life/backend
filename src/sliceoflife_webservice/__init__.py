"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os

from dotenv import load_dotenv
from flask import Flask, request

from .api import hello, get_latest_posts

LOGGER = logging.getLogger('gunicorn.error')

load_dotenv()

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

LOGGER.info("Added the route: GET /api/v1/slices/latest")
@app.route('/api/v1/slices/latest', methods=['GET'])
def latest_slices():
    """
        GET the most recent slices of life (posts)
    """
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    LOGGER.info("Responding to GET /api/v1/slices/latest?limit=%d&offset=%d", limit, offset)
    return get_latest_posts(limit, offset)
