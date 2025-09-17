from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.core.deps import get_current_active_user, get_redis
from app.models.user import User
from app.models.train import Train, TrainStatus
from app.models.schedule import Schedule, ScheduleStatus
from app.models.track import Track, TrackStatus
from app.services.optimization_engine import OptimizationEngine
from pydantic import BaseModel, Field
import json
import redis
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/optimization", tags=["optimization"])

class OptimizationRequest(BaseModel):
    objective: str = Field(..., regex="^(minimize_delays|maximize_efficiency|minimize_fuel|balance_load)$")
    time_horizon_hours: int = Field(24, ge=1, le=168)  # 1 hour to 1 week
    include_train_ids: Optional[List[int]] = None
    include_track_ids: Optional[List[int]] = None
    constraints: Optional[Dict[str, Any]] = None
    priority_schedules: Optional[List[int]] = None

class OptimizationResult(BaseModel):
    optimization_id: str
    status: str
    objective: str
    time_horizon_hours: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

@router.post("/schedule", response_model=OptimizationResult)
async def optimize_schedule(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Start schedule optimization process"""
    optimization_id = str(uuid.uuid4())
    
    # Validate request
    if request.include_train_ids:
        train_count = db.query(Train).filter(
            Train.id.in_(request.include_train_ids),
            Train.status == TrainStatus.ACTIVE
        ).count()
        if train_count != len(request.include_train_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some specified trains are not found or not active"
            )
    
    if request.include_track_ids:
        track_count = db.query(Track).filter(
            Track.id.in_(request.include_track_ids),
            Track.status == TrackStatus.OPERATIONAL
        ).count()
        if track_count != len(request.include_track_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some specified tracks are not found or not operational"
            )
    
    # Create optimization record
    optimization_data = OptimizationResult(
        optimization_id=optimization_id,
        status="running",
        objective=request.objective,
        time_horizon_hours=request.time_horizon_hours,
        created_at=datetime.utcnow()
    )
    
    # Store in Redis
    redis_client.setex(
        f"optimization:{optimization_id}",
        3600,  # 1 hour TTL
        optimization_data.model_dump_json()
    )
    
    # Start background optimization task
    background_tasks.add_task(
        run_optimization,
        optimization_id,
        request,
        current_user.id
    )
    
    logger.info(f"Started optimization {optimization_id} by user {current_user.id}")
    return optimization_data

@router.get("/status/{optimization_id}", response_model=OptimizationResult)
async def get_optimization_status(
    optimization_id: str,
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Get optimization status and results"""
    cached_data = redis_client.get(f"optimization:{optimization_id}")
    if not cached_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Optimization not found or expired"
        )
    
    return OptimizationResult.model_validate_json(cached_data)

@router.get("/history")
async def get_optimization_history(
    limit: int = Field(50, ge=1, le=100),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Get optimization history"""
    # In a real implementation, this would be stored in the database
    # For now, we'll return recent optimizations from Redis
    keys = redis_client.keys("optimization:*")
    optimizations = []
    
    for key in keys[-limit:]:
        data = redis_client.get(key)
        if data:
            try:
                optimization = OptimizationResult.model_validate_json(data)
                optimizations.append(optimization)
            except Exception as e:
                logger.error(f"Error parsing optimization data: {e}")
                continue
    
    # Sort by creation time, newest first
    optimizations.sort(key=lambda x: x.created_at, reverse=True)
    return optimizations

@router.post("/routes/optimize")
async def optimize_routes(
    start_date: datetime,
    end_date: datetime,
    objective: str = Field(..., regex="^(minimize_distance|minimize_time|maximize_capacity)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Optimize routes for given time period"""
    if end_date <= start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    if (end_date - start_date).days > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Time period cannot exceed 7 days"
        )
    
    # Get schedules in the time period
    schedules = db.query(Schedule).filter(
        and_(
            Schedule.scheduled_departure >= start_date,
            Schedule.scheduled_departure <= end_date,
            Schedule.status.in_([ScheduleStatus.SCHEDULED, ScheduleStatus.ACTIVE])
        )
    ).all()
    
    if not schedules:
        return {
            "message": "No schedules found in the specified time period",
            "optimized_routes": []
        }
    
    # Initialize optimization engine
    engine = OptimizationEngine()
    
    try:
        # Run route optimization
        optimized_routes = engine.optimize_routes(schedules, objective)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "objective": objective,
            "total_schedules": len(schedules),
            "optimized_routes": optimized_routes,
            "optimization_summary": {
                "total_distance_saved": sum(route.get("distance_saved", 0) for route in optimized_routes),
                "total_time_saved": sum(route.get("time_saved", 0) for route in optimized_routes),
                "efficiency_improvement": engine.calculate_efficiency_improvement(schedules, optimized_routes)
            }
        }
    
    except Exception as e:
        logger.error(f"Route optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Route optimization failed"
        )

