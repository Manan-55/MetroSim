from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application settings
    app_name: str = "Train Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://user:password@localhost/traindb"
    database_echo: bool = False
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # Security settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    allowed_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # ML Model settings
    model_path: str = "./models"
    prediction_cache_ttl: int = 300  # 5 minutes
    
    # Optimization settings
    max_optimization_time: int = 60  # seconds
    optimization_algorithm: str = "genetic"
    
    # Simulation settings
    simulation_time_step: float = 1.0  # seconds
    max_simulation_time: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
