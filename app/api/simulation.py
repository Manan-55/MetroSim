from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.core.deps import get_current_active_user, get_redis
from app.models.user import User
from app.models.train import Train, TrainStatus
from app.models.schedule import Schedule, ScheduleStatus
from app.models.track import Track
from app.services.simulation_engine import SimulationEngine
from pydantic import BaseModel, Field
import json
import redis
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/simulation", tags=["simulation"])

class SimulationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    simulation_type: str = Field(..., regex="^(schedule|incident|capacity|weather)$")
    duration_hours: int = Field(24, ge=1, le=168)  # 1 hour to 1 week
    time_step_seconds: float = Field(60.0, ge=1.0, le=3600.0)  # 1 second to 1 hour
    parameters: Dict[str, Any] = Field(default_factory=dict)
    include_train_ids: Optional[List[int]] = None
    include_track_ids: Optional[List[int]] = None
    scenario_data: Optional[Dict[str, Any]] = None

class SimulationResult(BaseModel):
    simulation_id: str
    name: str
    simulation_type: str
    status: str
    duration_hours: int
    time_step_seconds: float
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class ScenarioTemplate(BaseModel):
    name: str
    description: str
    simulation_type: str
    default_parameters: Dict[str, Any]
    required_inputs: List[str]

@router.post("/start", response_model=SimulationResult)
async def start_simulation(
    request: SimulationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Start a new simulation"""
    simulation_id = str(uuid.uuid4())
    
    # Validate request
    if request.include_train_ids:
        train_count = db.query(Train).filter(
            Train.id.in_(request.include_train_ids)
        ).count()
        if train_count != len(request.include_train_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some specified trains are not found"
            )
    
    if request.include_track_ids:
        track_count = db.query(Track).filter(
            Track.id.in_(request.include_track_ids)
        ).count()
        if track_count != len(request.include_track_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some specified tracks are not found"
            )
    
    # Create simulation record
    simulation_data = SimulationResult(
        simulation_id=simulation_id,
        name=request.name,
        simulation_type=request.simulation_type,
        status="queued",
        duration_hours=request.duration_hours,
        time_step_seconds=request.time_step_seconds,
        created_at=datetime.utcnow()
    )
    
    # Store in Redis
    redis_client.setex(
        f"simulation:{simulation_id}",
        7200,  # 2 hours TTL
        simulation_data.model_dump_json()
    )
    
    # Start background simulation task
    background_tasks.add_task(
        run_simulation,
        simulation_id,
        request,
        current_user.id
    )
    
    logger.info(f"Started simulation {simulation_id} by user {current_user.id}")
    return simulation_data

@router.get("/status/{simulation_id}", response_model=SimulationResult)
async def get_simulation_status(
    simulation_id: str,
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Get simulation status and results"""
    cached_data = redis_client.get(f"simulation:{simulation_id}")
    if not cached_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found or expired"
        )
    
    return SimulationResult.model_validate_json(cached_data)

