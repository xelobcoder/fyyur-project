from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_NAME = os.environ.get("Database_name")
DATABASE_USER=os.environ.get("Database_user")
DATABASE_PASSWORD = os.environ.get("Database_password")