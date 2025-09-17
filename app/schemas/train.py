from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.train import TrainType, TrainStatus

class TrainBase(BaseModel):
    train_number: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    train_type: TrainType
    status: TrainStatus = TrainStatus.ACTIVE
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year_manufactured: Optional[int] = Field(None, ge=1800, le=2030)
    max_speed: Optional[float] = Field(None, ge=0, le=500)
    capacity: Optional[int] = Field(None, ge=0)
    length: Optional[float] = Field(None, ge=0)
    width: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=50)
    fuel_consumption: Optional[float] = Field(None, ge=0)
    maintenance_interval: Optional[int] = Field(None, ge=1)
    current_location: Optional[str] = Field(None, max_length=100)
    home_depot: Optional[str] = Field(None, max_length=100)
    assigned_route: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class TrainCreate(TrainBase):
    pass

class TrainUpdate(BaseModel):
    train_number: Optional[str] = Field(None, min_length=1, max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    train_type: Optional[TrainType] = None
    status: Optional[TrainStatus] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year_manufactured: Optional[int] = Field(None, ge=1800, le=2030)
    max_speed: Optional[float] = Field(None, ge=0, le=500)
    capacity: Optional[int] = Field(None, ge=0)
    length: Optional[float] = Field(None, ge=0)
    width: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[str] = Field(None, max_length=50)
    fuel_consumption: Optional[float] = Field(None, ge=0)
    maintenance_interval: Optional[int] = Field(None, ge=1)
    current_location: Optional[str] = Field(None, max_length=100)
    home_depot: Optional[str] = Field(None, max_length=100)
    assigned_route: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None

class Train(TrainBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

class TrainWithDetails(Train):
    maintenance_records: List["MaintenanceRecord"] = []
    performance_metrics: List["PerformanceMetric"] = []

class MaintenanceRecordBase(BaseModel):
    train_id: int
    maintenance_type: str = Field(..., max_length=50)
    description: str
    cost: Optional[float] = Field(None, ge=0)
    duration_hours: Optional[float] = Field(None, ge=0)
    performed_by: Optional[str] = Field(None, max_length=100)
    parts_replaced: Optional[str] = None
    scheduled_date: datetime

class MaintenanceRecordCreate(MaintenanceRecordBase):
    pass

class MaintenanceRecordUpdate(BaseModel):
    maintenance_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    cost: Optional[float] = Field(None, ge=0)
    duration_hours: Optional[float] = Field(None, ge=0)
    performed_by: Optional[str] = Field(None, max_length=100)
    parts_replaced: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None

class MaintenanceRecord(MaintenanceRecordBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    completed_date: Optional[datetime] = None
    created_at: datetime

class PerformanceMetricBase(BaseModel):
    train_id: int
    date_recorded: datetime
    distance_traveled: Optional[float] = Field(None, ge=0)
    fuel_consumed: Optional[float] = Field(None, ge=0)
    average_speed: Optional[float] = Field(None, ge=0)
    max_speed_reached: Optional[float] = Field(None, ge=0)
    on_time_performance: Optional[float] = Field(None, ge=0, le=100)
    passenger_count: Optional[int] = Field(None, ge=0)
    engine_temperature: Optional[float] = None
    brake_efficiency: Optional[float] = Field(None, ge=0, le=100)
    energy_consumption: Optional[float] = Field(None, ge=0)

class PerformanceMetricCreate(PerformanceMetricBase):
    pass

class PerformanceMetric(PerformanceMetricBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