@router.post("/stop/{simulation_id}")
async def stop_simulation(
    simulation_id: str,
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Stop a running simulation"""
    cached_data = redis_client.get(f"simulation:{simulation_id}")
    if not cached_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found or expired"
        )
    
    simulation_data = SimulationResult.model_validate_json(cached_data)
    
    if simulation_data.status not in ["queued", "running"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is not running"
        )
    
    # Update status to stopped
    simulation_data.status = "stopped"
    simulation_data.completed_at = datetime.utcnow()
    
    redis_client.setex(
        f"simulation:{simulation_id}",
        7200,
        simulation_data.model_dump_json()
    )
    
    # Set stop flag
    redis_client.setex(f"simulation:{simulation_id}:stop", 300, "true")
    
    logger.info(f"Simulation {simulation_id} stopped by user {current_user.id}")
    return {"message": "Simulation stop requested"}

@router.get("/history")
async def get_simulation_history(
    limit: int = Field(50, ge=1, le=100),
    simulation_type: Optional[str] = None,
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Get simulation history"""
    keys = redis_client.keys("simulation:*")
    simulations = []
    
    for key in keys:
        if ":stop" in key:  # Skip stop flags
            continue
            
        data = redis_client.get(key)
        if data:
            try:
                simulation = SimulationResult.model_validate_json(data)
                if simulation_type and simulation.simulation_type != simulation_type:
                    continue
                simulations.append(simulation)
            except Exception as e:
                logger.error(f"Error parsing simulation data: {e}")
                continue
    
    # Sort by creation time, newest first
    simulations.sort(key=lambda x: x.created_at, reverse=True)
    return simulations[:limit]

@router.get("/templates", response_model=List[ScenarioTemplate])
async def get_scenario_templates(
    current_user: User = Depends(get_current_active_user)
):
    """Get available simulation scenario templates"""
    templates = [
        ScenarioTemplate(
            name="Schedule Delay Impact",
            description="Simulate the impact of schedule delays on the entire network",
            simulation_type="schedule",
            default_parameters={
                "delay_probability": 0.1,
                "average_delay_minutes": 15,
                "max_delay_minutes": 60,
                "cascade_effect": True
            },
            required_inputs=["affected_schedules", "delay_duration"]
        ),
        ScenarioTemplate(
            name="Track Maintenance Impact",
            description="Simulate the impact of track maintenance on train operations",
            simulation_type="incident",
            default_parameters={
                "maintenance_duration_hours": 8,
                "affected_capacity_percentage": 0.5,
                "rerouting_enabled": True
            },
            required_inputs=["track_id", "maintenance_start_time"]
        ),
        ScenarioTemplate(
            name="Peak Hour Capacity",
            description="Simulate train operations during peak hours with increased demand",
            simulation_type="capacity",
            default_parameters={
                "demand_multiplier": 1.5,
                "peak_start_hour": 7,
                "peak_end_hour": 9,
                "capacity_threshold": 0.9
            },
            required_inputs=["peak_hours", "demand_increase"]
        ),
        ScenarioTemplate(
            name="Weather Impact",
            description="Simulate the impact of adverse weather conditions on operations",
            simulation_type="weather",
            default_parameters={
                "weather_type": "heavy_rain",
                "speed_reduction_percentage": 0.3,
                "visibility_impact": True,
                "duration_hours": 4
            },
            required_inputs=["weather_conditions", "affected_area"]
        ),
        ScenarioTemplate(
            name="Equipment Failure",
            description="Simulate the impact of train equipment failures",
            simulation_type="incident",
            default_parameters={
                "failure_probability": 0.05,
                "repair_time_hours": 2,
                "replacement_available": True,
                "passenger_transfer_time": 30
            },
            required_inputs=["train_id", "failure_type"]
        ),
        ScenarioTemplate(
            name="Network Optimization",
            description="Simulate optimized schedules and routing",
            simulation_type="schedule",
            default_parameters={
                "optimization_objective": "minimize_delays",
                "allow_rescheduling": True,
                "max_schedule_change_minutes": 30
            },
            required_inputs=["optimization_parameters"]
        )
    ]
    
    return templates

@router.post("/scenarios/custom")
async def create_custom_scenario(
    name: str = Field(..., min_length=1, max_length=100),
    description: str = Field(..., min_length=1, max_length=500),
    simulation_type: str = Field(..., regex="^(schedule|incident|capacity|weather)$"),
    parameters: Dict[str, Any] = Field(...),
    duration_hours: int = Field(24, ge=1, le=168),
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Create and run a custom simulation scenario"""
    # Create simulation request
    request = SimulationRequest(
        name=name,
        simulation_type=simulation_type,
        duration_hours=duration_hours,
        parameters=parameters,
        scenario_data={"description": description, "custom": True}
    )
    
    # Start simulation
    return await start_simulation(request, background_tasks, db, redis_client, current_user)

@router.get("/results/{simulation_id}/export")
async def export_simulation_results(
    simulation_id: str,
    format: str = Field("json", regex="^(json|csv)$"),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Export simulation results in specified format"""
    cached_data = redis_client.get(f"simulation:{simulation_id}")
    if not cached_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found or expired"
        )
    
    simulation_data = SimulationResult.model_validate_json(cached_data)
    
    if simulation_data.status != "completed" or not simulation_data.results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation not completed or no results available"
        )
    
    if format == "json":
        return {
            "simulation_info": {
                "id": simulation_data.simulation_id,
                "name": simulation_data.name,
                "type": simulation_data.simulation_type,
                "duration_hours": simulation_data.duration_hours,
                "completed_at": simulation_data.completed_at
            },
            "results": simulation_data.results
        }
    
    elif format == "csv":
        # Convert results to CSV format
        import csv
        import io
        
        output = io.StringIO()
        
        # Extract key metrics for CSV
        if "timeline" in simulation_data.results:
            writer = csv.writer(output)
            writer.writerow(["timestamp", "metric", "value"])
            
            for timestamp, metrics in simulation_data.results["timeline"].items():
                for metric, value in metrics.items():
                    writer.writerow([timestamp, metric, value])
        
        return {
            "format": "csv",
            "data": output.getvalue()
        }

