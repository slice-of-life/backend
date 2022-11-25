"""
    :module_name: get
    :module_summary: response class that defines the GET methods for the slice of life api
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

import logging
import os

from . import BaseSliceOfLifeApiResponse

from ..dbtools.queries import paginated_posts, specific_user, \
                              specific_task, specific_post, \
                              top_level_comments, comments_responding_to, \
                              reactions_by_group, reaction_counts, reactors_by_emoji
from ..dbtools.schema import interpret_as, Post, User, Task, Comment, Reaction

from ..exceptions import SliceOfLifeAPIException

LOGGER = logging.getLogger('gunicorn.error')

class SliceOfLifeApiGetResponse(BaseSliceOfLifeApiResponse):
    """
        A subclass of SliceOfLifeApiResponse for specifically responding to GET request
    """

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

    def get_latest_posts(self, limit: int, offset: int) -> dict:
        """
            A GET route that returns the most recently posted slices of life. Pages results
            :arg limit: the size of the page of results
            :arg offset: the location where to start the next page of results.
            :returns: a JSON object of posts and their associated information
            :rtype: dict
        """
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
            "next": f"{os.getenv('BASE_URL')}/api/v1/slices/latest?limit={limit}&offset={offset + len(results)}"
        }

    def get_slice_by_id(self, slice_id: int) -> Post:
        """
            A GET method that returns the slice corresponding to the given ID, if it exists
            :arg slice_id: The ID post to retrieve
            :returns: the corresponding post, it it exists
            :rtype: Post
            :throws SliceOfLifeAPIException: when result size is not expected (1 excactly)
        """
        result = self.db_connection.query(specific_post(slice_id))
        if len(result) != 1:
            raise SliceOfLifeAPIException(f"Expected a single result, got {len(result)}")

        pinfo = interpret_as(Post, result[0]) #should only be one anyway
        if not isinstance(pinfo.posted_by, User):
            pinfo.posted_by = self._get_basic_post_author_info(pinfo.posted_by)
        if not isinstance(pinfo.completes, Task):
            pinfo.completes = self._get_task_info(pinfo.completes)
        pinfo.image = self.cdn_session.get_share_link(pinfo.image)
        return pinfo

    def get_comments_for_slice(self, slice_id: int) -> dict:
        """
            A Get method that return the comments associated with a given post id, if it exists
            :arg slice_id: The ID post to retrieve comments for
            :returns: the associated comments (threads included)
            :rtype: dict
            :throws: SliceOfLifeAPIException: the post ID invalid
        """
        pinfo = self.get_slice_by_id(slice_id)

        return self._build_comment_tree_for_slice(pinfo.post_id)

    def get_reactions_for_slice(self, slice_id: int) -> list:
        """
            A get method that returns the information on the reactions for a given post
            :arg slice_id: the slice id to get reactions for
            :returns: a list of each reaction and the number of times it occurs
            :rtype list:
            :throws SliceOfLifeAPIException: if the slice does not exist
        """
        self.get_slice_by_id(slice_id) # test for existing slice id
        return [
            {
                "reaction": r.emoji_code,
                "count": self._reaction_occurences(r.emoji_code, slice_id),
                "reactors": self._reactors_for_slice(r.emoji_code, slice_id)
            } for r in self._reactions_for_slice(slice_id)
        ]

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
                    "comment": interpret_as(Comment, c),
                    "responses": []
                } for c in self.db_connection.query(top_level_comments(slice_id))
        ]

    def _non_orphaned_comments(self, slice_id: int, parent_comment_id: int) -> list:
        return [
            {
                "comment": interpret_as(Comment, c),
                "responses": []
            } for c in self.db_connection.query(comments_responding_to(slice_id, parent_comment_id))
        ]

    def _get_responses(self, thread, slice_id) -> None:
        thread['responses'].extend(
            self._non_orphaned_comments(slice_id, thread["comment"].comment_id)
        )
        for subthread in thread['responses']:
            self._get_responses(subthread, slice_id)

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
            reactor[0] for reactor in self.dbinstance.query(reactors_by_emoji(emoji_used, post_id))
        ]
