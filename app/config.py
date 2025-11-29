import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "DEV").upper()
    RAILWAY_DOMAIN = os.getenv("RAILWAY_DOMAIN")
    PORT = int(os.getenv("PORT", 8000))
    
    # Google Auth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
    
    def get_redirect_uri(self):
        if self.DEPLOYMENT_MODE == "PROD" and self.RAILWAY_DOMAIN:
            return f"https://{self.RAILWAY_DOMAIN}/auth/callback"
        return self.GOOGLE_REDIRECT_URI or "http://localhost:8000/auth/callback"

settings = Settings()
