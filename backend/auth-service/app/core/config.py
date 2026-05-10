from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        self.SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
        self.ALGORITHM = "HS256"

        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL não configurada no ambiente")


settings = Settings()