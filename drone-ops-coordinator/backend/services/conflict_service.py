from datetime import datetime
from typing import List, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ConflictService:
    """Service for detecting scheduling and assignment conflicts"""
    
    def __init__(self, sheets_service):
        self.sheets = sheets_service
    
    def detect_all_conflicts(self) -> Dict[str, List[Dict]]:
        """Detect all types of conflicts"""
        try:
            conflicts = {
                "double_bookings": self.detect_double_bookings(),
                "skill_mismatches": self.detect_skill_mismatches(),
                "location_mismatches": self.detect_location_mismatches(),
                "maintenance_conflicts": self.detect_maintenance_conflicts()
            }
            
            total_conflicts = sum(len(v) for v in conflicts.values())
            logger.info(f"Detected {total_conflicts} total conflicts")
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting conflicts: {str(e)}")
            raise
    
    def detect_double_bookings(self) -> List[Dict]:
        """Detect pilots or drones assigned to overlapping missions"""
        try:
            missions_df = self.sheets.get_missions()
            pilots_df = self.sheets.get_pilot_roster()
            drones_df = self.sheets.get_drone_fleet()
            
            conflicts = []
            
            # Convert date strings to datetime
            missions_df['start_date'] = pd.to_datetime(missions_df['start_date'])
            missions_df['end_date'] = pd.to_datetime(missions_df['end_date'])
            
            # Check pilot double-bookings
            assigned_pilots = pilots_df[pilots_df['current_assignment'] != '–']
            
            for _, pilot in assigned_pilots.iterrows():
                pilot_missions = missions_df[
                    missions_df['project_id'] == pilot['current_assignment']
                ]
                
                if len(pilot_missions) == 0:
                    continue
                
                pilot_mission = pilot_missions.iloc[0]
                
                # Check for overlapping missions
                overlapping = missions_df[
                    (missions_df['project_id'] != pilot['current_assignment']) &
                    (missions_df['start_date'] <= pilot_mission['end_date']) &
                    (missions_df['end_date'] >= pilot_mission['start_date'])
                ]
                
                if len(overlapping) > 0:
                    conflicts.append({
                        "type": "pilot_double_booking",
                        "pilot_id": pilot['pilot_id'],
                        "pilot_name": pilot['name'],
                        "current_assignment": pilot['current_assignment'],
                        "conflicting_missions": overlapping['project_id'].tolist(),
                        "severity": "high"
                    })
            
            # Check drone double-bookings (similar logic)
            assigned_drones = drones_df[drones_df['current_assignment'] != '–']
            
            for _, drone in assigned_drones.iterrows():
                drone_missions = missions_df[
                    missions_df['project_id'] == drone['current_assignment']
                ]
                
                if len(drone_missions) == 0:
                    continue
                
                drone_mission = drone_missions.iloc[0]
                
                overlapping = missions_df[
                    (missions_df['project_id'] != drone['current_assignment']) &
                    (missions_df['start_date'] <= drone_mission['end_date']) &
                    (missions_df['end_date'] >= drone_mission['start_date'])
                ]
                
                if len(overlapping) > 0:
                    conflicts.append({
                        "type": "drone_double_booking",
                        "drone_id": drone['drone_id'],
                        "current_assignment": drone['current_assignment'],
                        "conflicting_missions": overlapping['project_id'].tolist(),
                        "severity": "high"
                    })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting double bookings: {str(e)}")
            return []
    
    def detect_skill_mismatches(self) -> List[Dict]:
        """Detect assignments where pilot lacks required skills or certifications"""
        try:
            missions_df = self.sheets.get_missions()
            pilots_df = self.sheets.get_pilot_roster()
            
            conflicts = []
            
            # Check each assigned pilot
            assigned_pilots = pilots_df[pilots_df['current_assignment'] != '–']
            
            for _, pilot in assigned_pilots.iterrows():
                # Get mission details
                mission = missions_df[
                    missions_df['project_id'] == pilot['current_assignment']
                ]
                
                if len(mission) == 0:
                    continue
                
                mission = mission.iloc[0]
                
                # Parse skills and certs
                pilot_skills = set(str(pilot['skills']).split(', '))
                pilot_certs = set(str(pilot['certifications']).split(', '))
                
                required_skills = set(str(mission['required_skills']).split(', '))
                required_certs = set(str(mission['required_certs']).split(', '))
                
                # Check for missing skills
                missing_skills = required_skills - pilot_skills
                missing_certs = required_certs - pilot_certs
                
                if missing_skills or missing_certs:
                    conflicts.append({
                        "type": "skill_mismatch",
                        "pilot_id": pilot['pilot_id'],
                        "pilot_name": pilot['name'],
                        "project_id": pilot['current_assignment'],
                        "missing_skills": list(missing_skills),
                        "missing_certifications": list(missing_certs),
                        "severity": "high" if missing_certs else "medium"
                    })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting skill mismatches: {str(e)}")
            return []
    
    def detect_location_mismatches(self) -> List[Dict]:
        """Detect when pilot and drone are in different locations"""
        try:
            missions_df = self.sheets.get_missions()
            pilots_df = self.sheets.get_pilot_roster()
            drones_df = self.sheets.get_drone_fleet()
            
            conflicts = []
            
            # Check each mission
            for _, mission in missions_df.iterrows():
                project_id = mission['project_id']
                mission_location = mission['location']
                
                # Find assigned pilot and drone
                assigned_pilot = pilots_df[pilots_df['current_assignment'] == project_id]
                assigned_drone = drones_df[drones_df['current_assignment'] == project_id]
                
                if len(assigned_pilot) > 0 and len(assigned_drone) > 0:
                    pilot = assigned_pilot.iloc[0]
                    drone = assigned_drone.iloc[0]
                    
                    # Check location mismatches
                    if pilot['location'] != mission_location:
                        conflicts.append({
                            "type": "pilot_location_mismatch",
                            "project_id": project_id,
                            "pilot_id": pilot['pilot_id'],
                            "pilot_location": pilot['location'],
                            "mission_location": mission_location,
                            "severity": "medium"
                        })
                    
                    if drone['location'] != mission_location:
                        conflicts.append({
                            "type": "drone_location_mismatch",
                            "project_id": project_id,
                            "drone_id": drone['drone_id'],
                            "drone_location": drone['location'],
                            "mission_location": mission_location,
                            "severity": "medium"
                        })
                    
                    if pilot['location'] != drone['location']:
                        conflicts.append({
                            "type": "pilot_drone_location_mismatch",
                            "project_id": project_id,
                            "pilot_id": pilot['pilot_id'],
                            "drone_id": drone['drone_id'],
                            "pilot_location": pilot['location'],
                            "drone_location": drone['location'],
                            "severity": "low"
                        })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting location mismatches: {str(e)}")
            return []
    
    def detect_maintenance_conflicts(self) -> List[Dict]:
        """Detect drones assigned to missions while in maintenance"""
        try:
            drones_df = self.sheets.get_drone_fleet()
            
            conflicts = []
            
            # Check for drones in maintenance that are assigned
            maintenance_drones = drones_df[
                (drones_df['status'] == 'Maintenance') & 
                (drones_df['current_assignment'] != '–')
            ]
            
            for _, drone in maintenance_drones.iterrows():
                conflicts.append({
                    "type": "maintenance_conflict",
                    "drone_id": drone['drone_id'],
                    "current_assignment": drone['current_assignment'],
                    "maintenance_due": drone['maintenance_due'],
                    "severity": "high"
                })
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting maintenance conflicts: {str(e)}")
            return []
