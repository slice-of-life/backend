"""
    :module_name: templates
    :module_summary: functions that generate templated sql statements
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging

from psycopg2 import sql

from ..schema import User, Post, Completion
from .statement import PreparedStatement


LOGGER = logging.getLogger('gunicorn.error')

def paginated_posts(page_size: int, page_offset: int = 0) -> PreparedStatement:
    """
        SQL query that selects the most recent posts up to a size of `page_size`
        :arg page_size: the size of the result set to ask for
        :arg page_offset: the start of the next page to ask for (defaults to 0)
        :returns: A templetate SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                      SELECT *
                      FROM POSTS p
                      ORDER BY p.created_at DESC
                      LIMIT {limit} OFFSET {offset}
                      """).format(
        limit=sql.Placeholder("limit"),
        offset=sql.Placeholder("offset")
    )
    parameters = {
        'limit': page_size,
        'offset': page_offset
    }
    return PreparedStatement(statement, **parameters)

def specific_user(user_handle: str) -> PreparedStatement:
    """
        SQL query that selects a specific user by their handle
        :arg user_handle: the handle to query for:
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM USERS u
                    WHERE u.handle = {handle}
                   """).format(
                    handle=sql.Placeholder("handle")
                   )
    parameters = {
        'handle': user_handle
    }
    return PreparedStatement(statement, **parameters)

def specific_task(task_id: int) -> PreparedStatement:
    """
        SQL query that selects a specific task by its ID
        :arg task_id: the task to query for
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM TASKS t
                    WHERE t.task_id = {task}
    """).format(
        task = sql.Placeholder("taskid")
    )
    parameters = {
        'taskid': task_id
    }
    return PreparedStatement(statement, **parameters)

def specific_post(post_id: int) -> PreparedStatement:
    """
        SQL query that selects a specific post by the given id
        :arg post_id: the id to query for
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM Posts p
                    WHERE p.post_id = {post}
    """).format(
        post=sql.Placeholder("postid")
    )
    parameters = {
        'postid': post_id
    }
    return PreparedStatement(statement, **parameters)

def top_level_comments(post_id: int) -> PreparedStatement:
    """
        SQL query that selects the comments for a post that have no parent comment
        :arg post_id: the post id to gather comments for
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM Comments c
                    WHERE c.comment_to = {post}
                    AND c.parent is NULL
                    ORDER BY c.created_at ASC
    """).format(
        post=sql.Placeholder('postid')
    )
    parameters = {
        'postid': post_id
    }
    return PreparedStatement(statement, **parameters)

def comments_responding_to(post_id: int, parent_comment_id: int) -> PreparedStatement:
    """
        SQL query that selects the comments that respond to a parent comment for a particular post
        :arg post_id: the post id to gather comments for
        :arg parent_comment_id: the comment id the gathered comments should have a s parrent
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM Comments c
                    WHERE c.comment_to = {postid}
                    AND c.parent = {commentid}
                    ORDER BY c.created_at ASC
    """).format(
        postid=sql.Placeholder('postid'),
        commentid=sql.Placeholder('commentid')
    )
    parameters = {
        'postid': post_id,
        'commentid': parent_comment_id
    }
    return PreparedStatement(statement, **parameters)

def reactions_by_group(post_id: int) -> PreparedStatement:
    """
        SQL query the selects that groups the reactions that have occured on a post
        :arg post_id: the post id to gather reactions for
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT DISTINCT ON (emoji) *
                    FROM Reactions r
                    WHERE r.reacted_to = {postid}
    """).format(
        postid=sql.Placeholder('postid')
    )
    parameters = {
        'postid': post_id
    }
    return PreparedStatement(statement, **parameters)

def reaction_counts(emoji_code: str, post_id: int) -> PreparedStatement:
    """
        SQL query that counts the number of times a certain reaction occurred on a given post
        :arg emoji_code: the unicode text representing the emoji for this reaction
        :arg post_id: the post the reaction occurrs on
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT COUNT(*)
                    FROM Reactions r
                    WHERE r.reacted_to = {postid}
                    AND r.emoji = {code}
    """).format(
        postid=sql.Placeholder('postid'),
        code=sql.Placeholder('code')
    )
    parameters = {
        'postid': post_id,
        'code': emoji_code
    }
    return PreparedStatement(statement, **parameters)

def reactors_by_emoji(emoji_code: str, post_id: int) -> PreparedStatement:
    """
        SQL query that gathers the handles of users that used a particular emoji for a given post
        :arg emoji_code: the unicode text representing the emoji for this reaction
        :arg post_id: the post these reactions occurr on
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT r.reacted_by
                    FROM Reactions r
                    WHERE r.reacted_to = {postid}
                    AND r.emoji = {code}
    """).format(
        postid=sql.Placeholder('postid'),
        code=sql.Placeholder('code')
    )
    parameters = {
        'postid': post_id,
        'code': emoji_code
    }
    return PreparedStatement(statement, **parameters)

def insert_user_account(new_user: User) -> PreparedStatement:
    """
        SQL query that inserts the given user object into the database
        :arg new_user: the user being added
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    INSERT INTO Users VALUES
                    ({handle}, {password}, {email}, {salt}, {first}, {last}, {avatar})
    """).format(
        handle=sql.Placeholder('handle'),
        password=sql.Placeholder('password'),
        email=sql.Placeholder('email'),
        salt=sql.Placeholder('salt'),
        first=sql.Placeholder('first'),
        last=sql.Placeholder('last'),
        avatar=sql.Placeholder('avatar')
    )
    parameters = {
        'handle': new_user.handle,
        'password': new_user.password_hash,
        'email': new_user.email,
        'salt': new_user.salt,
        'first': new_user.first_name,
        'last': new_user.last_name,
        'avatar': new_user.profile_pic
    }
    return PreparedStatement(statement, **parameters)

def insert_post(new_post: Post) -> PreparedStatement:
    """
        SQL query that inserts the given post object into the database
        :arg new_post: the post being added
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    INSERT INTO Posts VALUES
                    (DEFAULT, {free_text}, {image_url}, {created_at}, {post_author}, {task_completed})
    """).format(
        free_text=sql.Placeholder('freetext'),
        image_url=sql.Placeholder('image'),
        created_at=sql.Placeholder('date'),
        post_author=sql.Placeholder('author'),
        task_completed=sql.Placeholder('completes')
    )
    parameters = {
        'freetext': new_post.free_text,
        'image': new_post.image,
        'date': new_post.created_at,
        'author': new_post.posted_by,
        'completes': new_post.completes
    }
    return PreparedStatement(statement, **parameters)

def insert_completion(new_completion: Completion) -> PreparedStatement:
    """
        SQL query that inserts the given completion object into the database
        :arg new_completion: the completion being marked
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    INSERT INTO Completes VALUES
                    ({user}, {task})
    """).format(
        user=sql.Placeholder('user'),
        task=sql.Placeholder('task')
    )
    parameters = {
        'user': new_completion.completed_by,
        'task': new_completion.completed_task
    }
    return PreparedStatement(statement, **parameters)

def available_tasks(user_handle: str) -> PreparedStatement:
    """
        SQL query that gathers the tasks a given user can complete
        :arg user_handle: the user to gather available tasks for
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM Tasks t
                    WHERE t.task_id NOT IN (
                        SELECT completed_task
                        FROM Completes c
                        WHERE c.completed_by = {handle}
                    )
    """).format(
        handle=sql.Placeholder('handle')
    )
    parameters = {
        'handle': user_handle
    }
    return PreparedStatement(statement, **parameters)

def completed_tasks(user_handle: str) -> PreparedStatement:
    """
        SQL query that gathers the tasks a given user has completed
        :arg user_handle: the user to gather completed tasks for
        :returns: A templated SQL statement
        :rtype: PreparedStatement
    """
    statement = sql.SQL("""
                    SELECT *
                    FROM Tasks t
                    WHERE t.task_id IN (
                        SELECT completed_task
                        FROM Completes c
                        WHERE c.completed_by = {handle}
                    )
    """).format(
        handle=sql.Placeholder('handle')
    )
    parameters = {
        'handle': user_handle
    }
    return PreparedStatement(statement, **parameters)
