"""
Vercel serverless function entry point for FastAPI backend.
"""
from fastapi import FastAPI
from mangum import Mangum
import sys
from pathlib import Path

# Add parent directory to path to import app modules
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.main import app

# Wrap FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")
