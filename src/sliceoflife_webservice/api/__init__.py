"""
    :module_name: api
    :module_summary: implementation for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
import datetime

import jwt
from dotenv import load_dotenv
from flask import jsonify, make_response, request

from ..dbtools import Instance
from ..toolkit import SpaceIndex
from ..exceptions import SliceOfLifeAPIException, ContentNotFoundError, \
                         AuthorizationError, ServiceNotReachable

LOGGER = logging.getLogger("gunicorn.error")

DBCONNECTIONS = 10

load_dotenv()

class BaseSliceOfLifeApiResponse():
    """
    A base class for all slice of life API subclasses
        Has a single db and cdn connection with public references
    """

    _instance = None
    _space = None
    _auth_secret_key = os.getenv('APP_AUTH_KEY')
    _jwt_algoritm="HS256"

    def __init__(self):
        self._conn = None

    def create_auth_token(self, token_for: str) -> str:
        """
           Generate a new JWT for the given user handle
           :arg token_for: handle this JWT is for
           :returns: an encoded JWT
           :rtype: str
        """
        claims = {
            'handle': token_for,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'nbf': datetime.datetime.utcnow() + datetime.timedelta(seconds=2),
        }
        LOGGER.debug("Generate JWT token for %s", token_for)
        return jwt.encode(claims, self._auth_secret_key, algorithm=self._jwt_algoritm)


    def verify_auth_token(self, token_for: str) -> bool:
        """
            Returns true if the given handle has a valid token. False otherwise
            :arg token: the token with the encoded authorization claims
            :arg token_for: the handle that claims ownership of the token
            :rtype: boolean
            :throws AuthorizationError: if no auth token is found in the request headers
        """
        try:
            token = request.headers.get('x-auth-token')
            if not token:
                raise AuthorizationError('Missing authentication token in request headers')
            claims = jwt.decode(token,
                                self._auth_secret_key,
                                algorithms=self._jwt_algoritm,
                                require=['handle', 'exp', 'nbf']
                                )
            LOGGER.debug("Token formatted is valid. Verifying owernship")
            return claims['handle'] == token_for
        except jwt.exceptions.MissingRequiredClaimError as exc:
            LOGGER.debug("Token is missformated")
            LOGGER.error("Claim missing from token: %s", str(exc))
            return False
        except (jwt.exceptions.ImmatureSignatureError, jwt.exceptions.ExpiredSignatureError) as exc:
            LOGGER.debug("Token is not valid")
            LOGGER.error("Claim immature or expired %s", str(exc))
            return False

    @property
    def instance(self):
        """
            returns a reference to the api's shared db connection, creates it if is does not exist
            :returns: reference to dbinstance
            :rtype: Instance
        """
        return self._shared_instance()

    @property
    def spaces(self):
        """
            returns a reference to the api's shared cdn session, creates it if it does not exist
            :returns: shared cdn session
            :rtype: SpaceIndex
        """
        return self._shared_space_index()

    @classmethod
    def _shared_instance(cls):
        if not cls._instance:
            cls. _instance = Instance(
                DBCONNECTIONS,
                **{
                    'dbname': os.getenv('DBNAME'),
                    'user': os.getenv('DBUSER'),
                    'password': os.getenv('DBPASS'),
                    'host': os.getenv('DBHOST'),
                    'port': os.getenv('DBPORT')
                }
            )
        return cls._instance

    @classmethod
    def _shared_space_index(cls):
        if not cls._space:
            cls._space = SpaceIndex()
            if not cls._space.has_active_session():
                cls._space.create_session()
        return cls._space

    @staticmethod
    def safe_api_callback(method: callable) -> callable:
        """
            A decorator that provides error handling for API callbacks
            :arg method: the API callback to protect
            :returns: safe API response callback
            :rtype: callable
        """
        def wrapper(ref, *args):
            try:
                LOGGER.info("Request from %s", str(request.headers.get('Origin')))
                response = make_response(jsonify(method(ref, *args)), 200)
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            except ContentNotFoundError as exc:
                LOGGER.error("Requested content does not exist")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return make_response("Not found", 404)
            except AuthorizationError as exc:
                LOGGER.error("Insufficient permissions")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return make_response("Not authorized", 401)
            except ServiceNotReachable as exc:
                LOGGER.error("The requested resource timed out")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return make_response("Bad gateway", 504)
            except (KeyError, IndexError) as exc:
                LOGGER.error("The request could not be understood")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return make_response("Bad request", 400)
            except SliceOfLifeAPIException as exc:
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return make_response("Internal server error", 500)

        return wrapper
