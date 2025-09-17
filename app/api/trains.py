from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.database import get_db
from app.core.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.train import Train, MaintenanceRecord, PerformanceMetric, TrainStatus, TrainType
from app.schemas.train import (
    Train as TrainSchema, TrainCreate, TrainUpdate, TrainWithDetails,
    MaintenanceRecord as MaintenanceRecordSchema, MaintenanceRecordCreate, MaintenanceRecordUpdate,
    PerformanceMetric as PerformanceMetricSchema, PerformanceMetricCreate
)
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trains", tags=["trains"])

@router.get("/", response_model=List[TrainSchema])
async def get_trains(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    train_type: Optional[TrainType] = None,
    status: Optional[TrainStatus] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all trains with optional filtering"""
    query = db.query(Train)
    
    if train_type:
        query = query.filter(Train.train_type == train_type)
    
    if status:
        query = query.filter(Train.status == status)
    
    if search:
        query = query.filter(
            Train.name.ilike(f"%{search}%") |
            Train.train_number.ilike(f"%{search}%") |
            Train.manufacturer.ilike(f"%{search}%")
        )
    
    trains = query.offset(skip).limit(limit).all()
    return trains

@router.get("/{train_id}", response_model=TrainWithDetails)
async def get_train(
    train_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific train with details"""
    train = db.query(Train).options(
        joinedload(Train.maintenance_records),
        joinedload(Train.performance_metrics)
    ).filter(Train.id == train_id).first()
    
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    return train

@router.post("/", response_model=TrainSchema, status_code=status.HTTP_201_CREATED)
async def create_train(
    train_data: TrainCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new train"""
    # Check if train number already exists
    existing_train = db.query(Train).filter(Train.train_number == train_data.train_number).first()
    if existing_train:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Train number already exists"
        )
    
    train = Train(**train_data.model_dump(), created_by=current_user.id)
    db.add(train)
    db.commit()
    db.refresh(train)
    
    logger.info(f"Train {train.train_number} created by user {current_user.id}")
    return train

@router.put("/{train_id}", response_model=TrainSchema)
async def update_train(
    train_id: int,
    train_data: TrainUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a train"""
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    # Check if train number is being changed and already exists
    if train_data.train_number and train_data.train_number != train.train_number:
        existing_train = db.query(Train).filter(Train.train_number == train_data.train_number).first()
        if existing_train:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Train number already exists"
            )
    
    update_data = train_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(train, field, value)
    
    train.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(train)
    
    logger.info(f"Train {train.train_number} updated by user {current_user.id}")
    return train

@router.delete("/{train_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_train(
    train_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a train"""
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    db.delete(train)
    db.commit()
    
    logger.info(f"Train {train.train_number} deleted by user {current_user.id}")

# Maintenance Records endpoints
@router.get("/{train_id}/maintenance", response_model=List[MaintenanceRecordSchema])
async def get_train_maintenance_records(
    train_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get maintenance records for a train"""
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.train_id == train_id
    ).offset(skip).limit(limit).all()
    
    return records

@router.post("/{train_id}/maintenance", response_model=MaintenanceRecordSchema, status_code=status.HTTP_201_CREATED)
async def create_maintenance_record(
    train_id: int,
    record_data: MaintenanceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a maintenance record for a train"""
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    record = MaintenanceRecord(**record_data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record

@router.put("/maintenance/{record_id}", response_model=MaintenanceRecordSchema)
async def update_maintenance_record(
    record_id: int,
    record_data: MaintenanceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a maintenance record"""
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found"
        )
    
    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    
    return record

# Performance Metrics endpoints
@router.get("/{train_id}/performance", response_model=List[PerformanceMetricSchema])
async def get_train_performance_metrics(
    train_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get performance metrics for a train"""
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    query = db.query(PerformanceMetric).filter(PerformanceMetric.train_id == train_id)
    
    if start_date:
        query = query.filter(PerformanceMetric.date_recorded >= start_date)
    if end_date:
        query = query.filter(PerformanceMetric.date_recorded <= end_date)
    
    metrics = query.offset(skip).limit(limit).all()
    return metrics

@router.post("/{train_id}/performance", response_model=PerformanceMetricSchema, status_code=status.HTTP_201_CREATED)
async def create_performance_metric(
    train_id: int,
    metric_data: PerformanceMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a performance metric for a train"""
    train = db.query(Train).filter(Train.id == train_id).first()
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Train not found"
        )
    
    metric = PerformanceMetric(**metric_data.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    
    return metric

@router.get("/statistics/overview")
async def get_trains_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get overview statistics for all trains"""
    total_trains = db.query(Train).count()
    active_trains = db.query(Train).filter(Train.status == TrainStatus.ACTIVE).count()
    maintenance_trains = db.query(Train).filter(Train.status == TrainStatus.MAINTENANCE).count()
    
    # Trains needing maintenance soon (within 30 days)
    upcoming_maintenance = db.query(Train).filter(
        Train.next_maintenance <= datetime.utcnow() + timedelta(days=30)
    ).count()
    
    return {
        "total_trains": total_trains,
        "active_trains": active_trains,
        "maintenance_trains": maintenance_trains,
        "upcoming_maintenance": upcoming_maintenance,
        "train_types": {
            "passenger": db.query(Train).filter(Train.train_type == TrainType.PASSENGER).count(),
            "freight": db.query(Train).filter(Train.train_type == TrainType.FREIGHT).count(),
            "high_speed": db.query(Train).filter(Train.train_type == TrainType.HIGH_SPEED).count(),
            "metro": db.query(Train).filter(Train.train_type == TrainType.METRO).count(),
            "tram": db.query(Train).filter(Train.train_type == TrainType.TRAM).count(),
        }
    }
