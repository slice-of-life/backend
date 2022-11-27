"""
    :module_name: sliceoflife_webservice
    :module_summary: entry point for the slice of life backend
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
from dataclasses import asdict

from dotenv import load_dotenv
from flask import Flask, request, session

from .api.get import SliceOfLifeApiGetResponse
from .api.post import SliceOfLifeApiPostResponse

from .exceptions import SliceOfLifeBaseException, DuplicateHandleError, \
                        NoSuchUserError, InvalidCredentialsError

LOGGER = logging.getLogger('gunicorn.error')

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SESSION_KEY')

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
        LOGGER.error("error occured while responding: %s", str(exc))
        return (f"No such slice: {slice_id}", 404)

LOGGER.info("Added the route: POST /api/v1/users/account/new")
@app.route('/api/v1/users/account/new', methods=['POST'])
def create_new_user():
    """
        Create a new slice of life user account. Only basic information required to get started
    """
    form_data = {
        'handle': request.form['handle'],
        'email': request.form['email'],
        'password': request.form['password'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
    }
    try:
        return SliceOfLifeApiPostResponse(**form_data).create_user()
    except DuplicateHandleError as exc:
        LOGGER.error("Duplicate handle: %s", str(exc))
        return ("Handle unavailable", 403)
    except SliceOfLifeBaseException as exc:
        LOGGER.error("Exception occurred while responding: %s", str(exc))
        return (str(exc), 500)

LOGGER.info("Added the route: POST /api/v1/users/authenticate")
@app.route('/api/v1/users/authenticate', methods=['POST'])
def authenticate_user():
    """
        Authenticate the user. Gives the client an auth token if successful that can be used later
    """
    form_data = {
        'handle': request.form['handle'],
        'password': request.form['password']
    }
    try:
        auth_token = SliceOfLifeApiPostResponse(**form_data).authenticate_user()
        session[request.form['handle']] = auth_token
        return {
            'token': auth_token
        }
    except NoSuchUserError:
        LOGGER.error("No such credentials: %s", form_data['handle'])
        return ("Invalid handle/password", 403)
    except InvalidCredentialsError:
        LOGGER.error("Credentials did not match")
        return ("Invalid handle/password", 403)
    except SliceOfLifeBaseException as exc:
        LOGGER.error("Error occured while responding: %s", str(exc))
        return ("Internal server error", 500)
