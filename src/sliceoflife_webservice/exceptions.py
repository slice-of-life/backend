"""
    :module_name: exceptions
    :module_summary: exception classes for the sliceoflife API
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

class SliceOfLifeBaseException(BaseException):
    """
        Base exception class for all Slice Of Life API related exceptions
    """

class DatabaseNotConnectedError(SliceOfLifeBaseException):
    """
        Connection thrown if a sql query is attempted when the API has no active database connection
    """

class SliceOfLifeAPIException(SliceOfLifeBaseException):
    """
        Exception thrown when an API request cannot be completed succesfully
    """

class ContentNotRetrievableError(SliceOfLifeBaseException):
    """
        Exception thrown when the CDN cannot be reached
    """

class DuplicateHandleError(SliceOfLifeBaseException):
    """
        Exception thrown when a user is attempted to be created with a handle already in use
    """

class NoSuchUserError(SliceOfLifeAPIException):
    """
        Exception thrown when authentication is attempted with a nonexistent handle
    """

class InvalidCredentialsError(SliceOfLifeAPIException):
    """
        Exception thrown whan authenticating with invalid credentials
    """

class NotAuthorizedError(SliceOfLifeAPIException):
    """
        Exception thown when a user is not authorized to perform an action
    """
