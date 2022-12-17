"""
    :module_name: api
    :module_summary: implementation for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os

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

    def __init__(self):
        self._conn = None

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
                    'dbname': cls._env.get('DBNAME', os.getenv('DBNAME')),
                    'user': cls._env.get('DBUSER', os.getenv('DBUSER')),
                    'password': cls._env.get('DBPASS', os.getenv('DBPASS')),
                    'host': cls._env.get('DBHOST', os.getenv('DBHOST')),
                    'port': cls._env.get('DBPORT', os.getenv('DBPORT'))
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
                return jsonify(method(ref, *args))
            except ContentNotFoundError as exc:
                LOGGER.error("Requested content does not exist")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Not found", 404)
            except AuthorizationError as exc:
                LOGGER.error("Insufficient permissions")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Not authorized", 401)
            except ServiceNotReachable as exc:
                LOGGER.error("The requested resource timed out")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Bad gateway", 504)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                LOGGER.error("The request could not be understood")
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Bad request", 400)
            except SliceOfLifeAPIException as exc:
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Internal Server Error", 500)

        return wrapper
