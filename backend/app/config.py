"""
All the settings the app needs, read from environment variables (which
load from the .env file). Keeping them in one place means nothing else
in the codebase has to know HOW a setting is stored -- it just imports
`settings` from here.
"""
import os
from dotenv import load_dotenv

# This line reads the ".env" file in the project root and makes its
# values available via os.environ, exactly as if you'd set them in
# your terminal with `export KEY=value`.
load_dotenv()


class Settings:
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./studybuddy.db")


settings = Settings()
