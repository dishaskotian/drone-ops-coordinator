import gspread
from google.oauth2.service_account import Credentials
from config import Config
import pandas as pd
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetsService:
    """Service for interacting with Google Sheets"""
    
    def __init__(self):
        """Initialize Google Sheets client"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_CREDENTIALS_PATH,
                scopes=scopes
            )
            
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {str(e)}")
            raise
    
    def get_pilot_roster(self) -> pd.DataFrame:
        """Read pilot roster from Google Sheets"""
        try:
            sheet = self.client.open_by_key(Config.PILOT_ROSTER_SHEET_ID)
            worksheet = sheet.get_worksheet(0)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} pilots from roster")
            return df
        except Exception as e:
            logger.error(f"Error reading pilot roster: {str(e)}")
            raise Exception(f"Error reading pilot roster: {str(e)}")
    
    def get_drone_fleet(self) -> pd.DataFrame:
        """Read drone fleet from Google Sheets"""
        try:
            sheet = self.client.open_by_key(Config.DRONE_FLEET_SHEET_ID)
            worksheet = sheet.get_worksheet(0)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} drones from fleet")
            return df
        except Exception as e:
            logger.error(f"Error reading drone fleet: {str(e)}")
            raise Exception(f"Error reading drone fleet: {str(e)}")
    
    def get_missions(self) -> pd.DataFrame:
        """Read missions from Google Sheets"""
        try:
            sheet = self.client.open_by_key(Config.MISSIONS_SHEET_ID)
            worksheet = sheet.get_worksheet(0)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            logger.info(f"Retrieved {len(df)} missions")
            return df
        except Exception as e:
            logger.error(f"Error reading missions: {str(e)}")
            raise Exception(f"Error reading missions: {str(e)}")
    
    def update_pilot_status(self, pilot_id: str, new_status: str, 
                           current_assignment: Optional[str] = None) -> Dict:
        """Update pilot status in Google Sheets"""
        try:
            sheet = self.client.open_by_key(Config.PILOT_ROSTER_SHEET_ID)
            worksheet = sheet.get_worksheet(0)
            
            # Find the pilot row
            cell = worksheet.find(pilot_id)
            if not cell:
                raise ValueError(f"Pilot {pilot_id} not found")
            
            row = cell.row
            
            # Column mapping (adjust based on your sheet structure)
            # Assuming: A=pilot_id, B=name, C=skills, D=certs, E=location, 
            #           F=status, G=current_assignment, H=available_from
            
            # Update status (column F)
            worksheet.update_cell(row, 6, new_status)
            logger.info(f"Updated pilot {pilot_id} status to {new_status}")
            
            # Update assignment if provided (column G)
            if current_assignment is not None:
                worksheet.update_cell(row, 7, current_assignment)
                logger.info(f"Updated pilot {pilot_id} assignment to {current_assignment}")
            
            return {
                "success": True, 
                "message": f"Updated pilot {pilot_id}",
                "pilot_id": pilot_id,
                "new_status": new_status,
                "current_assignment": current_assignment
            }
            
        except Exception as e:
            logger.error(f"Error updating pilot status: {str(e)}")
            raise Exception(f"Error updating pilot status: {str(e)}")
    
    def update_drone_status(self, drone_id: str, new_status: str, 
                           current_assignment: Optional[str] = None) -> Dict:
        """Update drone status in Google Sheets"""
        try:
            sheet = self.client.open_by_key(Config.DRONE_FLEET_SHEET_ID)
            worksheet = sheet.get_worksheet(0)
            
            # Find the drone row
            cell = worksheet.find(drone_id)
            if not cell:
                raise ValueError(f"Drone {drone_id} not found")
            
            row = cell.row
            
            # Column mapping (adjust based on your sheet structure)
            # Assuming: A=drone_id, B=model, C=capabilities, D=status, 
            #           E=location, F=current_assignment, G=maintenance_due
            
            # Update status (column D)
            worksheet.update_cell(row, 4, new_status)
            logger.info(f"Updated drone {drone_id} status to {new_status}")
            
            # Update assignment if provided (column F)
            if current_assignment is not None:
                worksheet.update_cell(row, 6, current_assignment)
                logger.info(f"Updated drone {drone_id} assignment to {current_assignment}")
            
            return {
                "success": True,
                "message": f"Updated drone {drone_id}",
                "drone_id": drone_id,
                "new_status": new_status,
                "current_assignment": current_assignment
            }
            
        except Exception as e:
            logger.error(f"Error updating drone status: {str(e)}")
            raise Exception(f"Error updating drone status: {str(e)}")
    
    def assign_pilot_to_mission(self, pilot_id: str, project_id: str) -> Dict:
        """Assign a pilot to a mission"""
        return self.update_pilot_status(
            pilot_id=pilot_id,
            new_status="Assigned",
            current_assignment=project_id
        )
    
    def assign_drone_to_mission(self, drone_id: str, project_id: str) -> Dict:
        """Assign a drone to a mission"""
        return self.update_drone_status(
            drone_id=drone_id,
            new_status="Deployed",
            current_assignment=project_id
        )
