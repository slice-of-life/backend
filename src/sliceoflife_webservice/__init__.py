"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
from dataclasses import asdict

from dotenv import load_dotenv
from flask import Flask, request

from .api.get import SliceOfLifeApiGetResponse

from .exceptions import SliceOfLifeBaseException

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

    return SliceOfLifeApiGetResponse().hello()

LOGGER.info("Added the route: GET /api/v1/slices/latest")
@app.route('/api/v1/slices/latest', methods=['GET'])
def latest_slices():
    """
        GET the most recent slices of life (posts)
    """
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    LOGGER.info("Responding to GET /api/v1/slices/latest?limit=%d&offset=%d", limit, offset)
    return SliceOfLifeApiGetResponse().get_latest_posts(limit, offset)

LOGGER.info("Added the route: GET /api/v1/slices/<:id>")
@app.route('/api/v1/slices/<int:slice_id>', methods=['GET'])
def slice_by_id(slice_id: int):
    """
        GET the slice by its ID (post)
    """
    LOGGER.info("Responding to GET /api/v1/slices/%d", slice_id)
    try:
        return asdict(SliceOfLifeApiGetResponse().get_slice_by_id(slice_id))
    except SliceOfLifeBaseException as exc:
        LOGGER.error("Error occurred while responding: %s", str(exc))
        return (f"No such slice: {slice_id}", 404)

LOGGER.info("Added the route: GET /api/v1/slices/<:id>/comments")
@app.route('/api/v1/slices/<int:slice_id>/comments', methods=['GET'])
def comments_for_slice(slice_id: int):
    """
        GET the comments for a given post
    """
    LOGGER.info("Responding to GET /api/v1/slices/%d/comments", slice_id)
    try:
        return SliceOfLifeApiGetResponse().get_comments_for_slice(slice_id)
    except SliceOfLifeBaseException as exc:
        LOGGER.error("Error occured while responding: %s", str(exc))
        return (f"No such slice: {slice_id}", 404)

LOGGER.info("Added the route: GET /api/v1/slices/<:id>/reactions")
@app.route('/api/v1/slices/<int:slice_id>/reactions', methods=['GET'])
def reactions_for_slice(slice_id: int):
    """
        GET the reactions for a given post
    """
    try:
        return SliceOfLifeApiGetResponse().get_reactions_for_slice(slice_id)
    except SliceOfLifeBaseException as exc:
        LOGGER.error("error occured while resopnding: %s", str(exc))
        return (f"No such slice: {slice_id}", 404)
