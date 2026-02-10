from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from services.sheets_service import SheetsService
from services.assignment_service import AssignmentService
from services.conflict_service import ConflictService
from services.agent_service import AgentService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize services
try:
    Config.validate()
    
    sheets_service = SheetsService()
    assignment_service = AssignmentService(sheets_service)
    conflict_service = ConflictService(sheets_service)
    agent_service = AgentService(sheets_service, assignment_service, conflict_service)
    
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    sys.exit(1)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test Google Sheets connection
        pilots = sheets_service.get_pilot_roster()
        
        return jsonify({
            "status": "healthy",
            "services": {
                "google_sheets": "connected",
                "anthropic_api": "configured"
            },
            "data": {
                "pilots": len(pilots),
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# Main chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    """Main conversational endpoint"""
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        logger.info(f"Received message: {message}")
        
        # Get AI response
        response = agent_service.chat(message)
        
        return jsonify({
            "response": response,
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Reset conversation endpoint
@app.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    """Reset conversation history"""
    try:
        agent_service.reset_conversation()
        return jsonify({
            "status": "success",
            "message": "Conversation reset"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Data endpoints for direct access (optional)
@app.route('/api/pilots', methods=['GET'])
def get_pilots():
    """Get all pilots"""
    try:
        df = sheets_service.get_pilot_roster()
        return jsonify(df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drones', methods=['GET'])
def get_drones():
    """Get all drones"""
    try:
        df = sheets_service.get_drone_fleet()
        return jsonify(df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/missions', methods=['GET'])
def get_missions():
    """Get all missions"""
    try:
        df = sheets_service.get_missions()
        return jsonify(df.to_dict(orient='records')), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conflicts', methods=['GET'])
def get_conflicts():
    """Get all conflicts"""
    try:
        conflicts = conflict_service.detect_all_conflicts()
        return jsonify(conflicts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/pilots/<pilot_id>/assign', methods=['POST'])
def assign_pilot(pilot_id):
    """Assign pilot to mission"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        result = sheets_service.assign_pilot_to_mission(pilot_id, project_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/drones/<drone_id>/assign', methods=['POST'])
def assign_drone(drone_id):
    """Assign drone to mission"""
    try:
        data = request.json
        project_id = data.get('project_id')
        
        result = sheets_service.assign_drone_to_mission(drone_id, project_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = Config.PORT
    debug = Config.DEBUG
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
