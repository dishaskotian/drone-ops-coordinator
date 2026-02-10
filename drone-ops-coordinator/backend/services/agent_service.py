import json
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types
from config import Config

logger = logging.getLogger(__name__)

class AgentService:
    """AI Agent service using Gemini for conversational interface"""
    
    def __init__(self, sheets_service, assignment_service, conflict_service):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.sheets = sheets_service
        self.assignment = assignment_service
        self.conflict = conflict_service
        self.chat_session = None
        self.model_id = "gemini-2.5-flash-lite"
        
        # Define available tools/functions for Gemini
        # Note: Gemini uses OpenAPI-style schema. Your Anthropic 'input_schema'
        # maps directly to Gemini's 'parameters'.
        self.tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="get_pilot_roster",
                        description="Get all pilots or filter by criteria (skill, certification, location, status)",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "skill": {"type": "STRING", "description": "Filter by skill (e.g., Mapping, Inspection)"},
                                "certification": {"type": "STRING", "description": "Filter by certification (e.g., DGCA)"},
                                "location": {"type": "STRING", "description": "Filter by location (e.g., Bangalore, Mumbai)"},
                                "status": {"type": "STRING", "description": "Filter by status (Available, Assigned, On Leave)"}
                            }
                        }
                    ),
                    types.FunctionDeclaration(
                        name="get_drone_fleet",
                        description="Get all drones or filter by criteria (capability, status, location)",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "capability": {"type": "STRING", "description": "Filter by capability (e.g., Thermal, LiDAR)"},
                                "status": {"type": "STRING", "description": "Filter by status (Available, Maintenance, Deployed)"},
                                "location": {"type": "STRING", "description": "Filter by location"}
                            }
                        }
                    ),
                    types.FunctionDeclaration(
                        name="get_missions",
                        description="Get all missions or filter by criteria",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "priority": {"type": "STRING", "description": "Filter by priority (Urgent, High, Standard)"},
                                "location": {"type": "STRING", "description": "Filter by location"}
                            }
                        }
                    ),
                    types.FunctionDeclaration(
                        name="find_pilots_for_mission",
                        description="Find suitable pilots for a specific mission/project",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "project_id": {"type": "STRING", "description": "Project ID (e.g., PRJ001)"}
                            },
                            "required": ["project_id"]
                        }
                    ),
                    types.FunctionDeclaration(
                        name="find_drones_for_mission",
                        description="Find suitable drones for a specific mission/project",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "project_id": {"type": "STRING", "description": "Project ID"}
                            },
                            "required": ["project_id"]
                        }
                    ),
                    types.FunctionDeclaration(
                        name="detect_conflicts",
                        description="Detect all conflicts (double-bookings, skill mismatches, location issues, maintenance)",
                        parameters={"type": "OBJECT", "properties": {}}
                    ),
                    types.FunctionDeclaration(
                        name="update_pilot_status",
                        description="Update a pilot's status in Google Sheets",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "pilot_id": {"type": "STRING", "description": "Pilot ID (e.g., P001)"},
                                "new_status": {"type": "STRING", "description": "New status (Available, Assigned, On Leave)"},
                                "current_assignment": {"type": "STRING", "description": "Project ID if assigning"}
                            },
                            "required": ["pilot_id", "new_status"]
                        }
                    ),
                    types.FunctionDeclaration(
                        name="update_drone_status",
                        description="Update a drone's status in Google Sheets",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "drone_id": {"type": "STRING", "description": "Drone ID (e.g., D001)"},
                                "new_status": {"type": "STRING", "description": "New status (Available, Maintenance, Deployed)"},
                                "current_assignment": {"type": "STRING", "description": "Project ID if assigning"}
                            },
                            "required": ["drone_id", "new_status"]
                        }
                    ),
                    types.FunctionDeclaration(
                        name="get_urgent_reassignment_suggestions",
                        description="Get suggestions for urgent mission reassignments",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "project_id": {"type": "STRING", "description": "Urgent project ID"}
                            },
                            "required": ["project_id"]
                        }
                    )
                ]
            )
        ]
        
        self.reset_conversation()

    def _create_system_prompt(self) -> str:
        """System instructions for the Skylark Drones AI"""
        return """You are a helpful AI assistant for Skylark Drones operations coordination. 

Your role is to help manage:
- Pilot roster and availability
- Drone fleet and inventory
- Mission assignments
- Conflict detection
- Urgent reassignments

You have access to real-time data and can update pilot/drone statuses.
1. Use tools to fetch data.
2. Provide clear answers and highlight conflicts.
3. Proactively suggest solutions for detected problems.
4. Update statuses only when explicitly requested.
Be professional and friendly."""

    def chat(self, user_message: str) -> str:
        """Process user message using Gemini's continuous chat session"""
        try:
            # Send message to Gemini chat session
            response = self.chat_session.send_message(user_message)
            
            # Handle potential multi-turn tool calling
            # Gemini automatically suggests calls; we execute and send results back
            while response.candidates[0].content.parts[0].function_call:
                tool_results = []
                
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        call = part.function_call
                        logger.info(f"Executing tool: {call.name} with input: {call.args}")
                        
                        result = self._execute_tool(call.name, call.args)
                        
                        tool_results.append(
                            types.Part.from_function_response(
                                name=call.name,
                                response={"result": result}
                            )
                        )
                
                # Send tool outputs back to the model to get the final natural language response
                response = self.chat_session.send_message(tool_results)

            return response.text
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"I encountered an error: {str(e)}. Please try again."

    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Internal router for executing local service logic"""
        try:
            if tool_name == "get_pilot_roster":
                df = self.sheets.get_pilot_roster()
                if tool_input.get('skill'):
                    df = df[df['skills'].str.contains(tool_input['skill'], case=False, na=False)]
                if tool_input.get('certification'):
                    df = df[df['certifications'].str.contains(tool_input['certification'], case=False, na=False)]
                if tool_input.get('location'):
                    df = df[df['location'].str.contains(tool_input['location'], case=False, na=False)]
                if tool_input.get('status'):
                    df = df[df['status'] == tool_input['status']]
                return df.to_dict(orient='records')

            elif tool_name == "get_drone_fleet":
                df = self.sheets.get_drone_fleet()
                if tool_input.get('capability'):
                    df = df[df['capabilities'].str.contains(tool_input['capability'], case=False, na=False)]
                if tool_input.get('status'):
                    df = df[df['status'] == tool_input['status']]
                if tool_input.get('location'):
                    df = df[df['location'].str.contains(tool_input['location'], case=False, na=False)]
                return df.to_dict(orient='records')

            elif tool_name == "get_missions":
                df = self.sheets.get_missions()
                if tool_input.get('priority'):
                    df = df[df['priority'] == tool_input['priority']]
                if tool_input.get('location'):
                    df = df[df['location'].str.contains(tool_input['location'], case=False, na=False)]
                return df.to_dict(orient='records')

            elif tool_name == "find_pilots_for_mission":
                return self.assignment.find_suitable_pilots(tool_input['project_id'])

            elif tool_name == "find_drones_for_mission":
                return self.assignment.find_suitable_drones(tool_input['project_id'])

            elif tool_name == "detect_conflicts":
                return self.conflict.detect_all_conflicts()

            elif tool_name == "update_pilot_status":
                return self.sheets.update_pilot_status(
                    tool_input['pilot_id'], 
                    tool_input['new_status'], 
                    tool_input.get('current_assignment')
                )

            elif tool_name == "update_drone_status":
                return self.sheets.update_drone_status(
                    tool_input['drone_id'], 
                    tool_input['new_status'], 
                    tool_input.get('current_assignment')
                )

            elif tool_name == "get_urgent_reassignment_suggestions":
                return self.assignment.get_reassignment_suggestions(tool_input['project_id'])

            return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}

    def reset_conversation(self):
        """Reset state by starting a fresh Gemini chat session"""
        self.chat_session = self.client.chats.create(
            model=self.model_id,
            config=types.GenerateContentConfig(
                system_instruction=self._create_system_prompt(),
                tools=self.tools,
                temperature=0.1 # Low temperature for operational accuracy
            )
        )
        logger.info("Chat session initialized/reset")