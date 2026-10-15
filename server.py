"""Vercel entrypoint; avoids app.py/app package collision."""
from app.main import app
