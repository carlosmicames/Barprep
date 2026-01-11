"""
Pydantic schemas package initialization.
Exports all schemas from schemas.py.
"""

# Import everything from schemas.py using wildcard
from app.schemas.schemas import *

# Also explicitly import DifficultyEnum from models
from app.models.models import DifficultyEnum

# Everything from schemas.py is now available when importing from app.schemas