@router.post("/capacity/balance")
async def balance_capacity(
    time_window_hours: int = Field(24, ge=1, le=72),
    target_utilization: float = Field(0.8, ge=0.1, le=1.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Balance train capacity across routes"""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=time_window_hours)
    
    # Get active schedules in the time window
    schedules = db.query(Schedule).filter(
        and_(
            Schedule.scheduled_departure >= start_time,
            Schedule.scheduled_departure <= end_time,
            Schedule.status.in_([ScheduleStatus.SCHEDULED, ScheduleStatus.ACTIVE])
        )
    ).all()
    
    # Get active trains
    trains = db.query(Train).filter(Train.status == TrainStatus.ACTIVE).all()
    
    if not schedules or not trains:
        return {
            "message": "Insufficient data for capacity balancing",
            "recommendations": []
        }
    
    # Initialize optimization engine
    engine = OptimizationEngine()
    
    try:
        # Run capacity balancing
        recommendations = engine.balance_capacity(schedules, trains, target_utilization)
        
        return {
            "time_window_hours": time_window_hours,
            "target_utilization": target_utilization,
            "total_schedules": len(schedules),
            "total_trains": len(trains),
            "recommendations": recommendations,
            "summary": {
                "total_recommendations": len(recommendations),
                "potential_capacity_increase": sum(r.get("capacity_increase", 0) for r in recommendations),
                "estimated_efficiency_gain": engine.calculate_capacity_efficiency_gain(recommendations)
            }
        }
    
    except Exception as e:
        logger.error(f"Capacity balancing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Capacity balancing failed"
        )

@router.get("/recommendations")
async def get_optimization_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get general optimization recommendations"""
    # Analyze current system state
    now = datetime.utcnow()
    today = now.date()
    
    # Get today's schedules
    today_schedules = db.query(Schedule).filter(
        func.date(Schedule.scheduled_departure) == today
    ).all()
    
    # Get delayed schedules
    delayed_schedules = [s for s in today_schedules if s.status == ScheduleStatus.DELAYED]
    
    # Get underutilized trains
    underutilized_trains = db.query(Train).filter(
        and_(
            Train.status == TrainStatus.ACTIVE,
            Train.id.notin_([s.train_id for s in today_schedules])
        )
    ).all()
    
    # Get tracks with low utilization
    track_utilization = db.query(
        Track.id,
        Track.name,
        Track.current_usage
    ).filter(
        and_(
            Track.status == TrackStatus.OPERATIONAL,
            Track.current_usage < 50  # Less than 50% utilization
        )
    ).all()
    
    recommendations = []
    
    # Delay reduction recommendations
    if delayed_schedules:
        recommendations.append({
            "type": "delay_reduction",
            "priority": "high",
            "title": "Address Schedule Delays",
            "description": f"{len(delayed_schedules)} schedules are currently delayed",
            "action": "Consider rerouting or reassigning trains to reduce delays",
            "affected_schedules": len(delayed_schedules)
        })
    
    # Train utilization recommendations
    if underutilized_trains:
        recommendations.append({
            "type": "train_utilization",
            "priority": "medium",
            "title": "Improve Train Utilization",
            "description": f"{len(underutilized_trains)} trains are not scheduled today",
            "action": "Consider adding additional schedules or maintenance windows",
            "available_trains": len(underutilized_trains)
        })
    
    # Track utilization recommendations
    if track_utilization:
        recommendations.append({
            "type": "track_utilization",
            "priority": "low",
            "title": "Optimize Track Usage",
            "description": f"{len(track_utilization)} tracks have low utilization",
            "action": "Consider redistributing traffic to balance track usage",
            "underutilized_tracks": len(track_utilization)
        })
    
    # Maintenance scheduling recommendations
    upcoming_maintenance = db.query(Train).filter(
        and_(
            Train.next_maintenance <= now + timedelta(days=7),
            Train.status == TrainStatus.ACTIVE
        )
    ).count()
    
    if upcoming_maintenance > 0:
        recommendations.append({
            "type": "maintenance_scheduling",
            "priority": "high",
            "title": "Schedule Maintenance",
            "description": f"{upcoming_maintenance} trains need maintenance within 7 days",
            "action": "Schedule maintenance windows to avoid service disruption",
            "trains_needing_maintenance": upcoming_maintenance
        })
    
    return {
        "generated_at": now.isoformat(),
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "system_overview": {
            "total_schedules_today": len(today_schedules),
            "delayed_schedules": len(delayed_schedules),
            "available_trains": len(underutilized_trains),
            "underutilized_tracks": len(track_utilization)
        }
    }

async def run_optimization(optimization_id: str, request: OptimizationRequest, user_id: int):
    """Background task to run optimization"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    try:
        # Update status to running
        optimization_data = OptimizationResult(
            optimization_id=optimization_id,
            status="running",
            objective=request.objective,
            time_horizon_hours=request.time_horizon_hours,
            created_at=datetime.utcnow()
        )
        
        redis_client.setex(
            f"optimization:{optimization_id}",
            3600,
            optimization_data.model_dump_json()
        )
        
        # Initialize optimization engine
        engine = OptimizationEngine()
        
        # Get data for optimization
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=request.time_horizon_hours)
        
        schedules_query = db.query(Schedule).filter(
            and_(
                Schedule.scheduled_departure >= start_time,
                Schedule.scheduled_departure <= end_time,
                Schedule.status.in_([ScheduleStatus.SCHEDULED, ScheduleStatus.ACTIVE])
            )
        )
        
        if request.include_train_ids:
            schedules_query = schedules_query.filter(Schedule.train_id.in_(request.include_train_ids))
        
        if request.include_track_ids:
            schedules_query = schedules_query.filter(Schedule.track_id.in_(request.include_track_ids))
        
        schedules = schedules_query.all()
        
        # Run optimization
        results = engine.optimize_schedules(
            schedules=schedules,
            objective=request.objective,
            constraints=request.constraints or {},
            priority_schedules=request.priority_schedules or []
        )
        
        # Update with results
        optimization_data.status = "completed"
        optimization_data.completed_at = datetime.utcnow()
        optimization_data.results = results
        
        redis_client.setex(
            f"optimization:{optimization_id}",
            3600,
            optimization_data.model_dump_json()
        )
        
        logger.info(f"Optimization {optimization_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Optimization {optimization_id} failed: {e}")
        
        # Update with error
        optimization_data.status = "failed"
        optimization_data.completed_at = datetime.utcnow()
        optimization_data.error_message = str(e)
        
        redis_client.setex(
            f"optimization:{optimization_id}",
            3600,
            optimization_data.model_dump_json()
        )
    
    finally:
        db.close()
