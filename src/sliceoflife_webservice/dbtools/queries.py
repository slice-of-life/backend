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
    return sql.SQL("""
                      SELECT *
                      FROM POSTS p
                      ORDER BY p.created_at DESC
                      LIMIT {limit} OFFSET {offset}
                      """).format(
        limit=sql.Literal(page_size),
        offset=sql.Literal(page_offset)
    )

def specific_user(user_handle: str) -> sql.SQL:
    """
        SQL query that selects a specific user by their handle
        :arg user_handle: the handle to query for:
        :returns: A templated SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""
                    SELECT *
                    FROM USERS u
                    WHERE u.handle = {handle}
                   """).format(
                    handle=sql.Literal(user_handle)
                   )

def specific_task(task_id: int) -> sql.SQL:
    """
        SQL query that selects a specific task by its ID
        :arg task_id: the task to query for
        :returns: A templated SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""
                    SELECT *
                    FROM TASKS t
                    WHERE t.task_id = {id}
    """).format(
        id = sql.Literal(task_id)
    )

def specific_post(post_id: int) -> sql.SQL:
    """
        SQL query that selects a specific post by the given id
        :arg post_id: the id to query for
        :returns: A templated SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""
                    SELECT *
                    FROM Posts p
                    WHERE p.post_id = {id}
    """).format(
        id=sql.Literal(post_id)
    )

def top_level_comments(post_id: int) -> sql.SQL:
    """
        SQL query that selects the comments for a post that have no parent comment
        :arg post_id: the post id to gather comments for
        :returns: A templated SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""
                    SELECT *
                    FROM Comments c
                    WHERE c.comment_to = {id}
                    AND c.parent is NULL
                    ORDER BY c.created_at ASC
    """).format(
        id=sql.Literal(post_id)
    )

def comments_responding_to(post_id: int, parent_comment_id: int) -> sql.SQL:
    """
        SQL query that selects the comments that respond to a particular comment for a particular post
        :arg post_id: the post id to gather comments for
        :arg parent_comment_id: the comment id the gathered comments should have a s parrent
        :returns: A templated SQL statement
        :rtype sql.SQL:
    """
    return sql.SQL("""
                    SELECT *
                    FROM Comments c
                    WHERE c.comment_to = {post_id}
                    AND c.parent = {comment_id}
                    ORDER BY c.created_at ASC
    """).format(
        post_id=sql.Literal(post_id),
        comment_id=sql.Literal(parent_comment_id)
    )

def reactions_by_group(post_id: int) -> sql.SQL:
    """
        SQL query the selects that groups the reactions that have occured on a post
        :arg post_id: the post id to gather reactions for
        :returns: A templated SQL statement
        :rtype sql.SQL:
    """
    return sql.SQL("""
                    SELECT DISTINCT ON (emoji) *
                    FROM Reactions r
                    WHERE r.reacted_to = {id}
    """).format(
        id=sql.Literal(post_id)
    )

def reaction_counts(emoji_code: str, post_id: int) -> sql.SQL:
    """
        SQL query that counts the number of times a certain reaction occurred on a given post
        :arg emoji_code: the unicode text representing the emoji for this reaction
        :arg post_id: the post the reaction occurrs on
        :returns: A templated SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""
                    SELECT COUNT(*)
                    FROM Reactions r
                    WHERE r.reacted_to = {id}
                    AND r.emoji = {code}
    """).format(
        id=sql.Literal(post_id),
        code=sql.Literal(emoji_code)
    )

def reactors_by_emoji(emoji_code: str, post_id: int) -> sql.SQL:
    """
        SQL query that gathers the handles of users that used a particular emoji for a given post
        :arg emoji_code: the unicode text representing the emoji for this reaction
        :arg post_id: the post these reactions occurr on
        :returns: A templated SQL statement
        :rtype: sql.SQL
    """
    return sql.SQL("""
                    SELECT r.reacted_by
                    FROM Reactions r
                    WHERE r.reacted_to = {id}
                    AND r.emoji = {code}
    """).format(
        id =sql.Literal(post_id),
        code=sql.Literal(emoji_code)
    )
