"""
    :module_name: api
    :module_summary: implementation for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
from abc import ABC

from dotenv import dotenv_values
from flask import jsonify

from ..dbtools import Instance
from ..toolkit import SpaceIndex
from ..exceptions import SliceOfLifeAPIException, ContentNotFoundError, \
                         AuthorizationError, ServiceNotReachable

LOGGER = logging.getLogger("gunicorn.error")

class BaseSliceOfLifeApiResponse(ABC):
    """
        A base class for all slice of life API subclasses
        Has a single db and cdn connection with public references
    """
    dbinstance: Instance = Instance(**dotenv_values())
    blobinstance: SpaceIndex = SpaceIndex(**dotenv_values())

    @property
    def db_connection(self):
        """
            returns a reference to the api's shared db connection, creates it if is does not exist
            :returns: reference to dbinstance
            :rtype: Instance
        """
        LOGGER.debug("Returning shared database connection")
        return BaseSliceOfLifeApiResponse.dbinstance

    @property
    def cdn_session(self):
        """
            returns a reference to the api's shared cdn session, creates it if it does not exist
            :returns: shared cdn session
            :rtype: SpaceIndex
        """
        if not BaseSliceOfLifeApiResponse.blobinstance.has_active_session():
            LOGGER.debug("Creating single CDN session")
            BaseSliceOfLifeApiResponse.blobinstance.create_session()

        LOGGER.debug("Returning shared cdn session")
        return BaseSliceOfLifeApiResponse.blobinstance

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
            except SliceOfLifeAPIException as exc:
                LOGGER.error("Error occurred during execution: %s", str(exc))
                return ("Internal Server Error", 500)

        return wrapper
