"""
API package initialization.
Exports all routers for import in main.py.
"""

# This file makes app/api a Python package
# and allows imports like: from app.api import public, quiz, progress, essays, admin

__all__ = ["public", "quiz", "progress", "essays", "admin"]