async def run_simulation(simulation_id: str, request: SimulationRequest, user_id: int):
    """Background task to run simulation"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    try:
        # Update status to running
        simulation_data = SimulationResult(
            simulation_id=simulation_id,
            name=request.name,
            simulation_type=request.simulation_type,
            status="running",
            duration_hours=request.duration_hours,
            time_step_seconds=request.time_step_seconds,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow()
        )
        
        redis_client.setex(
            f"simulation:{simulation_id}",
            7200,
            simulation_data.model_dump_json()
        )
        
        # Initialize simulation engine
        engine = SimulationEngine()
        
        # Get data for simulation
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=request.duration_hours)
        
        # Get relevant schedules
        schedules_query = db.query(Schedule).filter(
            and_(
                Schedule.scheduled_departure >= start_time,
                Schedule.scheduled_departure <= end_time
            )
        )
        
        if request.include_train_ids:
            schedules_query = schedules_query.filter(Schedule.train_id.in_(request.include_train_ids))
        
        if request.include_track_ids:
            schedules_query = schedules_query.filter(Schedule.track_id.in_(request.include_track_ids))
        
        schedules = schedules_query.all()
        
        # Get trains and tracks
        trains = db.query(Train).all()
        tracks = db.query(Track).all()
        
        # Run simulation with progress updates
        def progress_callback(progress: float):
            simulation_data.progress_percentage = progress
            redis_client.setex(
                f"simulation:{simulation_id}",
                7200,
                simulation_data.model_dump_json()
            )
            
            # Check for stop signal
            if redis_client.get(f"simulation:{simulation_id}:stop"):
                return False  # Signal to stop simulation
            return True
        
        # Run simulation
        results = engine.run_simulation(
            simulation_type=request.simulation_type,
            schedules=schedules,
            trains=trains,
            tracks=tracks,
            duration_hours=request.duration_hours,
            time_step_seconds=request.time_step_seconds,
            parameters=request.parameters,
            scenario_data=request.scenario_data,
            progress_callback=progress_callback
        )
        
        # Update with results
        simulation_data.status = "completed"
        simulation_data.completed_at = datetime.utcnow()
        simulation_data.progress_percentage = 100.0
        simulation_data.results = results
        
        redis_client.setex(
            f"simulation:{simulation_id}",
            7200,
            simulation_data.model_dump_json()
        )
        
        # Clean up stop flag
        redis_client.delete(f"simulation:{simulation_id}:stop")
        
        logger.info(f"Simulation {simulation_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Simulation {simulation_id} failed: {e}")
        
        # Update with error
        simulation_data.status = "failed"
        simulation_data.completed_at = datetime.utcnow()
        simulation_data.error_message = str(e)
        
        redis_client.setex(
            f"simulation:{simulation_id}",
            7200,
            simulation_data.model_dump_json()
        )
        
        # Clean up stop flag
        redis_client.delete(f"simulation:{simulation_id}:stop")
    
    finally:
        db.close()
