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
