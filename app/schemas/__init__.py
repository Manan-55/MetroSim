"""
Pydantic schemas for API serialization and validation.
"""

from app.schemas.train import (
    TrainCreate,
    TrainUpdate, 
    TrainResponse,
    TrainMaintenanceCreate,
    TrainMaintenanceResponse
)
from app.schemas.track import (
    TrackCreate,
    TrackUpdate,
    TrackResponse,
    StationCreate,
    StationResponse,
    TrackSegmentCreate,
    TrackSegmentResponse
)
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleStopCreate,
    ScheduleStopResponse,
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse
)

__all__ = [
    # Train schemas
    "TrainCreate",
    "TrainUpdate",
    "TrainResponse", 
    "TrainMaintenanceCreate",
    "TrainMaintenanceResponse",
    
    # Track schemas
    "TrackCreate",
    "TrackUpdate",
    "TrackResponse",
    "StationCreate", 
    "StationResponse",
    "TrackSegmentCreate",
    "TrackSegmentResponse",
    
    # Schedule schemas
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScheduleStopCreate",
    "ScheduleStopResponse", 
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentResponse"
]
