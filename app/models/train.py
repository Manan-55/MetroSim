from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class TrainType(str, enum.Enum):
    PASSENGER = "passenger"
    FREIGHT = "freight"
    HIGH_SPEED = "high_speed"
    METRO = "metro"
    TRAM = "tram"

class TrainStatus(str, enum.Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RETIRED = "retired"

class Train(Base):
    __tablename__ = "trains"
    
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    train_type = Column(Enum(TrainType), nullable=False)
    status = Column(Enum(TrainStatus), default=TrainStatus.ACTIVE)
    
    # Technical specifications
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    year_manufactured = Column(Integer, nullable=True)
    max_speed = Column(Float, nullable=True)  # km/h
    capacity = Column(Integer, nullable=True)  # passengers or cargo weight
    length = Column(Float, nullable=True)  # meters
    width = Column(Float, nullable=True)  # meters
    height = Column(Float, nullable=True)  # meters
    weight = Column(Float, nullable=True)  # tons
    
    # Operational data
    fuel_type = Column(String(50), nullable=True)  # electric, diesel, hybrid
    fuel_consumption = Column(Float, nullable=True)  # per 100km
    maintenance_interval = Column(Integer, nullable=True)  # days
    last_maintenance = Column(DateTime(timezone=True), nullable=True)
    next_maintenance = Column(DateTime(timezone=True), nullable=True)
    
    # Location and assignment
    current_location = Column(String(100), nullable=True)
    home_depot = Column(String(100), nullable=True)
    assigned_route = Column(String(100), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    created_by_user = relationship("User", back_populates="created_trains")
    schedules = relationship("Schedule", back_populates="train")
    maintenance_records = relationship("MaintenanceRecord", back_populates="train")
    performance_metrics = relationship("PerformanceMetric", back_populates="train")

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # routine, repair, overhaul
    description = Column(Text, nullable=False)
    cost = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    performed_by = Column(String(100), nullable=True)
    parts_replaced = Column(Text, nullable=True)
    
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    train = relationship("Train", back_populates="maintenance_records")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    train_id = Column(Integer, ForeignKey("trains.id"), nullable=False)
    
    # Performance data
    date_recorded = Column(DateTime(timezone=True), nullable=False)
    distance_traveled = Column(Float, nullable=True)  # km
    fuel_consumed = Column(Float, nullable=True)
    average_speed = Column(Float, nullable=True)  # km/h
    max_speed_reached = Column(Float, nullable=True)  # km/h
    on_time_performance = Column(Float, nullable=True)  # percentage
    passenger_count = Column(Integer, nullable=True)
    
    # Technical metrics
    engine_temperature = Column(Float, nullable=True)
    brake_efficiency = Column(Float, nullable=True)
    energy_consumption = Column(Float, nullable=True)  # kWh or liters
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    train = relationship("Train", back_populates="performance_metrics")
