"""
Users models package.

Expõe os models User e Follow para serem importados facilmente.
"""

from .follow import Follow
from .user import User

__all__ = ["User", "Follow"]
