import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Gemini API (Replacing Anthropic)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'  # Fast, efficient, and has a great free tier
    
    # Google Sheets
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-sheets.json')
    PILOT_ROSTER_SHEET_ID = os.getenv('PILOT_ROSTER_SHEET_ID')
    DRONE_FLEET_SHEET_ID = os.getenv('DRONE_FLEET_SHEET_ID')
    MISSIONS_SHEET_ID = os.getenv('MISSIONS_SHEET_ID')
    
    # Flask
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'GEMINI_API_KEY', # Changed from ANTHROPIC_API_KEY
            'PILOT_ROSTER_SHEET_ID',
            'DRONE_FLEET_SHEET_ID',
            'MISSIONS_SHEET_ID'
        ]
        
        missing = [var for var in required if not getattr(cls, var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True