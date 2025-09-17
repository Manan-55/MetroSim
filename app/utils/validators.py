import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, time
from pydantic import validator
import phonenumbers
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_email_address(email: str) -> str:
    """Validate email address format"""
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError:
        raise ValidationError(f"Invalid email address: {email}")

def validate_phone_number(phone: str, country_code: str = "US") -> str:
    """Validate phone number format"""
    try:
        parsed = phonenumbers.parse(phone, country_code)
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError(f"Invalid phone number: {phone}")
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise ValidationError(f"Invalid phone number format: {phone}")

def validate_train_number(train_number: str) -> str:
    """Validate train number format (alphanumeric, 3-10 characters)"""
    if not re.match(r'^[A-Z0-9]{3,10}$', train_number.upper()):
        raise ValidationError(
            "Train number must be 3-10 alphanumeric characters"
        )
    return train_number.upper()

def validate_track_code(track_code: str) -> str:
    """Validate track code format"""
    if not re.match(r'^[A-Z0-9\-]{2,20}$', track_code.upper()):
        raise ValidationError(
            "Track code must be 2-20 characters (letters, numbers, hyphens)"
        )
    return track_code.upper()

def validate_station_code(station_code: str) -> str:
    """Validate station code format (3-letter IATA-style codes)"""
    if not re.match(r'^[A-Z]{3}$', station_code.upper()):
        raise ValidationError(
            "Station code must be exactly 3 uppercase letters"
        )
    return station_code.upper()

def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    """Validate GPS coordinates"""
    if not (-90 <= latitude <= 90):
        raise ValidationError(f"Latitude must be between -90 and 90: {latitude}")
    if not (-180 <= longitude <= 180):
        raise ValidationError(f"Longitude must be between -180 and 180: {longitude}")
    return latitude, longitude

def validate_speed(speed: float, max_speed: float = 500.0) -> float:
    """Validate speed value (km/h)"""
    if speed < 0:
        raise ValidationError(f"Speed cannot be negative: {speed}")
    if speed > max_speed:
        raise ValidationError(f"Speed exceeds maximum {max_speed} km/h: {speed}")
    return speed

def validate_capacity(capacity: int, min_capacity: int = 1, max_capacity: int = 2000) -> int:
    """Validate passenger capacity"""
    if not (min_capacity <= capacity <= max_capacity):
        raise ValidationError(
            f"Capacity must be between {min_capacity} and {max_capacity}: {capacity}"
        )
    return capacity

def validate_time_range(start_time: time, end_time: time) -> tuple[time, time]:
    """Validate that end time is after start time"""
    if end_time <= start_time:
        raise ValidationError(
            f"End time {end_time} must be after start time {start_time}"
        )
    return start_time, end_time

def validate_date_range(start_date: datetime, end_date: datetime) -> tuple[datetime, datetime]:
    """Validate that end date is after start date"""
    if end_date <= start_date:
        raise ValidationError(
            f"End date {end_date} must be after start date {start_date}"
        )
    return start_date, end_date

def validate_json_data(data: Any, required_fields: List[str] = None) -> Dict[str, Any]:
    """Validate JSON data structure"""
    if not isinstance(data, dict):
        raise ValidationError("Data must be a JSON object")
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {missing_fields}")
    
    return data

def validate_priority(priority: int, min_priority: int = 1, max_priority: int = 10) -> int:
    """Validate priority level"""
    if not (min_priority <= priority <= max_priority):
        raise ValidationError(
            f"Priority must be between {min_priority} and {max_priority}: {priority}"
        )
    return priority

def validate_percentage(value: float) -> float:
    """Validate percentage value (0-100)"""
    if not (0 <= value <= 100):
        raise ValidationError(f"Percentage must be between 0 and 100: {value}")
    return value

def sanitize_string(value: str, max_length: int = 255, allow_html: bool = False) -> str:
    """Sanitize string input"""
    if not isinstance(value, str):
        raise ValidationError("Value must be a string")
    
    # Remove leading/trailing whitespace
    value = value.strip()
    
    if len(value) > max_length:
        raise ValidationError(f"String exceeds maximum length {max_length}: {len(value)}")
    
    if not allow_html:
        # Basic HTML tag removal
        value = re.sub(r'<[^>]+>', '', value)
    
    return value

class TrainSystemValidators:
    """Collection of train system specific validators"""
    
    @staticmethod
    def validate_maintenance_interval(days: int) -> int:
        """Validate maintenance interval in days"""
        if not (1 <= days <= 365):
            raise ValidationError(
                f"Maintenance interval must be between 1 and 365 days: {days}"
            )
        return days
    
    @staticmethod
    def validate_fuel_efficiency(efficiency: float) -> float:
        """Validate fuel efficiency (km per liter)"""
        if not (0.1 <= efficiency <= 50.0):
            raise ValidationError(
                f"Fuel efficiency must be between 0.1 and 50.0 km/L: {efficiency}"
            )
        return efficiency
    
    @staticmethod
    def validate_route_distance(distance: float) -> float:
        """Validate route distance in kilometers"""
        if not (0.1 <= distance <= 10000.0):
            raise ValidationError(
                f"Route distance must be between 0.1 and 10000 km: {distance}"
            )
        return distance
