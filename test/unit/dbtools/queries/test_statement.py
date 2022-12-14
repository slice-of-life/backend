"""
    module_name: test_statement
    module_summary: tests for the PreparedStatement class
    module_author: Nathan Mendoza (nathacm@uci.edu)
"""

from sliceoflife_webservice.dbtools.queries.statement import PreparedStatement

def test_prepared_statement_creation_with_parmeters():
    """Test prepared statement creation"""
    pstmt = PreparedStatement(sql = "SELECT %(n)s", n = 1)
    assert pstmt.statement == "SELECT %(n)s"
    assert pstmt.parameters == {'n': 1}

def test_prepared_statement_creation_without_parmeters():
    """Test prepared statement creation"""
    pstmt = PreparedStatement(sql = 'SELECT 1')
    assert pstmt.statement == 'SELECT 1'
    assert pstmt.parameters == {}
