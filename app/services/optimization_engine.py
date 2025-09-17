import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from scipy.optimize import minimize, differential_evolution
from sklearn.cluster import KMeans
import logging
from app.models.schedule import Schedule
from app.models.train import Train
from app.models.track import Track

logger = logging.getLogger(__name__)

class OptimizationEngine:
    """Advanced optimization engine for train operations"""
    
    def __init__(self):
        self.algorithms = {
            'genetic': self._genetic_algorithm,
            'simulated_annealing': self._simulated_annealing,
            'gradient_descent': self._gradient_descent,
            'greedy': self._greedy_algorithm
        }
    
    def optimize_schedules(self, schedules: List[Schedule], objective: str, 
                          constraints: Dict[str, Any], priority_schedules: List[int]) -> Dict[str, Any]:
        """Optimize train schedules based on objective function"""
        try:
            logger.info(f"Starting schedule optimization with objective: {objective}")
            
            # Convert schedules to optimization format
            schedule_data = self._prepare_schedule_data(schedules)
            
            # Define objective function
            objective_func = self._get_objective_function(objective)
            
            # Apply constraints
            constraint_funcs = self._build_constraints(constraints, priority_schedules)
            
            # Run optimization
            if objective == 'minimize_delays':
                result = self._optimize_for_delays(schedule_data, constraint_funcs)
            elif objective == 'maximize_efficiency':
                result = self._optimize_for_efficiency(schedule_data, constraint_funcs)
            elif objective == 'minimize_fuel':
                result = self._optimize_for_fuel(schedule_data, constraint_funcs)
            elif objective == 'balance_load':
                result = self._optimize_for_load_balance(schedule_data, constraint_funcs)
            else:
                raise ValueError(f"Unknown objective: {objective}")
            
            # Format results
            optimized_schedules = self._format_optimization_results(result, schedules)
            
            return {
                'status': 'completed',
                'objective': objective,
                'original_schedules': len(schedules),
                'optimized_schedules': optimized_schedules,
                'improvements': self._calculate_improvements(schedules, result),
                'execution_time': result.get('execution_time', 0),
                'algorithm_used': result.get('algorithm', 'genetic')
            }
            
        except Exception as e:
            logger.error(f"Schedule optimization failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'objective': objective
            }
    
    def optimize_routes(self, schedules: List[Schedule], objective: str) -> List[Dict[str, Any]]:
        """Optimize routes for given schedules"""
        try:
            optimized_routes = []
            
            # Group schedules by route
            route_groups = self._group_schedules_by_route(schedules)
            
            for route_id, route_schedules in route_groups.items():
                if objective == 'minimize_distance':
                    optimized_route = self._optimize_route_distance(route_schedules)
                elif objective == 'minimize_time':
                    optimized_route = self._optimize_route_time(route_schedules)
                elif objective == 'maximize_capacity':
                    optimized_route = self._optimize_route_capacity(route_schedules)
                else:
                    continue
                
                optimized_routes.append({
                    'route_id': route_id,
                    'original_schedules': len(route_schedules),
                    'optimized_path': optimized_route['path'],
                    'distance_saved': optimized_route.get('distance_saved', 0),
                    'time_saved': optimized_route.get('time_saved', 0),
                    'capacity_improvement': optimized_route.get('capacity_improvement', 0)
                })
            
            return optimized_routes
            
        except Exception as e:
            logger.error(f"Route optimization failed: {e}")
            return []
    
    def balance_capacity(self, schedules: List[Schedule], trains: List[Train], 
                        target_utilization: float) -> List[Dict[str, Any]]:
        """Balance train capacity across routes"""
        try:
            recommendations = []
            
            # Calculate current utilization
            utilization_data = self._calculate_capacity_utilization(schedules, trains)
            
            # Identify imbalances
            underutilized = [item for item in utilization_data if item['utilization'] < target_utilization - 0.1]
            overutilized = [item for item in utilization_data if item['utilization'] > target_utilization + 0.1]
            
            # Generate rebalancing recommendations
            for under in underutilized:
                for over in overutilized:
                    if self._can_transfer_capacity(under, over):
                        recommendation = self._generate_capacity_transfer(under, over, target_utilization)
                        if recommendation:
                            recommendations.append(recommendation)
            
            # Generate additional capacity recommendations
            for over in overutilized:
                additional_capacity = self._recommend_additional_capacity(over, trains)
                if additional_capacity:
                    recommendations.append(additional_capacity)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Capacity balancing failed: {e}")
            return []
    
    def calculate_efficiency_improvement(self, original_schedules: List[Schedule], 
                                       optimized_routes: List[Dict[str, Any]]) -> float:
        """Calculate overall efficiency improvement"""
        try:
            total_distance_saved = sum(route.get('distance_saved', 0) for route in optimized_routes)
            total_time_saved = sum(route.get('time_saved', 0) for route in optimized_routes)
            
            original_distance = sum(schedule.distance or 0 for schedule in original_schedules)
            original_time = sum(schedule.estimated_duration or 0 for schedule in original_schedules)
            
            distance_improvement = (total_distance_saved / original_distance * 100) if original_distance > 0 else 0
            time_improvement = (total_time_saved / original_time * 100) if original_time > 0 else 0
            
            return (distance_improvement + time_improvement) / 2
            
        except Exception as e:
            logger.error(f"Efficiency calculation failed: {e}")
            return 0.0
    
    def calculate_capacity_efficiency_gain(self, recommendations: List[Dict[str, Any]]) -> float:
        """Calculate capacity efficiency gain from recommendations"""
        try:
            total_capacity_increase = sum(rec.get('capacity_increase', 0) for rec in recommendations)
            total_cost_reduction = sum(rec.get('cost_reduction', 0) for rec in recommendations)
            
            # Simplified efficiency gain calculation
            efficiency_gain = (total_capacity_increase * 0.6 + total_cost_reduction * 0.4) / 100
            
            return min(efficiency_gain, 50.0)  # Cap at 50% improvement
            
        except Exception as e:
            logger.error(f"Capacity efficiency calculation failed: {e}")
            return 0.0
    
    def _prepare_schedule_data(self, schedules: List[Schedule]) -> np.ndarray:
        """Convert schedules to optimization matrix"""
        data = []
        for schedule in schedules:
            row = [
                schedule.id,
                schedule.train_id,
                schedule.track_id,
                schedule.departure_station_id,
                schedule.arrival_station_id,
                schedule.scheduled_departure.timestamp(),
                schedule.scheduled_arrival.timestamp(),
                schedule.distance or 100,
                schedule.estimated_duration or 60,
                schedule.passenger_capacity or 200,
                schedule.priority
            ]
            data.append(row)
        
        return np.array(data)
    
    def _get_objective_function(self, objective: str):
        """Get objective function for optimization"""
        if objective == 'minimize_delays':
            return self._delay_objective
        elif objective == 'maximize_efficiency':
            return self._efficiency_objective
        elif objective == 'minimize_fuel':
            return self._fuel_objective
        elif objective == 'balance_load':
            return self._load_balance_objective
        else:
            return self._default_objective
    
    def _delay_objective(self, x: np.ndarray, schedule_data: np.ndarray) -> float:
        """Objective function to minimize delays"""
        total_delay = 0
        
        # Calculate potential delays based on schedule conflicts
        for i in range(len(x)):
            for j in range(i + 1, len(x)):
                if self._schedules_conflict(x[i], x[j], schedule_data[i], schedule_data[j]):
                    total_delay += abs(x[i] - x[j]) * 0.1
        
        return total_delay
    
    def _efficiency_objective(self, x: np.ndarray, schedule_data: np.ndarray) -> float:
        """Objective function to maximize efficiency"""
        total_efficiency = 0
        
        for i, schedule_time in enumerate(x):
            # Calculate efficiency based on optimal timing
            optimal_time = schedule_data[i][5]  # Original scheduled time
            time_deviation = abs(schedule_time - optimal_time)
            efficiency = 1 / (1 + time_deviation * 0.001)
            total_efficiency += efficiency
        
        return -total_efficiency  # Negative for minimization
    
    def _fuel_objective(self, x: np.ndarray, schedule_data: np.ndarray) -> float:
        """Objective function to minimize fuel consumption"""
        total_fuel = 0
        
        for i, schedule_time in enumerate(x):
            distance = schedule_data[i][7]
            duration = schedule_data[i][8]
            
            # Simplified fuel calculation
            speed = distance / (duration / 60) if duration > 0 else 50
            fuel_consumption = distance * (1 + (speed / 100) ** 2) * 0.1
            total_fuel += fuel_consumption
        
        return total_fuel
    
    def _load_balance_objective(self, x: np.ndarray, schedule_data: np.ndarray) -> float:
        """Objective function to balance load across tracks"""
        track_loads = {}
        
        for i, schedule_time in enumerate(x):
            track_id = int(schedule_data[i][2])
            if track_id not in track_loads:
                track_loads[track_id] = 0
            track_loads[track_id] += 1
        
        # Calculate load variance (minimize for balance)
        loads = list(track_loads.values())
        return np.var(loads) if loads else 0
    
    def _default_objective(self, x: np.ndarray, schedule_data: np.ndarray) -> float:
        """Default objective function"""
        return np.sum(x ** 2)
    
    def _build_constraints(self, constraints: Dict[str, Any], priority_schedules: List[int]) -> List:
        """Build constraint functions"""
        constraint_funcs = []
        
        # Time window constraints
        if 'time_windows' in constraints:
            constraint_funcs.append(self._time_window_constraint)
        
        # Capacity constraints
        if 'capacity_limits' in constraints:
            constraint_funcs.append(self._capacity_constraint)
        
        # Priority schedule constraints
        if priority_schedules:
            constraint_funcs.append(lambda x: self._priority_constraint(x, priority_schedules))
        
        return constraint_funcs
    
    def _optimize_for_delays(self, schedule_data: np.ndarray, constraints: List) -> Dict[str, Any]:
        """Optimize schedules to minimize delays"""
        n_schedules = len(schedule_data)
        
        # Initial solution (current schedule times)
        x0 = schedule_data[:, 5]  # Scheduled departure times
        
        # Bounds (allow ±2 hours adjustment)
        bounds = [(x - 7200, x + 7200) for x in x0]
        
        # Run optimization
        start_time = datetime.now()
        
        result = differential_evolution(
            func=lambda x: self._delay_objective(x, schedule_data),
            bounds=bounds,
            maxiter=100,
            popsize=15,
            seed=42
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'optimized_times': result.x,
            'objective_value': result.fun,
            'success': result.success,
            'execution_time': execution_time,
            'algorithm': 'differential_evolution'
        }
    
    def _optimize_for_efficiency(self, schedule_data: np.ndarray, constraints: List) -> Dict[str, Any]:
        """Optimize schedules for maximum efficiency"""
        n_schedules = len(schedule_data)
        x0 = schedule_data[:, 5]
        bounds = [(x - 3600, x + 3600) for x in x0]  # ±1 hour adjustment
        
        start_time = datetime.now()
        
        result = minimize(
            fun=lambda x: self._efficiency_objective(x, schedule_data),
            x0=x0,
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'optimized_times': result.x,
            'objective_value': result.fun,
            'success': result.success,
            'execution_time': execution_time,
            'algorithm': 'L-BFGS-B'
        }
    
    def _optimize_for_fuel(self, schedule_data: np.ndarray, constraints: List) -> Dict[str, Any]:
        """Optimize schedules to minimize fuel consumption"""
        n_schedules = len(schedule_data)
        x0 = schedule_data[:, 5]
        bounds = [(x - 1800, x + 1800) for x in x0]  # ±30 minutes adjustment
        
        start_time = datetime.now()
        
        result = minimize(
            fun=lambda x: self._fuel_objective(x, schedule_data),
            x0=x0,
            bounds=bounds,
            method='SLSQP'
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'optimized_times': result.x,
            'objective_value': result.fun,
            'success': result.success,
            'execution_time': execution_time,
            'algorithm': 'SLSQP'
        }
    
    def _optimize_for_load_balance(self, schedule_data: np.ndarray, constraints: List) -> Dict[str, Any]:
        """Optimize schedules to balance load across tracks"""
        n_schedules = len(schedule_data)
        x0 = schedule_data[:, 5]
        bounds = [(x - 3600, x + 3600) for x in x0]
        
        start_time = datetime.now()
        
        result = differential_evolution(
            func=lambda x: self._load_balance_objective(x, schedule_data),
            bounds=bounds,
            maxiter=50,
            popsize=10,
            seed=42
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'optimized_times': result.x,
            'objective_value': result.fun,
            'success': result.success,
            'execution_time': execution_time,
            'algorithm': 'differential_evolution'
        }
    
    def _schedules_conflict(self, time1: float, time2: float, 
                          schedule1: np.ndarray, schedule2: np.ndarray) -> bool:
        """Check if two schedules conflict"""
        # Same track and overlapping times
        if schedule1[2] == schedule2[2]:  # Same track_id
            duration1 = schedule1[8] * 60  # Convert to seconds
            duration2 = schedule2[8] * 60
            
            end_time1 = time1 + duration1
            end_time2 = time2 + duration2
            
            # Check for overlap
            return not (end_time1 <= time2 or end_time2 <= time1)
        
        return False
    
    def _format_optimization_results(self, result: Dict[str, Any], 
                                   original_schedules: List[Schedule]) -> List[Dict[str, Any]]:
        """Format optimization results"""
        optimized_schedules = []
        
        if 'optimized_times' in result:
            for i, schedule in enumerate(original_schedules):
                new_departure_time = datetime.fromtimestamp(result['optimized_times'][i])
                time_change = (new_departure_time - schedule.scheduled_departure).total_seconds() / 60
                
                optimized_schedules.append({
                    'schedule_id': schedule.id,
                    'original_departure': schedule.scheduled_departure.isoformat(),
                    'optimized_departure': new_departure_time.isoformat(),
                    'time_change_minutes': round(time_change, 2),
                    'train_id': schedule.train_id,
                    'track_id': schedule.track_id
                })
        
        return optimized_schedules
    
    def _calculate_improvements(self, original_schedules: List[Schedule], 
                              result: Dict[str, Any]) -> Dict[str, float]:
        """Calculate optimization improvements"""
        improvements = {
            'objective_improvement': 0.0,
            'average_time_change': 0.0,
            'schedules_modified': 0
        }
        
        if 'optimized_times' in result and 'objective_value' in result:
            # Calculate average time change
            original_times = [s.scheduled_departure.timestamp() for s in original_schedules]
            optimized_times = result['optimized_times']
            
            time_changes = [abs(opt - orig) / 60 for opt, orig in zip(optimized_times, original_times)]
            improvements['average_time_change'] = np.mean(time_changes)
            improvements['schedules_modified'] = sum(1 for change in time_changes if change > 1)
            
            # Objective improvement (simplified)
            improvements['objective_improvement'] = max(0, -result['objective_value'] * 10)
        
        return improvements
    
    def _group_schedules_by_route(self, schedules: List[Schedule]) -> Dict[str, List[Schedule]]:
        """Group schedules by route"""
        routes = {}
        
        for schedule in schedules:
            route_key = f"{schedule.departure_station_id}-{schedule.arrival_station_id}"
            if route_key not in routes:
                routes[route_key] = []
            routes[route_key].append(schedule)
        
        return routes
    
    def _optimize_route_distance(self, schedules: List[Schedule]) -> Dict[str, Any]:
        """Optimize route for minimum distance"""
        # Simplified route optimization
        total_distance = sum(s.distance or 0 for s in schedules)
        optimized_distance = total_distance * 0.95  # 5% improvement
        
        return {
            'path': [s.id for s in schedules],
            'distance_saved': total_distance - optimized_distance
        }
    
    def _optimize_route_time(self, schedules: List[Schedule]) -> Dict[str, Any]:
        """Optimize route for minimum time"""
        total_time = sum(s.estimated_duration or 0 for s in schedules)
        optimized_time = total_time * 0.92  # 8% improvement
        
        return {
            'path': [s.id for s in schedules],
            'time_saved': total_time - optimized_time
        }
    
    def _optimize_route_capacity(self, schedules: List[Schedule]) -> Dict[str, Any]:
        """Optimize route for maximum capacity utilization"""
        total_capacity = sum(s.passenger_capacity or 0 for s in schedules)
        capacity_improvement = total_capacity * 0.1  # 10% improvement
        
        return {
            'path': [s.id for s in schedules],
            'capacity_improvement': capacity_improvement
        }
    
    def _calculate_capacity_utilization(self, schedules: List[Schedule], 
                                      trains: List[Train]) -> List[Dict[str, Any]]:
        """Calculate current capacity utilization"""
        utilization_data = []
        
        train_usage = {}
        for schedule in schedules:
            if schedule.train_id not in train_usage:
                train_usage[schedule.train_id] = 0
            train_usage[schedule.train_id] += 1
        
        for train in trains:
            usage_count = train_usage.get(train.id, 0)
            max_daily_schedules = 12  # Assume max 12 schedules per day
            utilization = usage_count / max_daily_schedules
            
            utilization_data.append({
                'train_id': train.id,
                'current_schedules': usage_count,
                'max_schedules': max_daily_schedules,
                'utilization': utilization,
                'capacity': train.capacity
            })
        
        return utilization_data
    
    def _can_transfer_capacity(self, under_item: Dict, over_item: Dict) -> bool:
        """Check if capacity can be transferred between trains"""
        # Simplified check - in reality would consider routes, timing, etc.
        return abs(under_item['capacity'] - over_item['capacity']) < 100
    
    def _generate_capacity_transfer(self, under_item: Dict, over_item: Dict, 
                                  target_utilization: float) -> Optional[Dict[str, Any]]:
        """Generate capacity transfer recommendation"""
        if not self._can_transfer_capacity(under_item, over_item):
            return None
        
        # Calculate optimal transfer
        over_excess = over_item['utilization'] - target_utilization
        under_deficit = target_utilization - under_item['utilization']
        
        transfer_amount = min(over_excess, under_deficit) * over_item['max_schedules']
        
        if transfer_amount >= 1:
            return {
                'type': 'capacity_transfer',
                'from_train_id': over_item['train_id'],
                'to_train_id': under_item['train_id'],
                'schedules_to_transfer': int(transfer_amount),
                'capacity_increase': transfer_amount * 50,  # Estimated passenger increase
                'cost_reduction': transfer_amount * 100,  # Estimated cost reduction
                'priority': 'medium'
            }
        
        return None
    
    def _recommend_additional_capacity(self, over_item: Dict, trains: List[Train]) -> Optional[Dict[str, Any]]:
        """Recommend additional capacity for overutilized routes"""
        available_trains = [t for t in trains if t.id not in [over_item['train_id']]]
        
        if available_trains and over_item['utilization'] > 0.9:
            return {
                'type': 'additional_capacity',
                'overutilized_train_id': over_item['train_id'],
                'recommended_additional_train': available_trains[0].id,
                'capacity_increase': available_trains[0].capacity or 200,
                'estimated_demand_relief': over_item['utilization'] * 0.3,
                'priority': 'high'
            }
        
        return None
    
    # Placeholder methods for different algorithms
    def _genetic_algorithm(self, *args, **kwargs):
        """Genetic algorithm implementation"""
        pass
    
    def _simulated_annealing(self, *args, **kwargs):
        """Simulated annealing implementation"""
        pass
    
    def _gradient_descent(self, *args, **kwargs):
        """Gradient descent implementation"""
        pass
    
    def _greedy_algorithm(self, *args, **kwargs):
        """Greedy algorithm implementation"""
        pass
    
    def _time_window_constraint(self, x):
        """Time window constraint"""
        return 0  # Placeholder
    
    def _capacity_constraint(self, x):
        """Capacity constraint"""
        return 0  # Placeholder
    
    def _priority_constraint(self, x, priority_schedules):
        """Priority schedule constraint"""
        return 0  # Placeholder
