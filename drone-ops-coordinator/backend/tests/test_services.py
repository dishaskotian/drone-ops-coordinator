import pytest
from services.sheets_service import SheetsService
from services.assignment_service import AssignmentService
from services.conflict_service import ConflictService

def test_sheets_connection():
    """Test Google Sheets connection"""
    service = SheetsService()
    pilots = service.get_pilot_roster()
    assert len(pilots) > 0
    assert 'pilot_id' in pilots.columns

def test_find_suitable_pilots():
    """Test pilot matching algorithm"""
    sheets = SheetsService()
    assignment = AssignmentService(sheets)
    pilots = assignment.find_suitable_pilots('PRJ001')
    assert isinstance(pilots, list)

def test_conflict_detection():
    """Test conflict detection"""
    sheets = SheetsService()
    conflict = ConflictService(sheets)
    conflicts = conflict.detect_all_conflicts()
    assert 'double_bookings' in conflicts
    assert 'skill_mismatches' in conflicts

# Add more tests as needed