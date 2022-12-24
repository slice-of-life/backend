"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
from dataclasses import asdict
from secrets import compare_digest

from dotenv import load_dotenv
from flask import Flask, request

from .api.get import SliceOfLifeApiGetResponse
from .api.post import SliceOfLifeApiPostResponse

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
    LOGGER.info("Responding to GET /api/v1/slices/latest")
    return SliceOfLifeApiGetResponse().get_latest_posts()

LOGGER.info("Added the route: GET /api/v1/slices/<:id>")
@app.route('/api/v1/slices/<int:slice_id>', methods=['GET'])
def slice_by_id(slice_id: int):
    """
        GET the slice by its ID (post)
    """
    LOGGER.info("Responding to GET /api/v1/slices/<id>")
    return SliceOfLifeApiGetResponse().get_slice_by_id(slice_id)

LOGGER.info("Added the route: GET /api/v1/slices/<:id>/comments")
@app.route('/api/v1/slices/<int:slice_id>/comments', methods=['GET'])
def comments_for_slice(slice_id: int):
    """
        GET the comments for a given post
    """
    LOGGER.info("Responding to GET /api/v1/slices/<id>/comments")
    return SliceOfLifeApiGetResponse().get_comments_for_slice(slice_id)

LOGGER.info("Added the route: GET /api/v1/slices/<:id>/reactions")
@app.route('/api/v1/slices/<int:slice_id>/reactions', methods=['GET'])
def reactions_for_slice(slice_id: int):
    """
        GET the reactions for a given post
    """
    LOGGER.info("Responding to GET /api/v1/slices/<id>/reactions")
    return SliceOfLifeApiGetResponse().get_reactions_for_slice(slice_id)

LOGGER.info("Added the route: GET /api/v1/users/<:handle>/profile")
@app.route('/api/v1/users/<string:handle>/profile', methods=['GET'])
def user_profile_information(handle: str):
    """
        GET the basic profile information for a given user handle
    """
    LOGGER.info("Responding to GET /api/v1/users/<handle>/profile")
    return SliceOfLifeApiGetResponse().get_user_profile(handle)

LOGGER.info("Added the route: GET /api/v1/users/<:handle>/tasklist")
@app.route('/api/v1/users/<string:handle>/tasklist', methods=['GET'])
def user_task_list(handle: str):
    """
        GET the task list for the given user
    """
    LOGGER.info("Responding to GET /api/v1/users/<handle>/tasklist")
    return SliceOfLifeApiGetResponse().get_user_tasklist(handle)

LOGGER.info("Added the route: POST /api/v1/users/account/new")
@app.route('/api/v1/users/account/new', methods=['POST'])
def create_new_user():
    """
        Create a new slice of life user account. Only basic information required to get started
    """
    LOGGER.info("Responding to POST /api/v1/users/account/new")
    return SliceOfLifeApiPostResponse().create_user()

LOGGER.info("Added the route: POST /api/v1/users/authenticate")
@app.route('/api/v1/users/authenticate', methods=['POST'])
def authenticate_user():
    """
        Authenticate the user. Gives the client an auth token if successful that can be used later
    """
    LOGGER.info("Responding to POST /api/v1/users/authenticate")
    return SliceOfLifeApiPostResponse().authenticate_user()

LOGGER.info("Added the route: POST /api/v1/slices/new")
@app.route('/api/v1/slices/new', methods=['POST'])
def new_post():
    """
        Create a new post, if the user is authenicated

    """
    LOGGER.info("Responding to POST /api/v1/slices/new")
    return SliceOfLifeApiPostResponse().create_new_post()
