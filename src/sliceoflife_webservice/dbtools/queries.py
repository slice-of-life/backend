"""
    :module_name: queries
    :module_summary: functions that provide parametrized sql queries
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from psycopg2 import sql

LOGGER = logging.getLogger('gunicorn.error')

def paginated_posts(page_size: int, page_offset: int = 0) -> sql.SQL:
    """
        SQL query that selects the most recent posts up to a size of `page_size`
        :arg page_size: the size of the result set to ask for
        :arg page_offset: the start of the next page to ask for (defaults to 0)
        :returns: A templetate SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""SELECT *
                      FROM POSTS p
                      ORDER BY p.created_at DESC
                      LIMIT {limit} OFFSET {offset}
                      """).format(
        limit=sql.Literal(page_size),
        offset=sql.Literal(page_offset)
    )
