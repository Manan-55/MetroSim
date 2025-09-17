from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class ScheduleStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DELAYED = "delayed"

class ScheduleType(str, enum.Enum):
    REGULAR = "regular"
    EXPRESS = "express"
    FREIGHT = "freight"
    MAINTENANCE = "maintenance"
    SPECIAL = "special"

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    schedule_type = Column(Enum(ScheduleType), nullable=False)
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.SCHEDULED)
    
    # Train and route assignment
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    departure_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    arrival_station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    
    # Timing
    scheduled_departure = Column(DateTime(timezone=True), nullable=False)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=False)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    
    # Schedule details
    distance = Column(Float, nullable=True)  # km
    estimated_duration = Column(Integer, nullable=True)  # minutes
    actual_duration = Column(Integer, nullable=True)  # minutes
    max_speed = Column(Float, nullable=True)  # km/h
    average_speed = Column(Float, nullable=True)  # km/h
    
    # Passenger/cargo information
    passenger_capacity = Column(Integer, nullable=True)
    passenger_count = Column(Integer, nullable=True)
    cargo_weight = Column(Float, nullable=True)  # tons
    
    # Operational data
    priority = Column(Integer, default=5)  # 1-10 scale
    recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # daily, weekly, monthly
    
    # Performance metrics
    on_time_performance = Column(Float, nullable=True)  # percentage
    fuel_consumption = Column(Float, nullable=True)
    energy_consumption = Column(Float, nullable=True)  # kWh
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    train = relationship("Train", back_populates="schedules")
    track = relationship("Track", back_populates="schedules")
    departure_station = relationship("Station", foreign_keys=[departure_station_id], back_populates="departure_schedules")
    arrival_station = relationship("Station", foreign_keys=[arrival_station_id], back_populates="arrival_schedules")
    created_by_user = relationship("User", back_populates="created_schedules")
    schedule_stops = relationship("ScheduleStop", back_populates="schedule")
    incidents = relationship("Incident", back_populates="schedule")

class ScheduleStop(Base):
    __tablename__ = "schedule_stops"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    station_id = Column(Integer, ForeignKey("stations.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)
    
    # Timing
    scheduled_arrival = Column(DateTime(timezone=True), nullable=True)
    scheduled_departure = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
    
    # Stop details
    platform = Column(String(10), nullable=True)
    stop_duration = Column(Integer, nullable=True)  # minutes
    passenger_boarding = Column(Integer, nullable=True)
    passenger_alighting = Column(Integer, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    schedule = relationship("Schedule", back_populates="schedule_stops")
    station = relationship("Station")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=True)
    
    # Incident details
    incident_type = Column(String(50), nullable=False)  # delay, breakdown, accident, weather
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Timing
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Impact
    delay_minutes = Column(Integer, nullable=True)
    affected_passengers = Column(Integer, nullable=True)
    estimated_cost = Column(Float, nullable=True)
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    schedule = relationship("Schedule", back_populates="incidents")
    train = relationship("Train")
    track = relationship("Track")
