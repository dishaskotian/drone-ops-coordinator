# Drone Operations Coordinator AI Agent

An intelligent AI-powered assistant for managing drone fleet operations, pilot assignments, and mission coordination with real-time Google Sheets integration.

## 🚁 Features

- **Conversational Interface**: Natural language interaction with the AI agent
- **Pilot Roster Management**: Query availability, skills, certifications, and locations
- **Drone Fleet Tracking**: Monitor drone status, capabilities, and maintenance schedules
- **Smart Assignment Matching**: AI-powered pilot-to-mission matching based on skills, location, and availability
- **Conflict Detection**: Automatically detect double-bookings, skill mismatches, and location conflicts
- **Urgent Reassignment**: Handle urgent missions with intelligent reassignment suggestions
- **Real-time Sync**: Two-way synchronization with Google Sheets

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Vite + JS)   │
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│  Flask Backend  │
│   (Python 3.9+) │
├─────────────────┤
│ Anthropic Claude│ ◄── AI Agent
│   Google Sheets │ ◄── Data Source
└─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask, Flask-CORS
- **AI**: Anthropic Claude API (Sonnet 4.5)
- **Database**: Google Sheets API
- **Frontend**: React 18, Vite
- **Libraries**: gspread, pandas, python-dotenv

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Google Cloud account with Sheets API enabled
- Anthropic API key
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/drone-ops-coordinator.git
cd drone-ops-coordinator
```

### 2. Setup Google Sheets

1. Create three Google Sheets:
   - Pilot Roster
   - Drone Fleet
   - Missions

2. Upload the provided CSV data to each sheet

3. Setup Google Cloud:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Sheets API and Google Drive API
   - Create Service Account credentials
   - Download JSON credentials file
   - Save it as `backend/credentials/google-sheets.json`

4. Share your Google Sheets with the service account email (found in the JSON file)

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials:
# - ANTHROPIC_API_KEY
# - Google Sheet IDs
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser

## 💬 Usage Examples

Ask the AI agent natural language questions:

```
"Show me all available pilots in Bangalore"

"Which pilots can work on PRJ001?"

"Is there any conflict with pilot P002's assignments?"

"Update pilot P001 status to On Leave"

"Find me a drone with thermal capabilities in Mumbai"

"Help me reassign pilot P003 to the urgent mission"
```

## 🧪 Running Tests

```bash
cd backend
pytest tests/
```

## 📁 Project Structure

```
drone-ops-coordinator/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   ├── services/
│   │   ├── sheets_service.py  # Google Sheets integration
│   │   ├── agent_service.py   # Claude AI agent
│   │   ├── assignment_service.py  # Assignment logic
│   │   └── conflict_service.py    # Conflict detection
│   ├── models/
│   │   ├── pilot.py           # Pilot data model
│   │   ├── drone.py           # Drone data model
│   │   └── mission.py         # Mission data model
│   └── tests/
│       └── test_services.py   # Unit tests
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main app component
│   │   ├── components/
│   │   │   ├── Chat.jsx       # Chat interface
│   │   │   ├── Message.jsx    # Message display
│   │   │   └── ConflictDisplay.jsx
│   │   └── styles/
│   │       └── App.css
│   └── package.json
├── docs/
│   ├── DECISION_LOG.md        # Design decisions
│   └── API.md                 # API documentation
└── README.md
```

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
GOOGLE_CREDENTIALS_PATH=credentials/google-sheets.json
PILOT_ROSTER_SHEET_ID=your_sheet_id_here
DRONE_FLEET_SHEET_ID=your_sheet_id_here
MISSIONS_SHEET_ID=your_sheet_id_here
PORT=5000
```

**Frontend (.env)**
```
VITE_API_URL=http://localhost:5000
```

## 🎯 Key Features Explained

### Conflict Detection
The system automatically detects:
- **Double-booking**: Pilots/drones assigned to overlapping missions
- **Skill mismatches**: Assignments requiring unavailable skills
- **Certification gaps**: Missing required certifications
- **Location mismatches**: Pilot and drone in different cities

### Urgent Reassignment
For urgent missions, the agent can:
- Identify immediately available resources
- Suggest reassigning from lower-priority missions
- Provide step-by-step reassignment plans
- Update Google Sheets with new assignments

## 🚢 Deployment

### Deploy to Railway

1. Create Railway account
2. Connect GitHub repository
3. Add environment variables
4. Deploy!

### Deploy to Replit

1. Import from GitHub
2. Configure Secrets
3. Run

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

For issues and questions, please open an issue on GitHub.

## 🙏 Acknowledgments

- Anthropic for Claude API
- Google Sheets API
- Flask and React communities
