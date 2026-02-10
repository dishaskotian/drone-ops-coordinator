from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class AssignmentService:
    """Service for matching pilots and drones to missions"""
    
    def __init__(self, sheets_service):
        self.sheets = sheets_service
    
    def find_suitable_pilots(self, project_id: str) -> List[Dict]:
        """Find pilots suitable for a specific project"""
        try:
            missions_df = self.sheets.get_missions()
            pilots_df = self.sheets.get_pilot_roster()
            
            # Get project details
            project = missions_df[missions_df['project_id'] == project_id]
            
            if len(project) == 0:
                raise ValueError(f"Project {project_id} not found")
            
            project = project.iloc[0]
            
            required_skills = set(str(project['required_skills']).split(', '))
            required_certs = set(str(project['required_certs']).split(', '))
            location = project['location']
            start_date = pd.to_datetime(project['start_date'])
            
            suitable_pilots = []
            
            for _, pilot in pilots_df.iterrows():
                pilot_skills = set(str(pilot['skills']).split(', '))
                pilot_certs = set(str(pilot['certifications']).split(', '))
                
                # Check skills
                has_skills = required_skills.issubset(pilot_skills)
                
                # Check certifications
                has_certs = required_certs.issubset(pilot_certs)
                
                # Check location
                same_location = pilot['location'] == location
                
                # Check availability
                is_available = pilot['status'] == 'Available'
                
                # Check available from date
                available_from = pd.to_datetime(pilot['available_from'])
                is_available_on_date = available_from <= start_date
                
                # Calculate suitability score
                score = 0
                if has_skills and has_certs:
                    score += 50
                    if is_available and is_available_on_date:
                        score += 30
                    if same_location:
                        score += 20
                    
                    # Bonus for extra skills
                    extra_skills = pilot_skills - required_skills
                    score += len(extra_skills) * 2
                    
                    suitable_pilots.append({
                        'pilot_id': pilot['pilot_id'],
                        'name': pilot['name'],
                        'location': pilot['location'],
                        'status': pilot['status'],
                        'skills': list(pilot_skills),
                        'certifications': list(pilot_certs),
                        'same_location': same_location,
                        'is_available': is_available,
                        'score': score,
                        'recommendation': self._get_recommendation(
                            has_skills, has_certs, is_available, same_location
                        )
                    })
            
            # Sort by score (highest first)
            suitable_pilots.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Found {len(suitable_pilots)} suitable pilots for {project_id}")
            
            return suitable_pilots
            
        except Exception as e:
            logger.error(f"Error finding suitable pilots: {str(e)}")
            raise
    
    def find_suitable_drones(self, project_id: str) -> List[Dict]:
        """Find drones suitable for a specific project"""
        try:
            missions_df = self.sheets.get_missions()
            drones_df = self.sheets.get_drone_fleet()
            
            # Get project details
            project = missions_df[missions_df['project_id'] == project_id]
            
            if len(project) == 0:
                raise ValueError(f"Project {project_id} not found")
            
            project = project.iloc[0]
            location = project['location']
            
            # Infer required capabilities from skills
            required_skills = str(project['required_skills']).lower()
            required_capabilities = []
            
            if 'thermal' in required_skills:
                required_capabilities.append('Thermal')
            if 'mapping' in required_skills or 'lidar' in required_skills:
                required_capabilities.append('LiDAR')
            
            suitable_drones = []
            
            for _, drone in drones_df.iterrows():
                drone_caps = set(str(drone['capabilities']).split(', '))
                
                # Check availability
                is_available = drone['status'] == 'Available'
                
                # Check location
                same_location = drone['location'] == location
                
                # Check maintenance
                needs_maintenance = drone['status'] == 'Maintenance'
                
                # Calculate score
                score = 0
                if is_available:
                    score += 40
                if same_location:
                    score += 30
                
                # Check if has required capabilities
                if required_capabilities:
                    has_required = any(cap in drone_caps for cap in required_capabilities)
                    if has_required:
                        score += 30
                else:
                    score += 20  # No specific requirement
                
                if not needs_maintenance:
                    suitable_drones.append({
                        'drone_id': drone['drone_id'],
                        'model': drone['model'],
                        'capabilities': list(drone_caps),
                        'location': drone['location'],
                        'status': drone['status'],
                        'same_location': same_location,
                        'is_available': is_available,
                        'maintenance_due': drone['maintenance_due'],
                        'score': score
                    })
            
            # Sort by score
            suitable_drones.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Found {len(suitable_drones)} suitable drones for {project_id}")
            
            return suitable_drones
            
        except Exception as e:
            logger.error(f"Error finding suitable drones: {str(e)}")
            raise
    
    def get_reassignment_suggestions(self, project_id: str) -> Dict:
        """Get suggestions for urgent reassignment"""
        try:
            missions_df = self.sheets.get_missions()
            pilots_df = self.sheets.get_pilot_roster()
            
            # Get project details
            project = missions_df[missions_df['project_id'] == project_id]
            
            if len(project) == 0:
                raise ValueError(f"Project {project_id} not found")
            
            project = project.iloc[0]
            priority = project['priority']
            
            suggestions = {
                "immediate_available": self.find_suitable_pilots(project_id),
                "reassignment_candidates": []
            }
            
            # If urgent and no immediate pilots available
            if priority == 'Urgent' and len(suggestions["immediate_available"]) == 0:
                # Find pilots on lower priority missions
                assigned_pilots = pilots_df[pilots_df['current_assignment'] != '–']
                
                for _, pilot in assigned_pilots.iterrows():
                    current_mission = missions_df[
                        missions_df['project_id'] == pilot['current_assignment']
                    ]
                    
                    if len(current_mission) > 0:
                        current_mission = current_mission.iloc[0]
                        current_priority = current_mission['priority']
                        
                        # Only suggest if current mission is lower priority
                        if current_priority in ['Standard', 'Medium']:
                            suggestions["reassignment_candidates"].append({
                                "pilot_id": pilot['pilot_id'],
                                "name": pilot['name'],
                                "current_assignment": pilot['current_assignment'],
                                "current_priority": current_priority,
                                "location": pilot['location']
                            })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting reassignment suggestions: {str(e)}")
            raise
    
    def _get_recommendation(self, has_skills: bool, has_certs: bool, 
                          is_available: bool, same_location: bool) -> str:
        """Get recommendation text for a pilot"""
        if has_skills and has_certs and is_available and same_location:
            return "Excellent match - Ready to deploy"
        elif has_skills and has_certs and is_available:
            return "Good match - Different location"
        elif has_skills and has_certs:
            return "Qualified but not available"
        else:
            return "Not suitable - Missing requirements"
