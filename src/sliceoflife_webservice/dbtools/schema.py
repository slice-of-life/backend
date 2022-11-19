"""
    :module_name: schema
    :module_summary: dataclass definitions for Slice Of Life data schema
    :module_author: Nathan Mendoza (nathancm@uci.edu)
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """
        A dataclass that represents a row in the Users table
    """
    handle: str
    password_hash: str
    salt: str
    first_name: str
    last_name: str
    profile_pic: str

@dataclass
class Task:
    """
        A dataclass that represents a row in the Tasks table
    """
    task_id: int
    title: str
    description: str
    active: bool

@dataclass
class Post:
    """
        A dataclass that represents a row in the Posts table
    """
    post_id: int
    free_text: Optional[str]
    image: str
    created_at: datetime
    posted_by: User
    completes: Task

@dataclass
class Reaction:
    """
        A dataclass that represents a row in the Reactions table
    """
    reaction_id: int
    react_to: Post
    react_by: User

@dataclass
class Completion:
    """
        A dataclass that represents a row in the Completes table
    """
    completed_by: User
    completed_task: Task

@dataclass
class Comment:
    """
        A dataclass that represents a row in the Comments table
    """
    comment_id: int
    free_text: str
    comment_on: Post
    comment_by: User
    parent: Optional[Comment]
