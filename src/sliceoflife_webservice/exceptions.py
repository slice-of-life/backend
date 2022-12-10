"""
    :module_name: exceptions
    :module_summary: exception classes for the sliceoflife API
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

class SliceOfLifeAPIException(Exception):
    """
        Exception thrown when an API request cannot be completed succesfully
    """

class ContentNotFoundError(SliceOfLifeAPIException):
    """
        Exception thrown when an API request cannot find the data it expects
    """

class AuthorizationError(SliceOfLifeAPIException):
    """
        Exception thrown when an API request fails due to insufficient permissions
    """

class DuplicateHandleError(AuthorizationError):
    """
        Exception thrown when an API request discovers duplicate handles
    """

class NoSuchUserError(AuthorizationError):
    """
        Exception thrwon when an API request cannot verify a user exists
    """

class MismatchedCredentialsError(AuthorizationError):
    """
        Exception thrown when an API request fails to authenticate a user
    """

class ServiceNotReachable(SliceOfLifeAPIException):
    """
        Exception thrown when an API request fails becuase an external service is unreachable
    """
