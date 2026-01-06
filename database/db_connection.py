# database/db_connection.py
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_base_path():
    """
    Get the absolute path to the resource, works for dev and for PyInstaller.
    """
    # If the application is run as a bundle (compiled via PyInstaller),
    # the PyInstaller bootloader extends the sys module by a flag frozen=True
    # and sets the app path into variable _MEIPASS.
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # On Mac, the executable is inside the .app bundle, so we might need to adjust
        # For simplicity in this PBL, we will put the DB in the same folder as the App
        return os.path.dirname(sys.executable)
    else:
        # Running in normal Python environment
        return os.path.dirname(os.path.abspath(__file__))

# Determine the database path
BASE_DIR = get_base_path()

# Logic: Store DB in the database folder during dev, but next to the executable in prod
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(BASE_DIR, "logistics.db")
else:
    # Go up one level from 'database/' to project root
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    DB_PATH = os.path.join(PROJECT_ROOT, "logistics.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False) # Turn off echo for production
SessionLocal = sessionmaker(bind=engine)

def get_db_connection():
    return engine
