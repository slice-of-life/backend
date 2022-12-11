"""
    :module_name: get
    :module_summary: response class that defines the GET methods for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os
from dataclasses import asdict

from . import BaseSliceOfLifeApiResponse

from ..dbtools.queries import paginated_posts, specific_user, \
                              specific_task, specific_post, \
                              top_level_comments, comments_responding_to, \
                              reactions_by_group, reaction_counts, reactors_by_emoji, \
                              available_tasks, completed_tasks
from ..dbtools.schema import interpret_as, Post, User, Task, Comment, Reaction

from ..exceptions import ContentNotFoundError

LOGGER = logging.getLogger('gunicorn.error')

class SliceOfLifeApiGetResponse(BaseSliceOfLifeApiResponse):
    """
        A subclass of SliceOfLifeApiResponse for specifically responding to GET request
    """
    base_url = os.getenv('BASE_URL')

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def hello(self) -> dict:
        """
            A simple GET API route that introduces the Slice Of Life API
            :returns: A static JSON response
            :rtype: dict
        """
        response = {
            'msg': 'Welcome to the first endpoint of the slice of life api'
        }
        return response

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def get_latest_posts(self, limit: int, offset: int) -> dict:
        """
            A GET route that returns the most recently posted slices of life. Pages results
            :arg limit: the size of the page of results
            :arg offset: the location where to start the next page of results.
            :returns: a JSON object of posts and their associated information
            :rtype: dict
        """
        with self.db_connection:
            query = paginated_posts(limit, offset)
            results = self.db_connection.query(query)
            results = [interpret_as(Post, r) for r in results]
            for res in results:
                if not isinstance(res.posted_by, User):
                    res.posted_by = self._get_basic_post_author_info(res.posted_by)
                if not isinstance(res.completes, Task):
                    res.completes = self._get_task_info(res.completes)
                res.image = self.cdn_session.get_share_link(res.image)
            return {
                "page": results,
                "next":
                f"{self.base_url}/api/v1/slices/latest?limit={limit}&offset={offset + len(results)}"
            }

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def get_slice_by_id(self, slice_id: int) -> Post:
        """
            A GET method that returns the slice corresponding to the given ID, if it exists
            :arg slice_id: The ID post to retrieve
            :returns: the corresponding post, it it exists
            :rtype: Post
            :throws SliceOfLifeAPIException: when result size is not expected (1 excactly)
        """
        with self.db_connection:
            pinfo = self._get_post_information(slice_id)
            if not isinstance(pinfo.posted_by, User):
                pinfo.posted_by = self._get_basic_post_author_info(pinfo.posted_by)
            if not isinstance(pinfo.completes, Task):
                pinfo.completes = self._get_task_info(pinfo.completes)
            pinfo.image = self.cdn_session.get_share_link(pinfo.image)
            return pinfo

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def get_comments_for_slice(self, slice_id: int) -> dict:
        """
            A Get method that return the comments associated with a given post id, if it exists
            :arg slice_id: The ID post to retrieve comments for
            :returns: the associated comments (threads included)
            :rtype: dict
            :throws: SliceOfLifeAPIException: the post ID invalid
        """
        with self.db_connection:
            pinfo = self._get_post_information(slice_id)

            return self._build_comment_tree_for_slice(pinfo.post_id)

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def get_reactions_for_slice(self, slice_id: int) -> list:
        """
            A get method that returns the information on the reactions for a given post
            :arg slice_id: the slice id to get reactions for
            :returns: a list of each reaction and the number of times it occurs
            :rtype list:
            :throws SliceOfLifeAPIException: if the slice does not exist
        """
        with self.db_connection:
            self._get_post_information(slice_id) # test for existing slice id
            return [
                {
                    "reaction": r.emoji_code,
                    "count": self._reaction_occurences(r.emoji_code, slice_id),
                    "reactors": self._reactors_for_slice(r.emoji_code, slice_id)
                } for r in self._reactions_for_slice(slice_id)
            ]

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def get_user_profile(self, handle) -> User:
        """
            A get method that returns basic user information. Must be authorized to view
            :arg handle: the handle of the user to obtain profile info on
            :returns: basic user information
            :rtype: User
        """
        with self.db_connection:
            return self._get_basic_post_author_info(handle)

    @BaseSliceOfLifeApiResponse.safe_api_callback
    def get_user_tasklist(self, handle) -> dict:
        """
            A get method that a collection of tasks a user has completed and has not completed
            :arg handle: the handle of the user to obtain the task list for
            :returns: task information
            :rtype: dict
        """
        with self.db_connection:
            return {
                "completed": self._get_users_completed_tasks(handle),
                "available": self._get_users_available_tasks(handle)
            }

    def _get_post_information(self, post_id: int) -> Post:
        result = self.db_connection.query(specific_post(post_id))
        if len(result) != 1:
            raise ContentNotFoundError(f"Expected a single result, got {len(result)}")

        return interpret_as(Post, result[0]) # should be one anyway


    def _get_basic_post_author_info(self, author_handle: str) -> User:
        query = specific_user(author_handle)
        uinfo = interpret_as(User, self.db_connection.query(query)[0]) #should only be one anyway
        # hide sensitive information
        uinfo.password_hash = "***"
        uinfo.salt = "***"
        uinfo.email = "***"
        # get profile pic
        uinfo.profile_pic = self.cdn_session.get_share_link(uinfo.profile_pic)
        return uinfo

    def _get_task_info(self, task_id: int) -> Task:
        query = specific_task(task_id)
        tinfo = interpret_as(Task, self.db_connection.query(query)[0]) #should only be one anyway
        return tinfo

    def _build_comment_tree_for_slice(self, slice_id: int) -> dict:
        tree = {"threads": self._orphaned_comments(slice_id)}
        for thread in tree["threads"]:
            self._get_responses(thread, slice_id)
        return tree

    def _orphaned_comments(self, slice_id: int) -> list:
        return [
                {
                    "comment": self._comment_with_author(c),
                    "responses": []
                } for c in self.db_connection.query(top_level_comments(slice_id))
        ]

    def _non_orphaned_comments(self, slice_id: int, parent_comment_id: int) -> list:
        return [
            {
                "comment": self._comment_with_author(c),
                "responses": []
            } for c in self.db_connection.query(comments_responding_to(slice_id, parent_comment_id))
        ]

    def _get_responses(self, thread, slice_id) -> None:
        thread['responses'].extend(
            self._non_orphaned_comments(slice_id, thread["comment"].comment_id)
        )
        for subthread in thread['responses']:
            self._get_responses(subthread, slice_id)

    def _comment_with_author(self, comment_data) -> dict:
        comment_instance = interpret_as(Comment, comment_data)
        comment_instance.comment_by = self._get_basic_post_author_info(comment_instance.comment_by)
        return comment_instance

    def _reactions_for_slice(self, slice_id: int) -> [Reaction]:
        return [
            interpret_as(Reaction, r)
            for r in self.db_connection.query(
                reactions_by_group(slice_id)
            )
        ]

    def _reaction_occurences(self, emoji_used: str, post_id: int) -> int:
        return self.db_connection.query(reaction_counts(emoji_used, post_id))[0][0]

    def _reactors_for_slice(self, emoji_used: str, post_id: int) -> [str]:
        return [
            reactor[0] for reactor in self.db_connection.query(
                reactors_by_emoji(emoji_used, post_id)
            )
        ]

    def _get_users_available_tasks(self, user_handle: str) -> [Task]:
        return [
            interpret_as(Task, t) for t in self.db_connection.query(available_tasks(user_handle))
        ]

    def _get_users_completed_tasks(self, user_handle) -> [Task]:
        return [
            interpret_as(Task, t) for t in self.db_connection.query(completed_tasks(user_handle))
        ]
