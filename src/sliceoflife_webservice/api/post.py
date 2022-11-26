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
from ..exceptions import DuplicateHandleError, NoSuchUserError, InvalidCredentialsError
from ..dbtools.queries import specific_user, insert_user_account
from ..dbtools.schema import interpret_as, User

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

    def authenticate_user(self) -> str:
        """
            Logs the user in. On successful return a auth token to the client
            :returns: auth token
            :rtype: str
        """
        try:
            expected_uinfo = interpret_as(
                User,
                self.db_connection.query(specific_user(self._data['handle']))[0]
            )
            if self._credentials_are_valid(expected_uinfo):
                return self._generate_auth_token()
            raise InvalidCredentialsError("Incorrect handle or password")
        except IndexError as exc:
            raise NoSuchUserError(f"No user with handle {self._data['handle']}") from exc

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

    def _credentials_are_valid(self, expected: User) -> bool:
        return secrets.compare_digest(
            hashlib.sha256(f"{self._data['password']}{expected.salt}".encode()).hexdigest(),
            expected.password_hash
        )

    def _generate_auth_token(self) -> str:
        return secrets.token_hex()
