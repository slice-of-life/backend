"""
    :module_name: post
    :module_summary: response class that define POST endpoints for the slice of life API
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import pathlib
import hashlib
import secrets
import datetime

from . import BaseSliceOfLifeApiResponse
from ..exceptions import AuthorizationError
from ..dbtools.queries import specific_user, insert_user_account, \
                              insert_post, insert_completion
from ..dbtools.schema import interpret_as, User, Post, Completion

LOGGER = logging.getLogger('gunicorn.error')

class SliceOfLifeApiPostResponse(BaseSliceOfLifeApiResponse):
    """
        A subclass of BaseSliceOfLifeApiResponse for specifically responding to POST requests
    """

    def __init__(self, **request_data):
        self._data = request_data

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def create_user(self):
        """
            Creates a new user account for the slice of life application
        """
        with self.db_connection:
            if self._handle_is_available():
                self._make_user_account()
                return f"CREATED {self._data['handle']}"
            raise AuthorizationError(f"{self._data['handle']} is not available")

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def authenticate_user(self) -> str:
        """
            Logs the user in. On successful return a auth token to the client
            :returns: auth token
            :rtype: str
        """
        with self.db_connection:
            try:
                expected_uinfo = interpret_as(
                    User,
                    self.db_connection.query(specific_user(self._data['handle']))[0]
                )
                if self._credentials_are_valid(expected_uinfo):
                    return self._generate_auth_token()
                raise AuthorizationError("Incorrect handle or password")
            except IndexError as exc:
                raise AuthorizationError(f"No user with handle {self._data['handle']}") from exc

    def create_new_post(self) -> dict:
        """
            Create a new post. On success, return the saved data
            :returns: post data
            :rtype: dict
        """
        with self.db_connection:
            if secrets.compare_digest(self._data['token'], self._data['expected']):
                self._insert_post_record()
                return "CREATED"
            raise NotAuthorizedError(f"{self._data['handle']} is not authorized to make a post")

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

    def _insert_post_record(self) -> None:
        new_post = Post(
            post_id=None,
            free_text=self._data['free_text'],
            image=self._save_post_data(),
            created_at=datetime.datetime.utcnow(),
            posted_by=self._data['handle'],
            completes=self._data['task_id']
        )

        new_completion = Completion(
            completed_by=self._data['handle'],
            completed_task=self._data['task_id']
        )

        self.db_connection.query_no_fetch(insert_post(new_post))
        self.db_connection.query_no_fetch(insert_completion(new_completion))

    def _save_post_data(self) -> str:
        file_location = f"posts/{self._data['handle']}" \
                        + f"/task{self._data['task_id']}" \
                        + f"{pathlib.Path(self._data['slice_image'].filename).suffix}"
        self.cdn_session.save_file(
            file_location,
            self._data['slice_image']
        )
        return file_location
