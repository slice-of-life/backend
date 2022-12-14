"""
    module_name: statement
    module_summary: class that provides a convenient way to pass parameters to SQL statements
    module_auther: Nathan Mendoza (nathancm@uci.edu)
"""

class PreparedStatement:
    """
        A class that provides a convenient way to pass parameters to SQL statements
    """

    def __init__(self, sql, **params):
        self._sql = sql
        self._params = params

    @property
    def statement(self):
        """
            Return the sql statement
            :returns: statement
            :rtype: str or sql.SQL
        """
        return self._sql

    @property
    def parameters(self) -> dict:
        """
            Return the prepared statement's paremeters
            :returns: paramters
            :rtype: dict
        """
        return self._params
