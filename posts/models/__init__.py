"""
Posts models package.

Expõe os models Post, Comment e Like.
"""
from .post import Post
from .comment import Comment
from .like import Like

__all__ = ['Post', 'Comment', 'Like']
