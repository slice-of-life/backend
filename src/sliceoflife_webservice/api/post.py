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

from flask import request

from . import BaseSliceOfLifeApiResponse
from ..exceptions import AuthorizationError
from ..dbtools import Instance
from ..dbtools.queries import specific_user, insert_user_account, \
                              insert_post, insert_completion
from ..dbtools.schema import interpret_as, User, Post, Completion

LOGGER = logging.getLogger('gunicorn.error')

class SliceOfLifeApiPostResponse(BaseSliceOfLifeApiResponse):
    """
        A subclass of BaseSliceOfLifeApiResponse for specifically responding to POST requests
    """

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def create_user(self):
        """
            Creates a new user account for the slice of life application
        """
        form_data = {
            'handle': request.form['handle'],
            'email': request.form['email'],
            'password': request.form['password'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
        }
        with self.instance.start_transaction() as self._conn:
            if self._handle_is_available(form_data['handle']):
                self._make_user_account(form_data)
                return f"CREATED {form_data['handle']}"
            raise AuthorizationError(f"{form_data['handle']} is not available")

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def authenticate_user(self) -> dict:
        """
            Logs the user in. On successful return a auth token to the client
            :returns: auth token
            :rtype: dict
        """
        form_data = {
            'handle': request.form['handle'],
            'password': request.form['password']
        }

        with self.instance.start_transaction() as self._conn:
            try:
                expected_uinfo = interpret_as(
                    User,
                    Instance.query(self._conn, specific_user(form_data['handle']))[0]
                )
            except IndexError as exc:
                raise AuthorizationError(f"No user with handle {form_data['handle']}") from exc
            else:
                if self._credentials_are_valid(form_data, expected_uinfo):
                    return {'token': self.create_auth_token(form_data['handle'])}
                raise AuthorizationError("Incorrect handle or password")

    def create_new_post(self) -> str:
        """
            Create a new post. On success, return the message "CREATED"
            :returns: success message
            :rtype: str
        """
        post_data = {
            'author': request.form['handle'],
            'slice_image': request.files['slice_image'],
            'free_text': request.form['free_text'],
            'task_id': request.form['task_id']
        }
        with self.instance.start_transaction() as self._conn:
            if self.verify_auth_token(post_data['author']):
                self._insert_post_record(post_data)
                return "CREATED"
            raise AuthorizationError(f"{post_data['author']} is not authorized to make a post")

    def _handle_is_available(self, handle) -> bool:
        return not Instance.query(self._conn, specific_user(handle))

    def _make_user_account(self, account_info) -> None:
        user_salt = secrets.token_hex()
        user_hash = hashlib.sha256(f"{account_info['password']}{user_salt}".encode()).hexdigest()
        new_user = User(
            handle=account_info['handle'],
            password_hash=user_hash,
            email=account_info['email'],
            salt=user_salt,
            first_name=account_info['first_name'],
            last_name=account_info['last_name'],
            profile_pic='unknown.jpg'
        )
        Instance.query_no_fetch(self._conn, insert_user_account(new_user))

    def _credentials_are_valid(self, given: dict, expected: User) -> bool:
        return secrets.compare_digest(
            hashlib.sha256(f"{given['password']}{expected.salt}".encode()).hexdigest(),
            expected.password_hash
        )

    def _insert_post_record(self, post_info) -> None:
        new_post = Post(
            post_id=None,
            free_text=post_info['free_text'],
            image=self._save_post_data(post_info),
            created_at=datetime.datetime.utcnow(),
            posted_by=post_info['author'],
            completes=post_info['task_id']
        )

        new_completion = Completion(
            completed_by=post_info['author'],
            completed_task=post_info['task_id']
        )

        Instance.query_no_fetch(self._conn, insert_post(new_post))
        Instance.query_no_fetch(self._conn, insert_completion(new_completion))

    def _save_post_data(self, post_data) -> str:
        file_location = f"posts/{post_data['author']}" \
                        + f"/task{post_data['task_id']}" \
                        + f"{pathlib.Path(post_data['slice_image'].filename).suffix}"
        self.spaces.save_file(
            file_location,
            post_data['slice_image']
        )
        return file_location
