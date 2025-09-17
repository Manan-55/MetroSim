from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.schedule import ScheduleStatus, ScheduleType

class ScheduleBase(BaseModel):
    schedule_number: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    schedule_type: ScheduleType
    status: ScheduleStatus = ScheduleStatus.SCHEDULED
    train_id: int
    track_id: int
    departure_station_id: int
    arrival_station_id: int
    scheduled_departure: datetime
    scheduled_arrival: datetime
    distance: Optional[float] = Field(None, ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0)
    max_speed: Optional[float] = Field(None, ge=0)
    passenger_capacity: Optional[int] = Field(None, ge=0)
    cargo_weight: Optional[float] = Field(None, ge=0)
    priority: int = Field(5, ge=1, le=10)
    recurring: bool = False
    recurrence_pattern: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    schedule_number: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    schedule_type: Optional[ScheduleType] = None
    status: Optional[ScheduleStatus] = None
    train_id: Optional[int] = None
    track_id: Optional[int] = None
    departure_station_id: Optional[int] = None
    arrival_station_id: Optional[int] = None
    scheduled_departure: Optional[datetime] = None
    scheduled_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    distance: Optional[float] = Field(None, ge=0)
    estimated_duration: Optional[int] = Field(None, ge=0)
    actual_duration: Optional[int] = Field(None, ge=0)
    max_speed: Optional[float] = Field(None, ge=0)
    average_speed: Optional[float] = Field(None, ge=0)
    passenger_capacity: Optional[int] = Field(None, ge=0)
    passenger_count: Optional[int] = Field(None, ge=0)
    cargo_weight: Optional[float] = Field(None, ge=0)
    priority: Optional[int] = Field(None, ge=1, le=10)
    recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = Field(None, max_length=50)
    on_time_performance: Optional[float] = Field(None, ge=0, le=100)
    fuel_consumption: Optional[float] = Field(None, ge=0)
    energy_consumption: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

class Schedule(ScheduleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    actual_duration: Optional[int] = None
    average_speed: Optional[float] = None
    passenger_count: Optional[int] = None
    on_time_performance: Optional[float] = None
    fuel_consumption: Optional[float] = None
    energy_consumption: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

class ScheduleWithDetails(Schedule):
    train: Optional["Train"] = None
    track: Optional["Track"] = None
    departure_station: Optional["Station"] = None
    arrival_station: Optional["Station"] = None
    schedule_stops: List["ScheduleStop"] = []
    incidents: List["Incident"] = []

class ScheduleStopBase(BaseModel):
    schedule_id: int
    station_id: int
    stop_order: int
    scheduled_arrival: Optional[datetime] = None
    scheduled_departure: Optional[datetime] = None
    platform: Optional[str] = Field(None, max_length=10)
    stop_duration: Optional[int] = Field(None, ge=0)
    passenger_boarding: Optional[int] = Field(None, ge=0)
    passenger_alighting: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class ScheduleStopCreate(ScheduleStopBase):
    pass

class ScheduleStopUpdate(BaseModel):
    stop_order: Optional[int] = None
    scheduled_arrival: Optional[datetime] = None
    scheduled_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    platform: Optional[str] = Field(None, max_length=10)
    stop_duration: Optional[int] = Field(None, ge=0)
    passenger_boarding: Optional[int] = Field(None, ge=0)
    passenger_alighting: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class ScheduleStop(ScheduleStopBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    created_at: datetime

class IncidentBase(BaseModel):
    schedule_id: Optional[int] = None
    train_id: Optional[int] = None
    track_id: Optional[int] = None
    incident_type: str = Field(..., max_length=50)
    severity: str = Field(..., max_length=20)
    title: str = Field(..., max_length=200)
    description: str
    occurred_at: datetime
    delay_minutes: Optional[int] = Field(None, ge=0)
    affected_passengers: Optional[int] = Field(None, ge=0)
    estimated_cost: Optional[float] = Field(None, ge=0)

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    incident_type: Optional[str] = Field(None, max_length=50)
    severity: Optional[str] = Field(None, max_length=20)
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    occurred_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    delay_minutes: Optional[int] = Field(None, ge=0)
    affected_passengers: Optional[int] = Field(None, ge=0)
    estimated_cost: Optional[float] = Field(None, ge=0)
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = Field(None, max_length=100)

class Incident(IncidentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    resolved_at: Optional[datetime] = None
    reported_at: datetime
    resolution_notes: Optional[str] = None
    resolved_by: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
