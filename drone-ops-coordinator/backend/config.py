import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Gemini API (Replacing Anthropic)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'  # Fast, efficient, and has a great free tier
    
    # Google Sheets
    # Check if credentials are in environment variable (Railway)
    if os.getenv('GOOGLE_CREDENTIALS'):
        # Write to temp file
        import tempfile
        creds = json.loads(os.getenv('GOOGLE_CREDENTIALS'))
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(creds, f)
            GOOGLE_CREDENTIALS_PATH = f.name
    else:
        GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials/google-sheets.json')
    
    PILOT_ROSTER_SHEET_ID = os.getenv('PILOT_ROSTER_SHEET_ID')
    DRONE_FLEET_SHEET_ID = os.getenv('DRONE_FLEET_SHEET_ID')
    MISSIONS_SHEET_ID = os.getenv('MISSIONS_SHEET_ID')
    
    # Flask
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # AI Model
    CLAUDE_MODEL = 'claude-sonnet-4-20250514'
    MAX_TOKENS = 4096