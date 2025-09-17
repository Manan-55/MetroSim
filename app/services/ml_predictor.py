import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import joblib
import os
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class MLPredictor:
    """Machine Learning predictor for train operations"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_path = settings.model_path
        self._ensure_model_directory()
    
    def _ensure_model_directory(self):
        """Ensure model directory exists"""
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)
    
    def predict_delay(self, schedule_data: Dict[str, Any]) -> Dict[str, float]:
        """Predict schedule delay probability and expected delay time"""
        try:
            # Load or train delay prediction model
            if 'delay_predictor' not in self.models:
                self._load_or_train_delay_model()
            
            # Prepare features
            features = self._prepare_delay_features(schedule_data)
            
            # Make predictions
            delay_probability = self.models['delay_classifier'].predict_proba([features])[0][1]
            expected_delay = max(0, self.models['delay_regressor'].predict([features])[0])
            
            return {
                'delay_probability': float(delay_probability),
                'expected_delay_minutes': float(expected_delay),
                'confidence': self._calculate_prediction_confidence(features, 'delay')
            }
            
        except Exception as e:
            logger.error(f"Delay prediction failed: {e}")
            return {
                'delay_probability': 0.1,  # Default fallback
                'expected_delay_minutes': 5.0,
                'confidence': 0.5
            }
    
    def predict_demand(self, route_data: Dict[str, Any], time_period: str) -> Dict[str, float]:
        """Predict passenger demand for a route"""
        try:
            # Load or train demand prediction model
            if 'demand_predictor' not in self.models:
                self._load_or_train_demand_model()
            
            # Prepare features
            features = self._prepare_demand_features(route_data, time_period)
            
            # Make prediction
            predicted_demand = max(0, self.models['demand_predictor'].predict([features])[0])
            
            return {
                'predicted_passengers': float(predicted_demand),
                'demand_category': self._categorize_demand(predicted_demand),
                'confidence': self._calculate_prediction_confidence(features, 'demand')
            }
            
        except Exception as e:
            logger.error(f"Demand prediction failed: {e}")
            return {
                'predicted_passengers': 100.0,  # Default fallback
                'demand_category': 'medium',
                'confidence': 0.5
            }
    
    def predict_maintenance(self, train_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict maintenance needs for a train"""
        try:
            # Load or train maintenance prediction model
            if 'maintenance_predictor' not in self.models:
                self._load_or_train_maintenance_model()
            
            # Prepare features
            features = self._prepare_maintenance_features(train_data)
            
            # Make predictions
            maintenance_probability = self.models['maintenance_classifier'].predict_proba([features])[0][1]
            days_until_maintenance = max(1, self.models['maintenance_regressor'].predict([features])[0])
            
            # Predict maintenance type
            maintenance_type_probs = self.models['maintenance_type_classifier'].predict_proba([features])[0]
            maintenance_types = ['routine', 'repair', 'overhaul']
            predicted_type = maintenance_types[np.argmax(maintenance_type_probs)]
            
            return {
                'maintenance_probability': float(maintenance_probability),
                'days_until_maintenance': float(days_until_maintenance),
                'predicted_maintenance_type': predicted_type,
                'maintenance_type_probabilities': {
                    maintenance_types[i]: float(prob) 
                    for i, prob in enumerate(maintenance_type_probs)
                },
                'confidence': self._calculate_prediction_confidence(features, 'maintenance')
            }
            
        except Exception as e:
            logger.error(f"Maintenance prediction failed: {e}")
            return {
                'maintenance_probability': 0.2,
                'days_until_maintenance': 30.0,
                'predicted_maintenance_type': 'routine',
                'maintenance_type_probabilities': {
                    'routine': 0.7,
                    'repair': 0.2,
                    'overhaul': 0.1
                },
                'confidence': 0.5
            }
    
    def predict_fuel_consumption(self, trip_data: Dict[str, Any]) -> Dict[str, float]:
        """Predict fuel consumption for a trip"""
        try:
            # Load or train fuel consumption model
            if 'fuel_predictor' not in self.models:
                self._load_or_train_fuel_model()
            
            # Prepare features
            features = self._prepare_fuel_features(trip_data)
            
            # Make prediction
            predicted_consumption = max(0, self.models['fuel_predictor'].predict([features])[0])
            
            return {
                'predicted_fuel_consumption': float(predicted_consumption),
                'efficiency_rating': self._calculate_efficiency_rating(predicted_consumption, trip_data),
                'confidence': self._calculate_prediction_confidence(features, 'fuel')
            }
            
        except Exception as e:
            logger.error(f"Fuel consumption prediction failed: {e}")
            return {
                'predicted_fuel_consumption': 50.0,  # Default fallback
                'efficiency_rating': 'average',
                'confidence': 0.5
            }
    
    def predict_performance_metrics(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict comprehensive performance metrics"""
        try:
            delay_prediction = self.predict_delay(schedule_data)
            demand_prediction = self.predict_demand(schedule_data, 'current')
            fuel_prediction = self.predict_fuel_consumption(schedule_data)
            
            # Calculate composite performance score
            performance_score = self._calculate_performance_score(
                delay_prediction, demand_prediction, fuel_prediction
            )
            
            return {
                'delay_prediction': delay_prediction,
                'demand_prediction': demand_prediction,
                'fuel_prediction': fuel_prediction,
                'performance_score': performance_score,
                'recommendations': self._generate_performance_recommendations(
                    delay_prediction, demand_prediction, fuel_prediction
                )
            }
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return {
                'error': str(e),
                'performance_score': 0.5
            }
    
    def train_models(self, training_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict[str, float]]:
        """Train all ML models with provided data"""
        results = {}
        
        try:
            # Train delay prediction models
            if 'schedules' in training_data:
                results['delay'] = self._train_delay_models(training_data['schedules'])
            
            # Train demand prediction model
            if 'passenger_data' in training_data:
                results['demand'] = self._train_demand_model(training_data['passenger_data'])
            
            # Train maintenance prediction models
            if 'maintenance' in training_data:
                results['maintenance'] = self._train_maintenance_models(training_data['maintenance'])
            
            # Train fuel consumption model
            if 'performance' in training_data:
                results['fuel'] = self._train_fuel_model(training_data['performance'])
            
            logger.info("Model training completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {'error': str(e)}
    
    def _prepare_delay_features(self, schedule_data: Dict[str, Any]) -> List[float]:
        """Prepare features for delay prediction"""
        features = []
        
        # Time-based features
        departure_time = datetime.fromisoformat(schedule_data.get('scheduled_departure', datetime.now().isoformat()))
        features.extend([
            departure_time.hour,
            departure_time.weekday(),
            departure_time.day,
            departure_time.month
        ])
        
        # Route features
        features.extend([
            schedule_data.get('distance', 100),
            schedule_data.get('estimated_duration', 60),
            schedule_data.get('max_speed', 80),
            schedule_data.get('priority', 5)
        ])
        
        # Train features
        features.extend([
            schedule_data.get('train_capacity', 200),
            schedule_data.get('train_age', 10),
            schedule_data.get('last_maintenance_days', 30)
        ])
        
        # Weather features (simplified)
        features.extend([
            schedule_data.get('weather_score', 0.8),  # 0-1 scale
            schedule_data.get('temperature', 20),
            schedule_data.get('precipitation', 0)
        ])
        
        return features
    
    def _prepare_demand_features(self, route_data: Dict[str, Any], time_period: str) -> List[float]:
        """Prepare features for demand prediction"""
        features = []
        
        # Time features
        current_time = datetime.now()
        features.extend([
            current_time.hour,
            current_time.weekday(),
            current_time.day,
            current_time.month
        ])
        
        # Route features
        features.extend([
            route_data.get('route_popularity', 0.5),
            route_data.get('distance', 100),
            route_data.get('travel_time', 60),
            route_data.get('ticket_price', 10)
        ])
        
        # Historical features
        features.extend([
            route_data.get('avg_daily_passengers', 150),
            route_data.get('peak_hour_multiplier', 1.5),
            route_data.get('seasonal_factor', 1.0)
        ])
        
        return features
    
    def _prepare_maintenance_features(self, train_data: Dict[str, Any]) -> List[float]:
        """Prepare features for maintenance prediction"""
        features = []
        
        # Train characteristics
        features.extend([
            train_data.get('age_years', 10),
            train_data.get('total_distance', 100000),
            train_data.get('operating_hours', 5000),
            train_data.get('max_speed', 120)
        ])
        
        # Usage patterns
        features.extend([
            train_data.get('daily_usage_hours', 12),
            train_data.get('avg_load_factor', 0.7),
            train_data.get('harsh_braking_events', 5),
            train_data.get('emergency_stops', 1)
        ])
        
        # Maintenance history
        features.extend([
            train_data.get('days_since_last_maintenance', 30),
            train_data.get('maintenance_frequency', 4),  # per year
            train_data.get('avg_maintenance_cost', 5000),
            train_data.get('breakdown_count', 2)
        ])
        
        # Performance indicators
        features.extend([
            train_data.get('fuel_efficiency', 0.8),
            train_data.get('on_time_performance', 0.9),
            train_data.get('passenger_complaints', 3),
            train_data.get('system_alerts', 1)
        ])
        
        return features
    
    def _prepare_fuel_features(self, trip_data: Dict[str, Any]) -> List[float]:
        """Prepare features for fuel consumption prediction"""
        features = []
        
        # Trip characteristics
        features.extend([
            trip_data.get('distance', 100),
            trip_data.get('duration', 60),
            trip_data.get('avg_speed', 80),
            trip_data.get('max_speed', 120)
        ])
        
        # Train characteristics
        features.extend([
            trip_data.get('train_weight', 200),
            trip_data.get('passenger_count', 150),
            trip_data.get('cargo_weight', 0),
            trip_data.get('engine_efficiency', 0.8)
        ])
        
        # Route characteristics
        features.extend([
            trip_data.get('elevation_change', 100),
            trip_data.get('curve_count', 10),
            trip_data.get('stop_count', 5),
            trip_data.get('grade_percentage', 2)
        ])
        
        # Environmental factors
        features.extend([
            trip_data.get('temperature', 20),
            trip_data.get('wind_speed', 10),
            trip_data.get('weather_resistance', 1.0)
        ])
        
        return features
    
    def _load_or_train_delay_model(self):
        """Load existing delay models or train new ones"""
        try:
            # Try to load existing models
            self.models['delay_classifier'] = joblib.load(
                os.path.join(self.model_path, 'delay_classifier.pkl')
            )
            self.models['delay_regressor'] = joblib.load(
                os.path.join(self.model_path, 'delay_regressor.pkl')
            )
            logger.info("Loaded existing delay models")
        except FileNotFoundError:
            # Train new models with synthetic data
            logger.info("Training new delay models with synthetic data")
            self._train_delay_models_synthetic()
    
    def _load_or_train_demand_model(self):
        """Load existing demand model or train new one"""
        try:
            self.models['demand_predictor'] = joblib.load(
                os.path.join(self.model_path, 'demand_predictor.pkl')
            )
            logger.info("Loaded existing demand model")
        except FileNotFoundError:
            logger.info("Training new demand model with synthetic data")
            self._train_demand_model_synthetic()
    
    def _load_or_train_maintenance_model(self):
        """Load existing maintenance models or train new ones"""
        try:
            self.models['maintenance_classifier'] = joblib.load(
                os.path.join(self.model_path, 'maintenance_classifier.pkl')
            )
            self.models['maintenance_regressor'] = joblib.load(
                os.path.join(self.model_path, 'maintenance_regressor.pkl')
            )
            self.models['maintenance_type_classifier'] = joblib.load(
                os.path.join(self.model_path, 'maintenance_type_classifier.pkl')
            )
            logger.info("Loaded existing maintenance models")
        except FileNotFoundError:
            logger.info("Training new maintenance models with synthetic data")
            self._train_maintenance_models_synthetic()
    
    def _load_or_train_fuel_model(self):
        """Load existing fuel model or train new one"""
        try:
            self.models['fuel_predictor'] = joblib.load(
                os.path.join(self.model_path, 'fuel_predictor.pkl')
            )
            logger.info("Loaded existing fuel model")
        except FileNotFoundError:
            logger.info("Training new fuel model with synthetic data")
            self._train_fuel_model_synthetic()
    
    def _train_delay_models_synthetic(self):
        """Train delay models with synthetic data"""
        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: hour, weekday, distance, duration, capacity, weather_score
        X = np.random.rand(n_samples, 16)  # 16 features as prepared
        
        # Simulate delay patterns
        delay_prob = (X[:, 0] > 0.7).astype(int)  # More delays in evening
        delay_prob += (X[:, 1] > 0.8).astype(int)  # More delays on weekends
        delay_prob = np.clip(delay_prob, 0, 1)
        
        delay_minutes = np.where(delay_prob, 
                                np.random.exponential(15, n_samples), 
                                np.random.exponential(2, n_samples))
        
        # Train models
        self.models['delay_classifier'] = GradientBoostingClassifier(random_state=42)
        self.models['delay_classifier'].fit(X, delay_prob)
        
        self.models['delay_regressor'] = RandomForestRegressor(random_state=42)
        self.models['delay_regressor'].fit(X, delay_minutes)
        
        # Save models
        joblib.dump(self.models['delay_classifier'], 
                   os.path.join(self.model_path, 'delay_classifier.pkl'))
        joblib.dump(self.models['delay_regressor'], 
                   os.path.join(self.model_path, 'delay_regressor.pkl'))
    
    def _train_demand_model_synthetic(self):
        """Train demand model with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        X = np.random.rand(n_samples, 11)  # 11 features as prepared
        
        # Simulate demand patterns
        base_demand = 100 + X[:, 0] * 200  # Base demand 100-300
        peak_multiplier = np.where(X[:, 0] < 0.3, 1.5, 1.0)  # Peak hours
        weekend_multiplier = np.where(X[:, 1] > 0.7, 0.8, 1.0)  # Weekend effect
        
        y = base_demand * peak_multiplier * weekend_multiplier
        
        self.models['demand_predictor'] = RandomForestRegressor(random_state=42)
        self.models['demand_predictor'].fit(X, y)
        
        joblib.dump(self.models['demand_predictor'], 
                   os.path.join(self.model_path, 'demand_predictor.pkl'))
    
    def _train_maintenance_models_synthetic(self):
        """Train maintenance models with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        X = np.random.rand(n_samples, 16)  # 16 features as prepared
        
        # Simulate maintenance needs
        maintenance_prob = (X[:, 0] > 0.8).astype(int)  # Based on age
        maintenance_prob += (X[:, 4] > 0.9).astype(int)  # Based on usage
        maintenance_prob = np.clip(maintenance_prob, 0, 1)
        
        days_until = np.where(maintenance_prob, 
                             np.random.exponential(10, n_samples),
                             np.random.exponential(60, n_samples))
        
        maintenance_types = np.random.choice([0, 1, 2], n_samples, p=[0.6, 0.3, 0.1])
        
        # Train models
        self.models['maintenance_classifier'] = GradientBoostingClassifier(random_state=42)
        self.models['maintenance_classifier'].fit(X, maintenance_prob)
        
        self.models['maintenance_regressor'] = RandomForestRegressor(random_state=42)
        self.models['maintenance_regressor'].fit(X, days_until)
        
        self.models['maintenance_type_classifier'] = GradientBoostingClassifier(random_state=42)
        self.models['maintenance_type_classifier'].fit(X, maintenance_types)
        
        # Save models
        for model_name, model in [
            ('maintenance_classifier', self.models['maintenance_classifier']),
            ('maintenance_regressor', self.models['maintenance_regressor']),
            ('maintenance_type_classifier', self.models['maintenance_type_classifier'])
        ]:
            joblib.dump(model, os.path.join(self.model_path, f'{model_name}.pkl'))
    
    def _train_fuel_model_synthetic(self):
        """Train fuel model with synthetic data"""
        np.random.seed(42)
        n_samples = 1000
        
        X = np.random.rand(n_samples, 16)  # 16 features as prepared
        
        # Simulate fuel consumption based on distance, weight, and efficiency
        base_consumption = X[:, 0] * 100  # Distance factor
        weight_factor = 1 + X[:, 4] * 0.5  # Weight factor
        efficiency_factor = 1 - X[:, 7] * 0.3  # Efficiency factor
        
        y = base_consumption * weight_factor * efficiency_factor
        
        self.models['fuel_predictor'] = RandomForestRegressor(random_state=42)
        self.models['fuel_predictor'].fit(X, y)
        
        joblib.dump(self.models['fuel_predictor'], 
                   os.path.join(self.model_path, 'fuel_predictor.pkl'))
    
    def _calculate_prediction_confidence(self, features: List[float], model_type: str) -> float:
        """Calculate confidence score for predictions"""
        # Simplified confidence calculation based on feature variance
        feature_variance = np.var(features)
        base_confidence = 0.7
        
        # Adjust confidence based on model type and feature variance
        if model_type == 'delay':
            confidence = base_confidence + (1 - feature_variance) * 0.2
        elif model_type == 'demand':
            confidence = base_confidence + (1 - feature_variance) * 0.15
        elif model_type == 'maintenance':
            confidence = base_confidence + (1 - feature_variance) * 0.25
        else:
            confidence = base_confidence
        
        return min(max(confidence, 0.1), 0.95)
    
    def _categorize_demand(self, demand: float) -> str:
        """Categorize demand level"""
        if demand < 50:
            return 'low'
        elif demand < 150:
            return 'medium'
        elif demand < 250:
            return 'high'
        else:
            return 'very_high'
    
    def _calculate_efficiency_rating(self, fuel_consumption: float, trip_data: Dict[str, Any]) -> str:
        """Calculate efficiency rating"""
        distance = trip_data.get('distance', 100)
        efficiency = fuel_consumption / distance if distance > 0 else 1.0
        
        if efficiency < 0.5:
            return 'excellent'
        elif efficiency < 0.8:
            return 'good'
        elif efficiency < 1.2:
            return 'average'
        else:
            return 'poor'
    
    def _calculate_performance_score(self, delay_pred: Dict, demand_pred: Dict, fuel_pred: Dict) -> float:
        """Calculate composite performance score"""
        delay_score = 1 - delay_pred['delay_probability']
        demand_score = min(demand_pred['predicted_passengers'] / 200, 1.0)
        fuel_score = 1 - min(fuel_pred['predicted_fuel_consumption'] / 100, 1.0)
        
        # Weighted average
        return (delay_score * 0.4 + demand_score * 0.3 + fuel_score * 0.3)
    
    def _generate_performance_recommendations(self, delay_pred: Dict, demand_pred: Dict, fuel_pred: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        if delay_pred['delay_probability'] > 0.3:
            recommendations.append("High delay probability detected. Consider adjusting schedule or route.")
        
        if demand_pred['predicted_passengers'] > 180:
            recommendations.append("High demand predicted. Consider adding capacity or additional services.")
        
        if fuel_pred['efficiency_rating'] == 'poor':
            recommendations.append("Poor fuel efficiency predicted. Check train condition and route optimization.")
        
        if not recommendations:
            recommendations.append("Performance metrics look good. Continue current operations.")
        
        return recommendations

# Global ML predictor instance
ml_predictor = MLPredictor()
