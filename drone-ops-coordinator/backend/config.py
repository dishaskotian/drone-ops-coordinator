import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Anthropic API
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # Google Sheets
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-sheets.json')
    PILOT_ROSTER_SHEET_ID = os.getenv('PILOT_ROSTER_SHEET_ID')
    DRONE_FLEET_SHEET_ID = os.getenv('DRONE_FLEET_SHEET_ID')
    MISSIONS_SHEET_ID = os.getenv('MISSIONS_SHEET_ID')
    
    # Flask
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # AI Model
    CLAUDE_MODEL = 'claude-sonnet-4-20250514'
    MAX_TOKENS = 4096
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = [
            'ANTHROPIC_API_KEY',
            'PILOT_ROSTER_SHEET_ID',
            'DRONE_FLEET_SHEET_ID',
            'MISSIONS_SHEET_ID'
        ]
        
        missing = []
        for var in required:
            if not getattr(cls, var):
                missing.append(var)
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return True
