"""
Posts models package.

Expõe os models Post, Comment e Like.
"""

from .comment import Comment
from .like import Like
from .post import Post

__all__ = ["Post", "Comment", "Like"]
