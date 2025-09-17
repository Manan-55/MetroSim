import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import random
import logging
from app.models.schedule import Schedule
from app.models.train import Train
from app.models.track import Track

logger = logging.getLogger(__name__)

class SimulationEngine:
    """Advanced simulation engine for train operations"""
    
    def __init__(self):
        self.simulation_state = {}
        self.event_queue = []
        self.current_time = datetime.now()
        self.random_seed = 42
        
    def run_simulation(self, simulation_type: str, schedules: List[Schedule], 
                      trains: List[Train], tracks: List[Track],
                      duration_hours: int, time_step_seconds: float,
                      parameters: Dict[str, Any], scenario_data: Optional[Dict[str, Any]] = None,
                      progress_callback: Optional[Callable[[float], bool]] = None) -> Dict[str, Any]:
        """Run simulation based on type and parameters"""
        try:
            logger.info(f"Starting {simulation_type} simulation for {duration_hours} hours")
            
            # Initialize simulation
            self._initialize_simulation(schedules, trains, tracks, parameters)
            
            # Set random seed for reproducibility
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)
            
            # Run simulation based on type
            if simulation_type == 'schedule':
                return self._run_schedule_simulation(duration_hours, time_step_seconds, 
                                                   parameters, progress_callback)
            elif simulation_type == 'incident':
                return self._run_incident_simulation(duration_hours, time_step_seconds, 
                                                   parameters, progress_callback)
            elif simulation_type == 'capacity':
                return self._run_capacity_simulation(duration_hours, time_step_seconds, 
                                                   parameters, progress_callback)
            elif simulation_type == 'weather':
                return self._run_weather_simulation(duration_hours, time_step_seconds, 
                                                  parameters, progress_callback)
            else:
                raise ValueError(f"Unknown simulation type: {simulation_type}")
                
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'results': {}
            }
    
    def _initialize_simulation(self, schedules: List[Schedule], trains: List[Train], 
                             tracks: List[Track], parameters: Dict[str, Any]):
        """Initialize simulation state"""
        self.simulation_state = {
            'schedules': {s.id: self._schedule_to_dict(s) for s in schedules},
            'trains': {t.id: self._train_to_dict(t) for t in trains},
            'tracks': {t.id: self._track_to_dict(t) for t in tracks},
            'current_time': self.current_time,
            'events': [],
            'metrics': {
                'delays': [],
                'fuel_consumption': [],
                'passenger_counts': [],
                'incidents': [],
                'performance_scores': []
            },
            'parameters': parameters
        }
        
        # Initialize event queue with scheduled departures
        for schedule in schedules:
            self.event_queue.append({
                'time': schedule.scheduled_departure,
                'type': 'departure',
                'schedule_id': schedule.id,
                'train_id': schedule.train_id,
                'track_id': schedule.track_id
            })
        
        # Sort events by time
        self.event_queue.sort(key=lambda x: x['time'])
    
    def _run_schedule_simulation(self, duration_hours: int, time_step_seconds: float,
                               parameters: Dict[str, Any], progress_callback: Optional[Callable]) -> Dict[str, Any]:
        """Run schedule-focused simulation"""
        results = {
            'simulation_type': 'schedule',
            'timeline': {},
            'summary': {},
            'events': []
        }
        
        end_time = self.current_time + timedelta(hours=duration_hours)
        total_steps = int(duration_hours * 3600 / time_step_seconds)
        step = 0
        
        while self.current_time < end_time:
            # Process events at current time
            events_processed = self._process_events_at_time(self.current_time)
            
            # Apply schedule-specific logic
            self._apply_schedule_dynamics(parameters)
            
            # Record metrics
            metrics = self._collect_current_metrics()
            results['timeline'][self.current_time.isoformat()] = metrics
            
            # Update progress
            step += 1
            if progress_callback:
                progress = (step / total_steps) * 100
                if not progress_callback(progress):
                    break  # Simulation stopped
            
            # Advance time
            self.current_time += timedelta(seconds=time_step_seconds)
        
        # Generate summary
        results['summary'] = self._generate_schedule_summary()
        results['events'] = self.simulation_state['events']
        
        return results
    
    def _run_incident_simulation(self, duration_hours: int, time_step_seconds: float,
                               parameters: Dict[str, Any], progress_callback: Optional[Callable]) -> Dict[str, Any]:
        """Run incident-focused simulation"""
        results = {
            'simulation_type': 'incident',
            'timeline': {},
            'summary': {},
            'incidents': []
        }
        
        end_time = self.current_time + timedelta(hours=duration_hours)
        total_steps = int(duration_hours * 3600 / time_step_seconds)
        step = 0
        
        # Generate random incidents based on parameters
        incident_probability = parameters.get('incident_probability', 0.1)
        incident_types = parameters.get('incident_types', ['delay', 'breakdown', 'weather'])
        
        while self.current_time < end_time:
            # Check for random incidents
            if random.random() < incident_probability / 3600 * time_step_seconds:
                incident = self._generate_random_incident(incident_types)
                self._apply_incident(incident)
                results['incidents'].append(incident)
            
            # Process scheduled events
            self._process_events_at_time(self.current_time)
            
            # Apply incident effects
            self._apply_incident_effects()
            
            # Record metrics
            metrics = self._collect_current_metrics()
            results['timeline'][self.current_time.isoformat()] = metrics
            
            # Update progress
            step += 1
            if progress_callback:
                progress = (step / total_steps) * 100
                if not progress_callback(progress):
                    break
            
            self.current_time += timedelta(seconds=time_step_seconds)
        
        results['summary'] = self._generate_incident_summary()
        
        return results
    
    def _run_capacity_simulation(self, duration_hours: int, time_step_seconds: float,
                               parameters: Dict[str, Any], progress_callback: Optional[Callable]) -> Dict[str, Any]:
        """Run capacity-focused simulation"""
        results = {
            'simulation_type': 'capacity',
            'timeline': {},
            'summary': {},
            'capacity_analysis': {}
        }
        
        end_time = self.current_time + timedelta(hours=duration_hours)
        total_steps = int(duration_hours * 3600 / time_step_seconds)
        step = 0
        
        # Capacity parameters
        demand_multiplier = parameters.get('demand_multiplier', 1.0)
        peak_hours = parameters.get('peak_hours', [7, 8, 17, 18])
        
        while self.current_time < end_time:
            # Apply demand variations
            current_hour = self.current_time.hour
            if current_hour in peak_hours:
                current_demand_multiplier = demand_multiplier * 1.5
            else:
                current_demand_multiplier = demand_multiplier
            
            # Process events with capacity considerations
            self._process_events_at_time(self.current_time)
            self._apply_capacity_dynamics(current_demand_multiplier)
            
            # Record capacity metrics
            metrics = self._collect_capacity_metrics()
            results['timeline'][self.current_time.isoformat()] = metrics
            
            # Update progress
            step += 1
            if progress_callback:
                progress = (step / total_steps) * 100
                if not progress_callback(progress):
                    break
            
            self.current_time += timedelta(seconds=time_step_seconds)
        
        results['summary'] = self._generate_capacity_summary()
        results['capacity_analysis'] = self._analyze_capacity_utilization()
        
        return results
    
    def _run_weather_simulation(self, duration_hours: int, time_step_seconds: float,
                              parameters: Dict[str, Any], progress_callback: Optional[Callable]) -> Dict[str, Any]:
        """Run weather-focused simulation"""
        results = {
            'simulation_type': 'weather',
            'timeline': {},
            'summary': {},
            'weather_events': []
        }
        
        end_time = self.current_time + timedelta(hours=duration_hours)
        total_steps = int(duration_hours * 3600 / time_step_seconds)
        step = 0
        
        # Weather parameters
        weather_type = parameters.get('weather_type', 'rain')
        severity = parameters.get('severity', 'moderate')
        duration_hours_weather = parameters.get('duration_hours', 4)
        
        # Generate weather events
        weather_events = self._generate_weather_events(weather_type, severity, duration_hours_weather)
        results['weather_events'] = weather_events
        
        while self.current_time < end_time:
            # Check for active weather events
            active_weather = self._get_active_weather_events(weather_events, self.current_time)
            
            # Process events with weather effects
            self._process_events_at_time(self.current_time)
            self._apply_weather_effects(active_weather)
            
            # Record weather-affected metrics
            metrics = self._collect_weather_metrics(active_weather)
            results['timeline'][self.current_time.isoformat()] = metrics
            
            # Update progress
            step += 1
            if progress_callback:
                progress = (step / total_steps) * 100
                if not progress_callback(progress):
                    break
            
            self.current_time += timedelta(seconds=time_step_seconds)
        
        results['summary'] = self._generate_weather_summary()
        
        return results
    
    def _schedule_to_dict(self, schedule: Schedule) -> Dict[str, Any]:
        """Convert schedule to dictionary for simulation"""
        return {
            'id': schedule.id,
            'train_id': schedule.train_id,
            'track_id': schedule.track_id,
            'departure_station_id': schedule.departure_station_id,
            'arrival_station_id': schedule.arrival_station_id,
            'scheduled_departure': schedule.scheduled_departure,
            'scheduled_arrival': schedule.scheduled_arrival,
            'actual_departure': None,
            'actual_arrival': None,
            'status': 'scheduled',
            'delay_minutes': 0,
            'passenger_count': schedule.passenger_count or 0,
            'distance': schedule.distance or 100,
            'estimated_duration': schedule.estimated_duration or 60
        }
    
    def _train_to_dict(self, train: Train) -> Dict[str, Any]:
        """Convert train to dictionary for simulation"""
        return {
            'id': train.id,
            'train_number': train.train_number,
            'capacity': train.capacity or 200,
            'max_speed': train.max_speed or 120,
            'fuel_consumption_rate': 0.5,  # L/km
            'current_location': train.current_location,
            'status': 'available',
            'maintenance_due': False,
            'fuel_level': 100.0,
            'current_passengers': 0
        }
    
    def _track_to_dict(self, track: Track) -> Dict[str, Any]:
        """Convert track to dictionary for simulation"""
        return {
            'id': track.id,
            'name': track.name,
            'length': track.length,
            'max_speed': track.max_speed or 100,
            'capacity_per_hour': track.capacity_trains_per_hour or 10,
            'current_usage': 0,
            'status': 'operational',
            'weather_affected': False
        }
    
    def _process_events_at_time(self, current_time: datetime) -> int:
        """Process all events scheduled for current time"""
        events_processed = 0
        
        # Process events from queue
        while self.event_queue and self.event_queue[0]['time'] <= current_time:
            event = self.event_queue.pop(0)
            self._process_event(event)
            events_processed += 1
        
        return events_processed
    
    def _process_event(self, event: Dict[str, Any]):
        """Process a single event"""
        event_type = event['type']
        
        if event_type == 'departure':
            self._process_departure_event(event)
        elif event_type == 'arrival':
            self._process_arrival_event(event)
        elif event_type == 'incident':
            self._process_incident_event(event)
        elif event_type == 'maintenance':
            self._process_maintenance_event(event)
        
        # Record event
        self.simulation_state['events'].append({
            'time': self.current_time.isoformat(),
            'type': event_type,
            'details': event
        })
    
    def _process_departure_event(self, event: Dict[str, Any]):
        """Process train departure event"""
        schedule_id = event['schedule_id']
        train_id = event['train_id']
        
        if schedule_id in self.simulation_state['schedules']:
            schedule = self.simulation_state['schedules'][schedule_id]
            train = self.simulation_state['trains'][train_id]
            
            # Update schedule status
            schedule['actual_departure'] = self.current_time
            schedule['status'] = 'in_transit'
            
            # Calculate delay
            scheduled_time = schedule['scheduled_departure']
            delay_minutes = (self.current_time - scheduled_time).total_seconds() / 60
            schedule['delay_minutes'] = delay_minutes
            
            # Update train status
            train['status'] = 'in_transit'
            train['current_passengers'] = schedule['passenger_count']
            
            # Schedule arrival event
            estimated_arrival = self.current_time + timedelta(minutes=schedule['estimated_duration'])
            self.event_queue.append({
                'time': estimated_arrival,
                'type': 'arrival',
                'schedule_id': schedule_id,
                'train_id': train_id
            })
            
            # Sort event queue
            self.event_queue.sort(key=lambda x: x['time'])
    
    def _process_arrival_event(self, event: Dict[str, Any]):
        """Process train arrival event"""
        schedule_id = event['schedule_id']
        train_id = event['train_id']
        
        if schedule_id in self.simulation_state['schedules']:
            schedule = self.simulation_state['schedules'][schedule_id]
            train = self.simulation_state['trains'][train_id]
            
            # Update schedule status
            schedule['actual_arrival'] = self.current_time
            schedule['status'] = 'completed'
            
            # Update train status
            train['status'] = 'available'
            train['current_passengers'] = 0
            
            # Update fuel consumption
            distance = schedule['distance']
            fuel_consumed = distance * train['fuel_consumption_rate']
            train['fuel_level'] = max(0, train['fuel_level'] - fuel_consumed)
    
    def _apply_schedule_dynamics(self, parameters: Dict[str, Any]):
        """Apply schedule-specific dynamics"""
        delay_probability = parameters.get('delay_probability', 0.1)
        cascade_effect = parameters.get('cascade_effect', True)
        
        # Apply random delays
        for schedule_id, schedule in self.simulation_state['schedules'].items():
            if schedule['status'] == 'scheduled' and random.random() < delay_probability:
                delay_minutes = random.exponential(10)  # Average 10 minutes delay
                schedule['delay_minutes'] += delay_minutes
                
                # Update departure time
                new_departure = schedule['scheduled_departure'] + timedelta(minutes=delay_minutes)
                schedule['actual_departure'] = new_departure
    
    def _generate_random_incident(self, incident_types: List[str]) -> Dict[str, Any]:
        """Generate a random incident"""
        incident_type = random.choice(incident_types)
        
        # Select random train/track
        train_ids = list(self.simulation_state['trains'].keys())
        track_ids = list(self.simulation_state['tracks'].keys())
        
        incident = {
            'type': incident_type,
            'time': self.current_time,
            'severity': random.choice(['low', 'medium', 'high']),
            'duration_minutes': random.randint(15, 120),
            'affected_train_id': random.choice(train_ids) if train_ids else None,
            'affected_track_id': random.choice(track_ids) if track_ids else None,
            'description': f"Random {incident_type} incident"
        }
        
        return incident
    
    def _apply_incident(self, incident: Dict[str, Any]):
        """Apply incident effects to simulation"""
        if incident['affected_train_id']:
            train = self.simulation_state['trains'][incident['affected_train_id']]
            train['status'] = 'incident'
            
        if incident['affected_track_id']:
            track = self.simulation_state['tracks'][incident['affected_track_id']]
            track['status'] = 'disrupted'
    
    def _apply_incident_effects(self):
        """Apply ongoing incident effects"""
        # Simplified incident effect application
        for train in self.simulation_state['trains'].values():
            if train['status'] == 'incident':
                # Chance to resolve incident
                if random.random() < 0.1:  # 10% chance per time step
                    train['status'] = 'available'
    
    def _apply_capacity_dynamics(self, demand_multiplier: float):
        """Apply capacity-related dynamics"""
        for schedule in self.simulation_state['schedules'].values():
            if schedule['status'] == 'scheduled':
                # Adjust passenger count based on demand
                base_passengers = schedule['passenger_count']
                adjusted_passengers = int(base_passengers * demand_multiplier)
                
                # Get train capacity
                train = self.simulation_state['trains'][schedule['train_id']]
                max_capacity = train['capacity']
                
                # Apply capacity constraints
                schedule['passenger_count'] = min(adjusted_passengers, max_capacity)
                
                # If over capacity, add delay
                if adjusted_passengers > max_capacity:
                    overflow_delay = (adjusted_passengers - max_capacity) / max_capacity * 10
                    schedule['delay_minutes'] += overflow_delay
    
    def _generate_weather_events(self, weather_type: str, severity: str, duration_hours: int) -> List[Dict[str, Any]]:
        """Generate weather events for simulation"""
        events = []
        
        # Generate weather event
        start_time = self.current_time + timedelta(hours=random.randint(1, 6))
        end_time = start_time + timedelta(hours=duration_hours)
        
        events.append({
            'type': weather_type,
            'severity': severity,
            'start_time': start_time,
            'end_time': end_time,
            'speed_reduction': 0.3 if severity == 'severe' else 0.15,
            'delay_factor': 1.5 if severity == 'severe' else 1.2
        })
        
        return events
    
    def _get_active_weather_events(self, weather_events: List[Dict[str, Any]], current_time: datetime) -> List[Dict[str, Any]]:
        """Get weather events active at current time"""
        active_events = []
        
        for event in weather_events:
            if event['start_time'] <= current_time <= event['end_time']:
                active_events.append(event)
        
        return active_events
    
    def _apply_weather_effects(self, active_weather: List[Dict[str, Any]]):
        """Apply weather effects to simulation"""
        if not active_weather:
            return
        
        # Apply effects to all tracks
        for track in self.simulation_state['tracks'].values():
            track['weather_affected'] = True
            
        # Apply effects to schedules
        for schedule in self.simulation_state['schedules'].values():
            if schedule['status'] in ['scheduled', 'in_transit']:
                for weather in active_weather:
                    # Add weather-related delay
                    weather_delay = schedule['estimated_duration'] * (weather['delay_factor'] - 1)
                    schedule['delay_minutes'] += weather_delay
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current simulation metrics"""
        metrics = {
            'active_trains': sum(1 for t in self.simulation_state['trains'].values() if t['status'] == 'in_transit'),
            'delayed_schedules': sum(1 for s in self.simulation_state['schedules'].values() if s['delay_minutes'] > 5),
            'average_delay': np.mean([s['delay_minutes'] for s in self.simulation_state['schedules'].values()]),
            'total_passengers': sum(s['passenger_count'] for s in self.simulation_state['schedules'].values()),
            'fuel_consumption': sum(100 - t['fuel_level'] for t in self.simulation_state['trains'].values()),
            'operational_tracks': sum(1 for t in self.simulation_state['tracks'].values() if t['status'] == 'operational')
        }
        
        return metrics
    
    def _collect_capacity_metrics(self) -> Dict[str, Any]:
        """Collect capacity-specific metrics"""
        total_capacity = sum(t['capacity'] for t in self.simulation_state['trains'].values())
        used_capacity = sum(s['passenger_count'] for s in self.simulation_state['schedules'].values() if s['status'] != 'completed')
        
        return {
            'total_capacity': total_capacity,
            'used_capacity': used_capacity,
            'capacity_utilization': (used_capacity / total_capacity * 100) if total_capacity > 0 else 0,
            'overcapacity_schedules': sum(1 for s in self.simulation_state['schedules'].values() 
                                        if s['passenger_count'] > self.simulation_state['trains'][s['train_id']]['capacity'])
        }
    
    def _collect_weather_metrics(self, active_weather: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect weather-specific metrics"""
        return {
            'weather_events_active': len(active_weather),
            'weather_affected_tracks': sum(1 for t in self.simulation_state['tracks'].values() if t.get('weather_affected', False)),
            'weather_delays': sum(s['delay_minutes'] for s in self.simulation_state['schedules'].values() if s['delay_minutes'] > 0),
            'weather_severity': active_weather[0]['severity'] if active_weather else 'none'
        }
    
    def _generate_schedule_summary(self) -> Dict[str, Any]:
        """Generate schedule simulation summary"""
        schedules = list(self.simulation_state['schedules'].values())
        
        return {
            'total_schedules': len(schedules),
            'completed_schedules': sum(1 for s in schedules if s['status'] == 'completed'),
            'delayed_schedules': sum(1 for s in schedules if s['delay_minutes'] > 5),
            'average_delay_minutes': np.mean([s['delay_minutes'] for s in schedules]),
            'max_delay_minutes': max([s['delay_minutes'] for s in schedules]) if schedules else 0,
            'on_time_performance': sum(1 for s in schedules if s['delay_minutes'] <= 5) / len(schedules) * 100 if schedules else 0
        }
    
    def _generate_incident_summary(self) -> Dict[str, Any]:
        """Generate incident simulation summary"""
        return {
            'total_incidents': len([e for e in self.simulation_state['events'] if e['type'] == 'incident']),
            'trains_affected': len(set(t['id'] for t in self.simulation_state['trains'].values() if t['status'] == 'incident')),
            'tracks_disrupted': sum(1 for t in self.simulation_state['tracks'].values() if t['status'] == 'disrupted'),
            'average_resolution_time': 45.0  # Placeholder
        }
    
    def _generate_capacity_summary(self) -> Dict[str, Any]:
        """Generate capacity simulation summary"""
        return {
            'peak_utilization': 85.0,  # Placeholder
            'average_utilization': 65.0,  # Placeholder
            'overcapacity_events': 5,  # Placeholder
            'capacity_efficiency': 78.0  # Placeholder
        }
    
    def _generate_weather_summary(self) -> Dict[str, Any]:
        """Generate weather simulation summary"""
        return {
            'weather_duration_hours': 4.0,  # Placeholder
            'total_weather_delays': 120.0,  # Placeholder
            'affected_schedules': 15,  # Placeholder
            'weather_impact_score': 6.5  # Placeholder (1-10 scale)
        }
    
    def _analyze_capacity_utilization(self) -> Dict[str, Any]:
        """Analyze capacity utilization patterns"""
        return {
            'peak_hours': [7, 8, 17, 18],
            'utilization_by_hour': {str(h): random.uniform(40, 90) for h in range(24)},
            'bottleneck_routes': ['Route A-B', 'Route C-D'],
            'optimization_opportunities': ['Add capacity during peak hours', 'Redistribute off-peak services']
        }
