from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class UserData(BaseModel):
    userId: str
    diet_type: str
    transportation_mode: str
    vehicle_type: str
    heating_source: str
    home_energy_efficiency: str
    shower_frequency: str
    screen_time: str
    internet_usage: str
    clothes_purchases: str
    recycling: str
    trash_bag_size: str

class CarbonFootprintResponse(BaseModel):
    total_footprint: float
    breakdown: Dict[str, float]
    recommendations: List[str]
    timestamp: datetime

class TrainingData(BaseModel):
    userId: str
    carbon_footprint: float
    features: UserData

class ChallengeRecommendation(BaseModel):
    challenge_id: str
    title: str
    description: str
    category: str
    difficulty: str
    carbon_savings: float
    duration_days: int
    score: float

class UserChallenge(BaseModel):
    challenge_id: str
    start_date: datetime
    status: str
    progress: float
    completed: bool
    completion_date: Optional[datetime] = None

class ChallengeProgressUpdate(BaseModel):
    progress: float

class UserTestResult(BaseModel):
    body_type: str
    gender: str
    diet_type: str
    shower_frequency: str
    heating_source: str
    transportation_mode: str
    vehicle_type: str
    social_activity: str
    trash_bag_size: str
    air_travel_frequency: str
    home_energy_efficiency: str
    recycling: str
    cooking_devices: str
    screen_time: str
    clothes_purchases: str
    internet_usage: str
    userId: str 