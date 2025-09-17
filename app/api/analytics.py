from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.core.deps import get_current_active_user, get_redis
from app.models.user import User
from app.models.train import Train, PerformanceMetric, TrainType, TrainStatus
from app.models.schedule import Schedule, ScheduleStatus, Incident
from app.models.track import Track, TrackStatus
from app.config import settings
import json
import redis
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard_analytics(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive dashboard analytics"""
    cache_key = "dashboard_analytics"
    
    # Try to get from cache first
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    
    # Calculate analytics
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # Train statistics
    total_trains = db.query(Train).count()
    active_trains = db.query(Train).filter(Train.status == TrainStatus.ACTIVE).count()
    maintenance_trains = db.query(Train).filter(Train.status == TrainStatus.MAINTENANCE).count()
    
    # Schedule statistics
    total_schedules_today = db.query(Schedule).filter(
        func.date(Schedule.scheduled_departure) == today
    ).count()
    
    completed_schedules_today = db.query(Schedule).filter(
        and_(
            func.date(Schedule.scheduled_departure) == today,
            Schedule.status == ScheduleStatus.COMPLETED
        )
    ).count()
    
    delayed_schedules_today = db.query(Schedule).filter(
        and_(
            func.date(Schedule.scheduled_departure) == today,
            Schedule.status == ScheduleStatus.DELAYED
        )
    ).count()
    
    # On-time performance
    on_time_schedules = db.query(Schedule).filter(
        and_(
            Schedule.scheduled_departure >= week_ago,
            Schedule.actual_departure.isnot(None),
            Schedule.actual_departure <= Schedule.scheduled_departure + timedelta(minutes=5)
        )
    ).count()
    
    total_completed_schedules = db.query(Schedule).filter(
        and_(
            Schedule.scheduled_departure >= week_ago,
            Schedule.actual_departure.isnot(None)
        )
    ).count()
    
    on_time_percentage = (on_time_schedules / total_completed_schedules * 100) if total_completed_schedules > 0 else 0
    
    # Incident statistics
    incidents_today = db.query(Incident).filter(
        func.date(Incident.occurred_at) == today
    ).count()
    
    incidents_this_week = db.query(Incident).filter(
        Incident.occurred_at >= week_ago
    ).count()
    
    # Track utilization
    total_tracks = db.query(Track).count()
    operational_tracks = db.query(Track).filter(Track.status == TrackStatus.OPERATIONAL).count()
    
    # Average performance metrics
    avg_performance = db.query(
        func.avg(PerformanceMetric.on_time_performance).label('avg_on_time'),
        func.avg(PerformanceMetric.fuel_consumed).label('avg_fuel'),
        func.avg(PerformanceMetric.average_speed).label('avg_speed')
    ).filter(PerformanceMetric.date_recorded >= week_ago).first()
    
    analytics_data = {
        "trains": {
            "total": total_trains,
            "active": active_trains,
            "maintenance": maintenance_trains,
            "utilization_rate": (active_trains / total_trains * 100) if total_trains > 0 else 0
        },
        "schedules": {
            "today_total": total_schedules_today,
            "today_completed": completed_schedules_today,
            "today_delayed": delayed_schedules_today,
            "completion_rate": (completed_schedules_today / total_schedules_today * 100) if total_schedules_today > 0 else 0
        },
        "performance": {
            "on_time_percentage": round(on_time_percentage, 2),
            "avg_on_time_performance": round(avg_performance.avg_on_time or 0, 2),
            "avg_fuel_consumption": round(avg_performance.avg_fuel or 0, 2),
            "avg_speed": round(avg_performance.avg_speed or 0, 2)
        },
        "incidents": {
            "today": incidents_today,
            "this_week": incidents_this_week
        },
        "infrastructure": {
            "total_tracks": total_tracks,
            "operational_tracks": operational_tracks,
            "track_availability": (operational_tracks / total_tracks * 100) if total_tracks > 0 else 0
        },
        "last_updated": now.isoformat()
    }
    
    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(analytics_data, default=str))
    
    return analytics_data

@router.get("/performance/trends")
async def get_performance_trends(
    days: int = Query(30, ge=1, le=365),
    train_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get performance trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        func.date(PerformanceMetric.date_recorded).label('date'),
        func.avg(PerformanceMetric.on_time_performance).label('avg_on_time'),
        func.avg(PerformanceMetric.fuel_consumed).label('avg_fuel'),
        func.avg(PerformanceMetric.average_speed).label('avg_speed'),
        func.count(PerformanceMetric.id).label('record_count')
    ).filter(PerformanceMetric.date_recorded >= start_date)
    
    if train_id:
        query = query.filter(PerformanceMetric.train_id == train_id)
    
    trends = query.group_by(func.date(PerformanceMetric.date_recorded)).order_by('date').all()
    
    return [
        {
            "date": trend.date.isoformat(),
            "avg_on_time_performance": round(trend.avg_on_time or 0, 2),
            "avg_fuel_consumption": round(trend.avg_fuel or 0, 2),
            "avg_speed": round(trend.avg_speed or 0, 2),
            "record_count": trend.record_count
        }
        for trend in trends
    ]

@router.get("/schedules/analysis")
async def get_schedule_analysis(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed schedule analysis"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Schedule status distribution
    status_distribution = db.query(
        Schedule.status,
        func.count(Schedule.id).label('count')
    ).filter(
        and_(
            Schedule.scheduled_departure >= start_date,
            Schedule.scheduled_departure <= end_date
        )
    ).group_by(Schedule.status).all()
    
    # Delay analysis
    delay_analysis = db.query(
        func.avg(
            func.extract('epoch', Schedule.actual_departure - Schedule.scheduled_departure) / 60
        ).label('avg_delay_minutes'),
        func.max(
            func.extract('epoch', Schedule.actual_departure - Schedule.scheduled_departure) / 60
        ).label('max_delay_minutes'),
        func.count(Schedule.id).label('total_schedules')
    ).filter(
        and_(
            Schedule.scheduled_departure >= start_date,
            Schedule.scheduled_departure <= end_date,
            Schedule.actual_departure.isnot(None)
        )
    ).first()
    
    # Route performance
    route_performance = db.query(
        Schedule.departure_station_id,
        Schedule.arrival_station_id,
        func.count(Schedule.id).label('total_trips'),
        func.avg(Schedule.on_time_performance).label('avg_on_time'),
        func.avg(
            func.extract('epoch', Schedule.actual_departure - Schedule.scheduled_departure) / 60
        ).label('avg_delay')
    ).filter(
        and_(
            Schedule.scheduled_departure >= start_date,
            Schedule.scheduled_departure <= end_date,
            Schedule.actual_departure.isnot(None)
        )
    ).group_by(Schedule.departure_station_id, Schedule.arrival_station_id).all()
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "status_distribution": [
            {"status": status.status, "count": status.count}
            for status in status_distribution
        ],
        "delay_analysis": {
            "avg_delay_minutes": round(delay_analysis.avg_delay_minutes or 0, 2),
            "max_delay_minutes": round(delay_analysis.max_delay_minutes or 0, 2),
            "total_schedules": delay_analysis.total_schedules
        },
        "route_performance": [
            {
                "departure_station_id": route.departure_station_id,
                "arrival_station_id": route.arrival_station_id,
                "total_trips": route.total_trips,
                "avg_on_time_performance": round(route.avg_on_time or 0, 2),
                "avg_delay_minutes": round(route.avg_delay or 0, 2)
            }
            for route in route_performance
        ]
    }

@router.get("/incidents/analysis")
async def get_incident_analysis(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get incident analysis and trends"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Incident type distribution
    incident_types = db.query(
        Incident.incident_type,
        func.count(Incident.id).label('count'),
        func.avg(Incident.delay_minutes).label('avg_delay'),
        func.sum(Incident.affected_passengers).label('total_affected')
    ).filter(Incident.occurred_at >= start_date).group_by(Incident.incident_type).all()
    
    # Severity distribution
    severity_distribution = db.query(
        Incident.severity,
        func.count(Incident.id).label('count')
    ).filter(Incident.occurred_at >= start_date).group_by(Incident.severity).all()
    
    # Daily incident trends
    daily_trends = db.query(
        func.date(Incident.occurred_at).label('date'),
        func.count(Incident.id).label('incident_count'),
        func.sum(Incident.delay_minutes).label('total_delay'),
        func.sum(Incident.affected_passengers).label('total_affected')
    ).filter(Incident.occurred_at >= start_date).group_by(
        func.date(Incident.occurred_at)
    ).order_by('date').all()
    
    # Resolution time analysis
    resolution_analysis = db.query(
        func.avg(
            func.extract('epoch', Incident.resolved_at - Incident.occurred_at) / 3600
        ).label('avg_resolution_hours'),
        func.count(Incident.id).label('resolved_incidents')
    ).filter(
        and_(
            Incident.occurred_at >= start_date,
            Incident.resolved_at.isnot(None)
        )
    ).first()
    
    return {
        "period_days": days,
        "incident_types": [
            {
                "type": incident.incident_type,
                "count": incident.count,
                "avg_delay_minutes": round(incident.avg_delay or 0, 2),
                "total_affected_passengers": incident.total_affected or 0
            }
            for incident in incident_types
        ],
        "severity_distribution": [
            {"severity": severity.severity, "count": severity.count}
            for severity in severity_distribution
        ],
        "daily_trends": [
            {
                "date": trend.date.isoformat(),
                "incident_count": trend.incident_count,
                "total_delay_minutes": trend.total_delay or 0,
                "total_affected_passengers": trend.total_affected or 0
            }
            for trend in daily_trends
        ],
        "resolution_analysis": {
            "avg_resolution_hours": round(resolution_analysis.avg_resolution_hours or 0, 2),
            "resolved_incidents": resolution_analysis.resolved_incidents
        }
    }

@router.get("/efficiency/metrics")
async def get_efficiency_metrics(
    train_type: Optional[TrainType] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get efficiency metrics for trains"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(
        Train.train_type,
        func.avg(PerformanceMetric.fuel_consumed / PerformanceMetric.distance_traveled).label('fuel_efficiency'),
        func.avg(PerformanceMetric.on_time_performance).label('avg_punctuality'),
        func.avg(PerformanceMetric.passenger_count / Train.capacity * 100).label('avg_capacity_utilization'),
        func.count(PerformanceMetric.id).label('metric_count')
    ).join(PerformanceMetric).filter(
        and_(
            PerformanceMetric.date_recorded >= start_date,
            PerformanceMetric.distance_traveled > 0,
            Train.capacity > 0
        )
    )
    
    if train_type:
        query = query.filter(Train.train_type == train_type)
    
    efficiency_data = query.group_by(Train.train_type).all()
    
    return [
        {
            "train_type": data.train_type,
            "fuel_efficiency": round(data.fuel_efficiency or 0, 4),
            "avg_punctuality": round(data.avg_punctuality or 0, 2),
            "avg_capacity_utilization": round(data.avg_capacity_utilization or 0, 2),
            "metric_count": data.metric_count
        }
        for data in efficiency_data
    ]

@router.get("/reports/summary")
async def get_summary_report(
    report_type: str = Query(..., regex="^(daily|weekly|monthly)$"),
    date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate summary reports"""
    if not date:
        date = datetime.utcnow()
    
    if report_type == "daily":
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif report_type == "weekly":
        start_date = date - timedelta(days=date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
    else:  # monthly
        start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
    
    # Get summary statistics
    total_schedules = db.query(Schedule).filter(
        and_(
            Schedule.scheduled_departure >= start_date,
            Schedule.scheduled_departure < end_date
        )
    ).count()
    
    completed_schedules = db.query(Schedule).filter(
        and_(
            Schedule.scheduled_departure >= start_date,
            Schedule.scheduled_departure < end_date,
            Schedule.status == ScheduleStatus.COMPLETED
        )
    ).count()
    
    total_incidents = db.query(Incident).filter(
        and_(
            Incident.occurred_at >= start_date,
            Incident.occurred_at < end_date
        )
    ).count()
    
    avg_performance = db.query(
        func.avg(PerformanceMetric.on_time_performance).label('avg_on_time'),
        func.sum(PerformanceMetric.fuel_consumed).label('total_fuel'),
        func.sum(PerformanceMetric.distance_traveled).label('total_distance')
    ).filter(
        and_(
            PerformanceMetric.date_recorded >= start_date,
            PerformanceMetric.date_recorded < end_date
        )
    ).first()
    
    return {
        "report_type": report_type,
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "summary": {
            "total_schedules": total_schedules,
            "completed_schedules": completed_schedules,
            "completion_rate": (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0,
            "total_incidents": total_incidents,
            "avg_on_time_performance": round(avg_performance.avg_on_time or 0, 2),
            "total_fuel_consumed": round(avg_performance.total_fuel or 0, 2),
            "total_distance_traveled": round(avg_performance.total_distance or 0, 2),
            "fuel_efficiency": round(
                (avg_performance.total_fuel / avg_performance.total_distance) if avg_performance.total_distance else 0, 4
            )
        }
    }
