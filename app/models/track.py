from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class TrackType(str, enum.Enum):
    MAIN_LINE = "main_line"
    BRANCH_LINE = "branch_line"
    SIDING = "siding"
    YARD = "yard"
    TERMINAL = "terminal"

class TrackStatus(str, enum.Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"
    UNDER_CONSTRUCTION = "under_construction"

class Track(Base):
    __tablename__ = "tracks"
    
    id = Column(Integer, primary_key=True, index=True)
    track_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    track_type = Column(Enum(TrackType), nullable=False)
    status = Column(Enum(TrackStatus), default=TrackStatus.OPERATIONAL)
    
    # Geographic data
    start_station = Column(String(100), nullable=False)
    end_station = Column(String(100), nullable=False)
    length = Column(Float, nullable=False)  # km
    gauge = Column(Float, nullable=True)  # mm (track gauge)
    
    # Technical specifications
    max_speed = Column(Float, nullable=True)  # km/h
    grade = Column(Float, nullable=True)  # percentage
    curvature = Column(Float, nullable=True)  # degrees
    electrified = Column(Boolean, default=False)
    voltage = Column(Integer, nullable=True)  # volts
    signaling_system = Column(String(50), nullable=True)
    
    # Capacity and usage
    capacity_trains_per_hour = Column(Integer, nullable=True)
    current_usage = Column(Float, nullable=True)  # percentage
    
    # Maintenance data
    last_inspection = Column(DateTime(timezone=True), nullable=True)
    next_inspection = Column(DateTime(timezone=True), nullable=True)
    condition_rating = Column(Float, nullable=True)  # 1-10 scale
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    schedules = relationship("Schedule", back_populates="track")
    track_segments = relationship("TrackSegment", back_populates="track")

class TrackSegment(Base):
    __tablename__ = "track_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)
    segment_number = Column(Integer, nullable=False)
    
    # Segment details
    start_km = Column(Float, nullable=False)
    end_km = Column(Float, nullable=False)
    length = Column(Float, nullable=False)  # km
    
    # Geographic coordinates
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    end_latitude = Column(Float, nullable=True)
    end_longitude = Column(Float, nullable=True)
    
    # Segment characteristics
    max_speed = Column(Float, nullable=True)  # km/h
    grade = Column(Float, nullable=True)  # percentage
    curvature = Column(Float, nullable=True)  # degrees
    bridges = Column(Integer, default=0)
    tunnels = Column(Integer, default=0)
    level_crossings = Column(Integer, default=0)
    
    # Condition data
    condition_rating = Column(Float, nullable=True)  # 1-10 scale
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    track = relationship("Track", back_populates="track_segments")

class Station(Base):
    __tablename__ = "stations"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    
    # Location data
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)  # meters above sea level
    
    # Station characteristics
    station_type = Column(String(50), nullable=True)  # terminal, junction, halt
    platforms = Column(Integer, default=1)
    tracks = Column(Integer, default=1)
    electrified = Column(Boolean, default=False)
    
    # Facilities
    has_parking = Column(Boolean, default=False)
    has_restaurant = Column(Boolean, default=False)
    has_waiting_room = Column(Boolean, default=False)
    has_ticket_office = Column(Boolean, default=False)
    wheelchair_accessible = Column(Boolean, default=False)
    
    # Operational data
    opened_date = Column(DateTime(timezone=True), nullable=True)
    daily_passengers = Column(Integer, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    departure_schedules = relationship("Schedule", foreign_keys="Schedule.departure_station_id", back_populates="departure_station")
    arrival_schedules = relationship("Schedule", foreign_keys="Schedule.arrival_station_id", back_populates="arrival_station")
