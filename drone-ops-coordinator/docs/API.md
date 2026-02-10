# API Documentation

## Base URL
http://localhost:5000/

## Endpoints

### Health Check
**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "services": {
    "google_sheets": "connected",
    "gemini_api": "configured"
  }
}
```

### Chat
**POST** `/api/chat`

Request:
```json
{
  "message": "Show me all available pilots"
}
```

Response:
```json
{
  "response": "Here are the available pilots...",
  "status": "success"
}
```

### Get Pilots
**GET** `/api/pilots`

Response: Array of pilot objects

### Get Drones
**GET** `/api/drones`

Response: Array of drone objects

### Get Missions
**GET** `/api/missions`

Response: Array of mission objects

### Detect Conflicts
**GET** `/api/conflicts`

Response:
```json
{
  "double_bookings": [],
  "skill_mismatches": [],
  "location_mismatches": [],
  "maintenance_conflicts": []
}
```

### Assign Pilot
**POST** `/api/pilots/:pilot_id/assign`

Request:
```json
{
  "project_id": "PRJ001"
}
```

### Assign Drone
**POST** `/api/drones/:drone_id/assign`

Request:
```json
{
  "project_id": "PRJ001"
}
```