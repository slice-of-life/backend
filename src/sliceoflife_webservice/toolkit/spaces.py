"""
    :module_name: spaces
    :module_summary: object that interfaces witht the sliceoflife CDN
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
import pathlib

import boto3

from ..exceptions import ContentNotRetrievableError

LOGGER = logging.getLogger('gunicorn.error')

class SpaceIndex:
    """
        Class that can communicate and accomplish tasks with CDN APIs
    """
    SPACES_BUCKET="blob-sliceoflife"
    SPACES_SHARE_TIME=300

    def __init__(self, **config):
        self._region = config.get("SPACES_REGION", os.getenv("SPACES_REGION"))
        self._endpoint = config.get("SPACES_ENDPOINT", os.getenv("SPACES_ENDPOINT"))
        self._access_key = config.get("SPACES_KEY", os.getenv("SPACES_KEY"))
        self._access_secret = config.get("SPACES_SECRET", os.getenv("SPACES_SECRET"))
        self._session = None

    def create_session(self) -> None:
        """
            Creates a new session with the sliceoflife CDN
        """
        self._session = boto3.session.Session().client(
            's3',
            endpoint_url=self._endpoint,
            region_name=self._region,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._access_secret
        )
        LOGGER.info("New space index session to %s", self._endpoint)

    def has_active_session(self) -> bool:
        """
            Returns true if this space index has an active session, otherwise false
        """
        return bool(self._session)

    def get_share_link(self, path_to_file: str) -> str:
        """
            get a sharable link to the given file path
            :arg path_to_file: the file to generate a share link for
            :returns: sharelink
            :rtype: str
            :throws: ContentNotRetrievableError if no sesssion is active
        """

        if not self._session:
            raise ContentNotRetrievableError("No session exists to interact with application CDN")

        LOGGER.info("Generating share link for file: %s", path_to_file)
        return self._session.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.SPACES_BUCKET,
                'Key': path_to_file
            },
            ExpiresIn=self.SPACES_SHARE_TIME
        )

    def save_file(self, save_as: str, file_to_save) -> None:
        """
            save the given file under the given name
            :arg save_as: filename to use
            :arg file_to_save: file-like object to save
            :returns: nothing
            :rtype: NoneType
            :throws: ContentNotRetrievableError if no session is active
        """

        if not self._session:
            raise ContentNotRetrievableError("no session exists to interact with application CDN")

        LOGGER.debug("Received the file: %s", file_to_save.filename)
        LOGGER.debug("Saving the file as: %s", save_as)
        self._session.put_object(
            Bucket=self.SPACES_BUCKET,
            Key=save_as,
            Body=file_to_save,
            ACL='private',
            ContentType='image/*'
        )
