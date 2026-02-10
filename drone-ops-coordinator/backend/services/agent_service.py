import anthropic
from config import Config
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

class AgentService:
    """AI Agent service using Claude for conversational interface"""
    
    def __init__(self, sheets_service, assignment_service, conflict_service):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.sheets = sheets_service
        self.assignment = assignment_service
        self.conflict = conflict_service
        self.conversation_history = []
        
        # Define available tools/functions
        self.tools = [
            {
                "name": "get_pilot_roster",
                "description": "Get all pilots or filter by criteria (skill, certification, location, status)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "skill": {"type": "string", "description": "Filter by skill (e.g., Mapping, Inspection)"},
                        "certification": {"type": "string", "description": "Filter by certification (e.g., DGCA)"},
                        "location": {"type": "string", "description": "Filter by location (e.g., Bangalore, Mumbai)"},
                        "status": {"type": "string", "description": "Filter by status (Available, Assigned, On Leave)"}
                    }
                }
            },
            {
                "name": "get_drone_fleet",
                "description": "Get all drones or filter by criteria (capability, status, location)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "capability": {"type": "string", "description": "Filter by capability (e.g., Thermal, LiDAR)"},
                        "status": {"type": "string", "description": "Filter by status (Available, Maintenance, Deployed)"},
                        "location": {"type": "string", "description": "Filter by location"}
                    }
                }
            },
            {
                "name": "get_missions",
                "description": "Get all missions or filter by criteria",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "priority": {"type": "string", "description": "Filter by priority (Urgent, High, Standard)"},
                        "location": {"type": "string", "description": "Filter by location"}
                    }
                }
            },
            {
                "name": "find_pilots_for_mission",
                "description": "Find suitable pilots for a specific mission/project",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID (e.g., PRJ001)"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "find_drones_for_mission",
                "description": "Find suitable drones for a specific mission/project",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"}
                    },
                    "required": ["project_id"]
                }
            },
            {
                "name": "detect_conflicts",
                "description": "Detect all conflicts (double-bookings, skill mismatches, location issues, maintenance)",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "update_pilot_status",
                "description": "Update a pilot's status in Google Sheets",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "pilot_id": {"type": "string", "description": "Pilot ID (e.g., P001)"},
                        "new_status": {"type": "string", "description": "New status (Available, Assigned, On Leave)"},
                        "current_assignment": {"type": "string", "description": "Project ID if assigning"}
                    },
                    "required": ["pilot_id", "new_status"]
                }
            },
            {
                "name": "update_drone_status",
                "description": "Update a drone's status in Google Sheets",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "drone_id": {"type": "string", "description": "Drone ID (e.g., D001)"},
                        "new_status": {"type": "string", "description": "New status (Available, Maintenance, Deployed)"},
                        "current_assignment": {"type": "string", "description": "Project ID if assigning"}
                    },
                    "required": ["drone_id", "new_status"]
                }
            },
            {
                "name": "get_urgent_reassignment_suggestions",
                "description": "Get suggestions for urgent mission reassignments",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Urgent project ID"}
                    },
                    "required": ["project_id"]
                }
            }
        ]
    
    def chat(self, user_message: str) -> str:
        """Process user message and return AI response"""
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            # Call Claude API
            response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.MAX_TOKENS,
                system=system_prompt,
                messages=self.conversation_history,
                tools=self.tools
            )
            
            # Process response and handle tool calls
            return self._process_response(response)
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for Claude"""
        return """You are a helpful AI assistant for Skylark Drones operations coordination. 

Your role is to help manage:
- Pilot roster and availability
- Drone fleet and inventory
- Mission assignments
- Conflict detection
- Urgent reassignments

You have access to real-time data from Google Sheets and can update pilot and drone statuses.

When users ask questions:
1. Use the appropriate tools to fetch data
2. Provide clear, concise answers
3. Highlight any conflicts or issues
4. Suggest solutions when problems are detected
5. Update statuses when requested

Be friendly, professional, and proactive in identifying potential issues."""
    
    def _process_response(self, response) -> str:
        """Process Claude's response and handle tool calls"""
        assistant_message = ""
        tool_results = []
        
        # Process all content blocks
        for block in response.content:
            if block.type == "text":
                assistant_message += block.text
            
            elif block.type == "tool_use":
                # Execute the tool
                tool_name = block.name
                tool_input = block.input
                
                logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
                
                # Call the appropriate function
                tool_result = self._execute_tool(tool_name, tool_input)
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(tool_result)
                })
        
        # If there were tool calls, we need to continue the conversation
        if tool_results:
            # Add assistant's response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Add tool results to history
            self.conversation_history.append({
                "role": "user",
                "content": tool_results
            })
            
            # Get final response from Claude
            final_response = self.client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=Config.MAX_TOKENS,
                system=self._create_system_prompt(),
                messages=self.conversation_history,
                tools=self.tools
            )
            
            # Extract text from final response
            final_text = ""
            for block in final_response.content:
                if block.type == "text":
                    final_text += block.text
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": final_text
            })
            
            return final_text
        
        else:
            # No tool calls, return the text response
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
    
    def _execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        """Execute a tool function"""
        try:
            if tool_name == "get_pilot_roster":
                df = self.sheets.get_pilot_roster()
                
                # Apply filters
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
                
                # Apply filters
                if tool_input.get('capability'):
                    df = df[df['capabilities'].str.contains(tool_input['capability'], case=False, na=False)]
                if tool_input.get('status'):
                    df = df[df['status'] == tool_input['status']]
                if tool_input.get('location'):
                    df = df[df['location'].str.contains(tool_input['location'], case=False, na=False)]
                
                return df.to_dict(orient='records')
            
            elif tool_name == "get_missions":
                df = self.sheets.get_missions()
                
                # Apply filters
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
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"error": str(e)}
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")
