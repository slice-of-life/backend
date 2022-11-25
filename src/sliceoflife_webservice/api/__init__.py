"""
    :module_name: api
    :module_summary: implementation for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
from abc import ABC

from dotenv import dotenv_values

from ..dbtools import Instance
from ..toolkit import SpaceIndex

LOGGER = logging.getLogger("gunicorn.error")

class BaseSliceOfLifeApiResponse(ABC):
    """
        A base class for all slice of life API subclasses
        Has a single db and cdn connection with public references
    """
    dbinstance: Instance
    blobinstance: SpaceIndex

    @property
    def db_connection(self):
        """
            returns a reference to the api's shared db connection, creates it if is does not exist
            :returns: reference to dbinstance
            :rtype: Instance
        """
        if not BaseSliceOfLifeApiResponse.dbinstance:
            LOGGER.debug("Creating single database connection")
            BaseSliceOfLifeApiResponse.dbinstance = Instance(**dotenv_values())
            BaseSliceOfLifeApiResponse.dbinstance.connect()

        LOGGER.debug("Returning shared database connection")
        return BaseSliceOfLifeApiResponse.dbinstance

    @property
    def cdn_session(self):
        """
            returns a reference to the api's shared cdn session, creates it if it does not exist
            :returns: shared cdn session
            :rtype: SpaceIndex
        """
        if not BaseSliceOfLifeApiResponse.blobinstance:
            LOGGER.debug("Creating single cdn session")
            BaseSliceOfLifeApiResponse.blobinstance = SpaceIndex(**dotenv_values())
            BaseSliceOfLifeApiResponse.blobinstance.create_session()

        LOGGER.debug("Returning shared cdn session")
        return BaseSliceOfLifeApiResponse.blobinstance
