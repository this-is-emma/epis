"""Initialize Config class to access environment variables."""
from dotenv import load_dotenv
import os

load_dotenv()

class Config(object):
    """Set environment variables."""

    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_PHOTOS_DEST = 'foundation_app/static/uploads'
