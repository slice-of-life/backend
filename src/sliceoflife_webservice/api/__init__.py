"""
    :module_name: api
    :module_summary: implementation for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from dotenv import dotenv_values
from flask import jsonify, session

from ..dbtools import Instance
from ..toolkit import SpaceIndex
from ..exceptions import SliceOfLifeAPIException, ContentNotFoundError, \
                         AuthorizationError, ServiceNotReachable

LOGGER = logging.getLogger("gunicorn.error")

DBCONNECTIONS = 10

class BaseSliceOfLifeApiResponse():
    """
        A base class for all slice of life API subclasses
        Has a single db and cdn connection with public references
    """

    _env = dotenv_values()
    _instance = None
    _space = None

    def has_authorized(self, handle: str) -> bool:
        """
            Returns true if the given handle has an active session. False otherwise
            :arg handle: the handle to check an active session for
            :rtype: boolean
        """
        return handle in session

    @property
    def instance(self):
        """
            returns a reference to the api's shared db connection, creates it if is does not exist
            :returns: reference to dbinstance
            :rtype: Instance
        """
        if not self._instance:
            self._instance = Instance(DBCONNECTIONS, **self._env)
        return self._instance

    @property
    def spaces(self):
        """
            returns a reference to the api's shared cdn session, creates it if it does not exist
            :returns: shared cdn session
            :rtype: SpaceIndex
        """
        if not self._space:
            self._space = SpaceIndex(**self._env)
            if not self._space.has_active_session():
                self._space.create_session()
        return self._space

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
                return jsonify(method(ref, *args))
            except ContentNotFoundError:
                LOGGER.error("Requested content does not exist")
                return ("Not found", 404)
            except AuthorizationError:
                LOGGER.error("Insufficient permissions")
                return ("Not authorized", 401)
            except ServiceNotReachable:
                LOGGER.error("The requested resource timed out")
                return ("Bad gateway", 504)
            except (KeyError, IndexError, TypeError, ValueError):
                LOGGER.error("The request could not be understood")
                return ("Bad request", 400)
            except SliceOfLifeAPIException as exc:
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Internal Server Error", 500)

        return wrapper
