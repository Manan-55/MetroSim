from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.track import TrackType, TrackStatus

class TrackBase(BaseModel):
    track_number: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    track_type: TrackType
    status: TrackStatus = TrackStatus.OPERATIONAL
    start_station: str = Field(..., max_length=100)
    end_station: str = Field(..., max_length=100)
    length: float = Field(..., ge=0)
    gauge: Optional[float] = Field(None, ge=0)
    max_speed: Optional[float] = Field(None, ge=0)
    grade: Optional[float] = None
    curvature: Optional[float] = None
    electrified: bool = False
    voltage: Optional[int] = Field(None, ge=0)
    signaling_system: Optional[str] = Field(None, max_length=50)
    capacity_trains_per_hour: Optional[int] = Field(None, ge=0)
    current_usage: Optional[float] = Field(None, ge=0, le=100)
    condition_rating: Optional[float] = Field(None, ge=1, le=10)
    description: Optional[str] = None

class TrackCreate(TrackBase):
    pass

class TrackUpdate(BaseModel):
    track_number: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    track_type: Optional[TrackType] = None
    status: Optional[TrackStatus] = None
    start_station: Optional[str] = Field(None, max_length=100)
    end_station: Optional[str] = Field(None, max_length=100)
    length: Optional[float] = Field(None, ge=0)
    gauge: Optional[float] = Field(None, ge=0)
    max_speed: Optional[float] = Field(None, ge=0)
    grade: Optional[float] = None
    curvature: Optional[float] = None
    electrified: Optional[bool] = None
    voltage: Optional[int] = Field(None, ge=0)
    signaling_system: Optional[str] = Field(None, max_length=50)
    capacity_trains_per_hour: Optional[int] = Field(None, ge=0)
    current_usage: Optional[float] = Field(None, ge=0, le=100)
    last_inspection: Optional[datetime] = None
    next_inspection: Optional[datetime] = None
    condition_rating: Optional[float] = Field(None, ge=1, le=10)
    description: Optional[str] = None

class Track(TrackBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_inspection: Optional[datetime] = None
    next_inspection: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class TrackWithDetails(Track):
    track_segments: List["TrackSegment"] = []

class TrackSegmentBase(BaseModel):
    track_id: int
    segment_number: int
    start_km: float = Field(..., ge=0)
    end_km: float = Field(..., ge=0)
    length: float = Field(..., ge=0)
    start_latitude: Optional[float] = Field(None, ge=-90, le=90)
    start_longitude: Optional[float] = Field(None, ge=-180, le=180)
    end_latitude: Optional[float] = Field(None, ge=-90, le=90)
    end_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_speed: Optional[float] = Field(None, ge=0)
    grade: Optional[float] = None
    curvature: Optional[float] = None
    bridges: int = Field(0, ge=0)
    tunnels: int = Field(0, ge=0)
    level_crossings: int = Field(0, ge=0)
    condition_rating: Optional[float] = Field(None, ge=1, le=10)

class TrackSegmentCreate(TrackSegmentBase):
    pass

class TrackSegmentUpdate(BaseModel):
    segment_number: Optional[int] = None
    start_km: Optional[float] = Field(None, ge=0)
    end_km: Optional[float] = Field(None, ge=0)
    length: Optional[float] = Field(None, ge=0)
    start_latitude: Optional[float] = Field(None, ge=-90, le=90)
    start_longitude: Optional[float] = Field(None, ge=-180, le=180)
    end_latitude: Optional[float] = Field(None, ge=-90, le=90)
    end_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_speed: Optional[float] = Field(None, ge=0)
    grade: Optional[float] = None
    curvature: Optional[float] = None
    bridges: Optional[int] = Field(None, ge=0)
    tunnels: Optional[int] = Field(None, ge=0)
    level_crossings: Optional[int] = Field(None, ge=0)
    condition_rating: Optional[float] = Field(None, ge=1, le=10)
    last_maintenance: Optional[datetime] = None

class TrackSegment(TrackSegmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_maintenance: Optional[datetime] = None
    created_at: datetime

class StationBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=10)
    name: str = Field(..., min_length=1, max_length=100)
    city: str = Field(..., max_length=100)
    country: str = Field(..., max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    elevation: Optional[float] = None
    station_type: Optional[str] = Field(None, max_length=50)
    platforms: int = Field(1, ge=1)
    tracks: int = Field(1, ge=1)
    electrified: bool = False
    has_parking: bool = False
    has_restaurant: bool = False
    has_waiting_room: bool = False
    has_ticket_office: bool = False
    wheelchair_accessible: bool = False
    daily_passengers: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    elevation: Optional[float] = None
    station_type: Optional[str] = Field(None, max_length=50)
    platforms: Optional[int] = Field(None, ge=1)
    tracks: Optional[int] = Field(None, ge=1)
    electrified: Optional[bool] = None
    has_parking: Optional[bool] = None
    has_restaurant: Optional[bool] = None
    has_waiting_room: Optional[bool] = None
    has_ticket_office: Optional[bool] = None
    wheelchair_accessible: Optional[bool] = None
    opened_date: Optional[datetime] = None
    daily_passengers: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None

class Station(StationBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    opened_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
