"""
Vercel serverless function entry point for FastAPI backend.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Set environment to production
os.environ.setdefault("ENVIRONMENT", "production")

from mangum import Mangum
from app.main import app

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")