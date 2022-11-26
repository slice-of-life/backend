"""
    :module_name: post
    :module_summary: response class that define POST endpoints for the slice of life API
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
import hashlib
import secrets

from . import BaseSliceOfLifeApiResponse
from ..exceptions import DuplicateHandleError
from ..dbtools.queries import specific_user, insert_user_account
from ..dbtools.schema import User

LOGGER = logging.getLogger('gunicorn.error')

class SliceOfLifeApiPostResponse(BaseSliceOfLifeApiResponse):
    """
        A subclass of BaseSliceOfLifeApiResponse for specifically responding to POST requests
    """

    def __init__(self, **request_data):
        self._data = request_data

    def create_user(self):
        """
            Creates a new user account for the slice of life application
        """
        if self._handle_is_available():
            self._make_user_account()
            return f"CREATED {self._data['handle']}"
        raise DuplicateHandleError(f"{self._data['handle']} is not available")

    def _handle_is_available(self) -> bool:
        return not self.db_connection.query(specific_user(self._data['handle']))

    def _make_user_account(self) -> None:
        user_salt = secrets.token_hex()
        user_hash = hashlib.sha256(f"{self._data['password']}{user_salt}".encode()).hexdigest()
        new_user = User(
            handle=self._data['handle'],
            password_hash=user_hash,
            email=self._data['email'],
            salt=user_salt,
            first_name=self._data['first_name'],
            last_name=self._data['last_name'],
            profile_pic='unknown.jpg'
        )
        self.db_connection.query_no_fetch(insert_user_account(new_user))
