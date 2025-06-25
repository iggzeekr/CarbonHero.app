from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from sklearn.metrics.pairwise import cosine_similarity

from app.services import CarbonCalculator, ChallengeService, RecommendationEngine
from app.ml import CarbonFootprintModel, CollaborativeFilter
from .models import UserData, CarbonFootprintResponse, TrainingData
from .services.ml_service import MLService

# Load environment variables
load_dotenv()

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize services
carbon_calculator = CarbonCalculator()
recommendation_engine = RecommendationEngine()
carbon_model = CarbonFootprintModel()
collaborative_filter = CollaborativeFilter()
challenge_service = ChallengeService()
ml_service = MLService()

# Initialize similarity matrix with existing user data
def initialize_similarity_matrix():
    try:
        print("Loading user data from Firestore to initialize similarity matrix...")
        users_ref = db.collection("user_data").stream()
        user_data = []
        
        # Collect all user data
        for doc in users_ref:
            user_dict = doc.to_dict()
            # Ensure userId is present
            if 'userId' not in user_dict:
                user_dict['userId'] = doc.id
            user_data.append(user_dict)
        
        if user_data:
            print(f"Found {len(user_data)} users in Firestore")
            # Update the ML service with user data
            ml_service.update_user_item_matrix(user_data)
            print("Successfully initialized similarity matrix with existing user data")
        else:
            print("No user data found in Firestore")
            # Initialize empty mappings to prevent errors
            ml_service.user_id_to_index = {}
            ml_service.index_to_user_id = {}
    except Exception as e:
        print(f"Error initializing similarity matrix: {str(e)}")
        import traceback
        traceback.print_exc()
        # Initialize empty mappings to prevent errors
        ml_service.user_id_to_index = {}
        ml_service.index_to_user_id = {}

# Initialize the similarity matrix
initialize_similarity_matrix()

app = FastAPI(title="Carbon Hero API",debug=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
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

class TrainingData(BaseModel):
    userId: str
    carbon_footprint: float
    features: UserData

class UserDataUpdate(BaseModel):
    field: str
    value: str

# Endpoints
@app.post("/calculate-carbon-footprint", response_model=CarbonFootprintResponse)
async def calculate_carbon_footprint(user_data: UserData):
    """Calculate carbon footprint based on user data"""
    try:
        # Calculate footprint
        footprint = calculate_footprint(user_data.dict())
        
        # Save to Firestore
        footprint_data = {
            "userId": user_data.userId,
            "timestamp": firestore.SERVER_TIMESTAMP,
            **footprint
        }
        db.collection("carbon_footprints").add(footprint_data)
        
        # Save user data if not exists
        user_ref = db.collection("user_data").document(user_data.userId)
        if not user_ref.get().exists:
            user_ref.set(user_data.dict())
        
        return CarbonFootprintResponse(
            total_footprint=footprint["total"],
            breakdown=footprint,
            recommendations=footprint["recommendations"],
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend-challenges/{user_id}")
async def recommend_challenges(user_id: str):
    """Kullanıcıya önerilen meydan okumaları getirir."""
    try:
        # Kullanıcı verilerini al
        user_doc = db.collection("user_data").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        user_data = user_doc.to_dict()
        
        # Kullanıcının mevcut meydan okumalarını al
        user_challenges = challenge_service.get_user_challenges(user_id)
        
        # Öneri motorunu kullanarak meydan okuma önerileri al
        recommendations = recommendation_engine.get_challenge_recommendations(user_data)
        
        # Önerilen meydan okumaların detaylarını al
        recommended_challenges = []
        for rec in recommendations:
            challenge = challenge_service.get_challenge_by_id(rec['challenge_id'])
            if challenge:
                recommended_challenges.append({
                    **challenge,
                    'recommendation_score': rec['score']
                })
        
        return recommended_challenges
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-stats/{user_id}")
async def get_user_stats(user_id: str):
    """Get user statistics including carbon footprint trends and challenge progress"""
    try:
        # Get user's carbon footprints (historical data)
        footprints_ref = db.collection("carbon_footprints")\
            .where("userId", "==", user_id)\
            .order_by("timestamp", direction=firestore.Query.DESCENDING)\
            .limit(10)\
            .stream()
        
        footprints = [doc.to_dict() for doc in footprints_ref]
        
        user_doc_ref = db.collection("user_data").document(user_id)
        user_doc = user_doc_ref.get()
        current_user_data = user_doc.to_dict() if user_doc.exists else {}

        # Initialize breakdown data to an empty dictionary
        breakdown_data = {}
        
        # Try to get breakdown from the latest carbon_footprints entry first
        if footprints:
            breakdown_data = footprints[0].get("breakdown", {})
            print(f"[GET_USER_STATS] Breakdown from carbon_footprints: {breakdown_data}") # Debug log
        
        # Eğer breakdown boşsa, son 5 footprint dokümanında breakdown içeren ilk dokümanı bul
        if not breakdown_data and footprints:
            for fp in footprints[1:5]:
                if fp.get("breakdown"):
                    breakdown_data = fp["breakdown"]
                    print(f"[GET_USER_STATS] Breakdown found in previous footprint: {breakdown_data}")
                    break
        # If breakdown is still empty, try to get it from the user_data document (fallback for older data)
        if not breakdown_data and current_user_data:
            breakdown_data = current_user_data.get("carbon_footprint_breakdown", {})
            print(f"[GET_USER_STATS] Breakdown from user_data (fallback): {breakdown_data}") # Debug log
        # Eğer breakdown hala boşsa, kullanıcı verisinden tekrar hesapla
        if not breakdown_data and current_user_data:
            from app.services.carbon_calculator import CarbonCalculator
            carbon_calculator = CarbonCalculator()
            breakdown_data = carbon_calculator.calculate(current_user_data).get("breakdown", {})
            print(f"[GET_USER_STATS] Breakdown recalculated: {breakdown_data}")

        # Determine current footprint
        current_footprint = 0.0
        if footprints:
            current_footprint = footprints[0].get("total_footprint", 0.0)
        elif current_user_data:
            current_footprint = current_user_data.get("carbon_footprint", 0.0)

        # Calculate average footprint
        average_footprint = 0.0
        if footprints:
            total_sum = sum(f.get("total_footprint", 0.0) for f in footprints)
            if len(footprints) > 0:
                average_footprint = total_sum / len(footprints)
        else:
            average_footprint = current_footprint # If no historical data, average is current

        # Calculate trend
        trend = 0.0
        trend_percentage = 0.0
        if len(footprints) >= 2:
            latest_footprint = footprints[0].get("total_footprint", 0.0)
            oldest_footprint = footprints[-1].get("total_footprint", 0.0)
            trend = latest_footprint - oldest_footprint
            if oldest_footprint != 0.0:
                trend_percentage = (trend / oldest_footprint) * 100

        # Get user's challenges (assuming challenge_service is properly initialized and available)
        # Note: challenge_service might be outside this function's scope if not passed as arg
        # For simplicity, assuming it's globally accessible or correctly injected
        # user_challenges = challenge_service.get_user_challenges(user_id)
        # completed_challenges = [c for c in user_challenges if c["user_challenge"]["completed"]]
        # in_progress_challenges = [c for c in user_challenges if not c["user_challenge"]["completed"]]
        # total_carbon_saved = sum(c["challenge"]["carbon_savings"] for c in completed_challenges)
        
        # Default challenges data if not fetching real challenges here
        challenges_stats = {
            "completed": 0,
            "in_progress": 0,
            "total_carbon_saved": 0.0
        }
        # If you want to fetch challenges, you'd need challenge_service.get_user_challenges(user_id) here

        # Get recommendations from user_data document
        recommendations_data = current_user_data.get("recommendations", [])

        # Get total score from user_data
        total_score = current_user_data.get("total_score", 0)

        # Ensure that if no footprint data is found at all, we return a 404
        if not footprints and not current_user_data:
            raise HTTPException(status_code=404, detail="No footprint data found for user")

        return {
            "current_footprint": current_footprint,
            "average_footprint": average_footprint,
            "trend": trend,
            "trend_percentage": trend_percentage,
            "improvement_percentage": abs(trend_percentage) if trend < 0 else 0,
            "challenges": challenges_stats, # Use the default or fetched challenges_stats
            "recent_footprints": footprints[:5],  # Last 5 historical footprints
            "breakdown": breakdown_data,
            "recommendations": recommendations_data, # Include recommendations in the response
            "user_data": current_user_data,
            "total_score": total_score
        }
    except Exception as e:
        import traceback
        print(f"[GET_USER_STATS] HATA: {e}") # Debug log
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.post("/challenges/{user_id}/start/{challenge_id}", response_model=UserChallenge)
async def start_challenge(user_id: str, challenge_id: str):
    """Start a new challenge for a user"""
    try:
        result = challenge_service.start_challenge(user_id, challenge_id)
        return UserChallenge(
            challenge_id=result["challenge"]["id"],
            start_date=result["user_challenge"]["startDate"],
            status=result["user_challenge"]["status"],
            progress=result["user_challenge"]["progress"],
            completed=result["user_challenge"]["completed"]
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/challenges/{user_challenge_id}/progress", response_model=UserChallenge)
async def update_challenge_progress(
    user_challenge_id: str,
    progress_update: ChallengeProgressUpdate
):
    """Update the progress of a user's challenge"""
    try:
        result = challenge_service.update_challenge_progress(
            user_challenge_id,
            progress_update.progress
        )
        return UserChallenge(
            challenge_id=result["challenge"]["id"],
            start_date=result["user_challenge"]["startDate"],
            status=result["user_challenge"]["status"],
            progress=result["user_challenge"]["progress"],
            completed=result["user_challenge"]["completed"],
            completion_date=result["user_challenge"].get("completionDate")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/challenges/{user_id}", response_model=List[UserChallenge])
async def get_user_challenges(user_id: str):
    """Get all challenges for a user"""
    try:
        challenges = challenge_service.get_user_challenges(user_id)
        return [
            UserChallenge(
                challenge_id=c["challenge"]["id"],
                start_date=c["user_challenge"]["startDate"],
                status=c["user_challenge"]["status"],
                progress=c["user_challenge"]["progress"],
                completed=c["user_challenge"]["completed"],
                completion_date=c["user_challenge"].get("completionDate")
            )
            for c in challenges
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/challenges/categories/{category}", response_model=List[ChallengeRecommendation])
async def get_challenges_by_category(category: str):
    """Get all challenges for a specific category"""
    try:
        challenges = challenge_service.get_challenges_by_category(category)
        return [
            ChallengeRecommendation(
                challenge_id=c["id"],
                title=c["title"],
                description=c["description"],
                category=c["category"],
                difficulty=c["difficulty"],
                carbon_savings=c["carbon_savings"],
                duration_days=c["duration_days"],
                score=1.0  # Default score for category listing
            )
            for c in challenges
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/challenges/difficulty/{difficulty}", response_model=List[ChallengeRecommendation])
async def get_challenges_by_difficulty(difficulty: str):
    """Get all challenges for a specific difficulty level"""
    try:
        challenges = challenge_service.get_challenges_by_difficulty(difficulty)
        return [
            ChallengeRecommendation(
                challenge_id=c["id"],
                title=c["title"],
                description=c["description"],
                category=c["category"],
                difficulty=c["difficulty"],
                carbon_savings=c["carbon_savings"],
                duration_days=c["duration_days"],
                score=1.0  # Default score for difficulty listing
            )
            for c in challenges
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/challenges/{user_id}/complete/{challenge_title}")
async def complete_challenge(user_id: str, challenge_title: str):
    """Complete a challenge and update user score"""
    try:
        # Get user's current score
        user_ref = db.collection("user_data").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_doc.to_dict()
        current_score = user_data.get("total_score", 0)
        
        # Find the challenge in all categories
        all_challenges = challenge_service.get_all_challenges()
        challenge = next((c for c in all_challenges if c["title"] == challenge_title), None)
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Dynamic points calculation
        difficulty_bonus = {"easy": 0, "medium": 10, "hard": 20}
        points_earned = int(challenge["carbon_savings"] * 20) + difficulty_bonus.get(challenge["difficulty"].lower(), 0)
        new_total_score = current_score + points_earned
        
        # Update user's total score
        user_ref.update({
            "total_score": new_total_score,
            "last_challenge_completed": challenge_title,
            "last_challenge_date": datetime.now()
        })
        
        # Add to completed challenges collection
        db.collection("completed_challenges").add({
            "userId": user_id,
            "challenge_title": challenge_title,
            "points_earned": points_earned,
            "completed_at": datetime.now()
        })
        
        return {
            "status": "success",
            "message": f"Challenge '{challenge_title}' completed!",
            "points_earned": points_earned,
            "total_score": new_total_score
        }
    except Exception as e:
        print(f"[COMPLETE_CHALLENGE ERROR] {e}")
        raise HTTPException(status_code=500, detail=f"Error completing challenge: {str(e)}")

@app.post("/tahmin")
def tahmin_yap(veri: UserTestResult):
    prediction = carbon_model.predict(veri.dict())
    # Model önerileri
    recommendations = [
        {"challenge": "Toplu taşıma kullan", "score": 10},
        {"challenge": "Et tüketimini azalt", "score": 8}
    ]
    # Collaborative filtering ile benzer kullanıcılar ve ortak challenge
    similar_users = collaborative_filter.find_similar_users(veri.dict())
    collaborative_challenges = []
    for user in similar_users:
        collaborative_challenges.append({
            "challenge": "Haftada 3 gün bisiklet kullan",
            "users": [user["user_data"].get("userId", "")],
            "score": 15
        })
    return {
        "sonuc": prediction,
        "recommendations": recommendations,
        "collaborative_challenges": collaborative_challenges
    }

@app.post("/api/user-data")
async def submit_user_data(user_data: UserData):
    try:
        # Karbon ayak izini hesapla (ML modeli ile)
        footprint_data_calculated = carbon_calculator.calculate(user_data.dict())

        # Firestore'a kaydet (user_data koleksiyonu)
        user_doc_ref = db.collection("user_data").document(user_data.userId)
        user_doc_ref.set({
            **user_data.dict(),
            "carbon_footprint": footprint_data_calculated["total_footprint"],
            "carbon_footprint_breakdown": footprint_data_calculated["breakdown"], # Add breakdown
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        })

        # carbon_footprints koleksiyonuna da ekle (geçmiş verileri)
        db.collection("carbon_footprints").add({
            "userId": user_data.userId,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "total_footprint": footprint_data_calculated["total_footprint"],
            "breakdown": footprint_data_calculated["breakdown"] # Ensure breakdown is here
        })

        # Önerileri al
        try:
            recommendations = ml_service.get_recommendations(user_data.userId)
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            recommendations = []

        # Önerileri de kaydet (user_data koleksiyonuna)
        user_doc_ref.update({
            "recommendations": recommendations
        })

        initialize_similarity_matrix()  # Yeni kullanıcı eklenince similarity matrix güncellensin

        return {
            "status": "success",
            "message": "User data saved successfully",
            "data": {
                "footprint": footprint_data_calculated["total_footprint"],
                "breakdown": footprint_data_calculated["breakdown"],
                "recommendations": recommendations
            }
        }
    except Exception as e:
        print(f"Error saving user data: {str(e)}") # Debug
        import traceback # Debug
        traceback.print_exc() # Debug
        raise HTTPException(
            status_code=500,
            detail=f"Error saving user data: {str(e)}"
        )

@app.post("/train-models")
async def train_models(training_data: List[TrainingData]):
    """Train ML models for each category using historical data"""
    try:
        # Convert training data to format expected by ML service
        formatted_data = []
        for data in training_data:
            formatted_data.append({
                "userId": data.userId,
                "carbon_footprint": data.carbon_footprint,
                **data.features.dict()
            })

        carbon_calculator.train_models(formatted_data)
        # Update collaborative filtering with all users
        try:
            # Get all users from Firestore
            users_ref = db.collection("user_data").stream()
            firestore_users = [doc.to_dict() for doc in users_ref]
            # If we have users in Firestore, use them
            if firestore_users:
                print("Updating collaborative filtering with Firestore users...")
                carbon_calculator.update_collaborative_filtering(firestore_users)
            else:
                # Otherwise use the training data
                print("No users in Firestore, using training data for collaborative filtering...")
                carbon_calculator.update_collaborative_filtering(formatted_data)
            print("Successfully updated collaborative filtering system")
        except Exception as e:
            print(f"Error updating collaborative filtering: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error updating collaborative filtering: {str(e)}"
            )
        return {"status": "success", "message": "Models trained successfully"}
    except Exception as e:
        print(f"Error training models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-recommendations/{user_id}")
async def get_user_recommendations(user_id: str):
    print("user-recommendations endpoint başı")
    try:
        # Check if user exists in Firestore
        user_doc = db.collection("user_data").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # If similarity matrix is not initialized, try to initialize it
        if not hasattr(ml_service, 'user_id_to_index') or not ml_service.user_id_to_index:
            print("Similarity matrix not initialized, attempting to initialize...")
            initialize_similarity_matrix()
            
            # If still not initialized, return empty recommendations
            if not hasattr(ml_service, 'user_id_to_index') or not ml_service.user_id_to_index:
                return {
                    "status": "success",
                    "recommendations": [],
                    "message": "No similar users found yet. Recommendations will be available as more users join."
                }
        
        # Get recommendations using ML service
        recommendations = ml_service.get_recommendations(user_id)
        
        # Format recommendations
        formatted_recommendations = []
        for rec in recommendations:
            feature = rec["feature"]
            improvement = rec["improvement_potential"]
            similarity = rec["similarity_score"]
            
            # Create recommendation message based on feature
            if feature == "diet_type":
                formatted_recommendations.append({
                    "category": "Diet",
                    "message": f"Similar users with {similarity:.1%} similarity have reduced their diet impact by {improvement:.1f} units",
                    "improvement_potential": improvement,
                    "similarity_score": similarity
                })
            elif feature == "transportation_mode":
                formatted_recommendations.append({
                    "category": "Transportation",
                    "message": f"Consider changing your transportation habits like {similarity:.1%} of similar users",
                    "improvement_potential": improvement,
                    "similarity_score": similarity
                })
            # Add more feature-specific recommendations as needed
        
        return {
            "status": "success",
            "recommendations": formatted_recommendations
        }
    except ValueError as e:
        print("user-recommendations endpoint ValueError")
        print(f"HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return empty recommendations instead of error
        return {
            "status": "success",
            "recommendations": [],
            "message": str(e)
        }
    except Exception as e:
        print("user-recommendations endpoint except bloğu")
        print(f"HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        with open("error.log", "a") as f:
            f.write(str(e) + "\n")
            traceback.print_exc(file=f)
        # Return empty recommendations instead of error
        return {
            "status": "success",
            "recommendations": [],
            "message": "An error occurred while getting recommendations. Please try again later."
        }

@app.get("/similar-users/{user_id}")
async def get_similar_users(user_id: str, n_recommendations: int = 5):
    """Get similar users based on collaborative filtering"""
    try:
        similar_users = ml_service.get_similar_users(user_id, n_recommendations)
        
        # Get user details for similar users
        similar_users_details = []
        for user_idx, similarity_score in similar_users:
            user_doc = db.collection("user_data").document(str(user_idx)).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                similar_users_details.append({
                    "userId": str(user_idx),
                    "similarity_score": float(similarity_score),
                    "carbon_footprint": user_data.get("carbon_footprint", {}).get("total", 0.0)
                })
        
        return {
            "status": "success",
            "similar_users": similar_users_details
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get leaderboard of users ranked by total score"""
    try:
        # Get all users with their total scores
        users_ref = db.collection("user_data").stream()
        users_data = []
        
        for doc in users_ref:
            user_data = doc.to_dict()
            user_data['userId'] = doc.id
            users_data.append(user_data)
        
        # Sort users by total_score (descending)
        users_data.sort(key=lambda x: x.get('total_score', 0), reverse=True)
        
        # Create leaderboard entries
        leaderboard = []
        for rank, user in enumerate(users_data, 1):
            leaderboard.append({
                "userId": user.get('userId', ''),
                "username": user.get('username', f'User {user.get("userId", "")[:8]}'),
                "points": user.get('total_score', 0),
                "carbon_footprint": user.get('carbon_footprint', {}),
                "rank": rank
            })
        
        return {
            "status": "success",
            "leaderboard": leaderboard
        }
    except Exception as e:
        print(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/user-data/update/{user_id}")
async def update_user_data(user_id: str, update: UserDataUpdate):
    try:
        # Get current user data
        user_ref = db.collection("user_data").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(status_code=404, detail="User data not found")
        
        current_data = user_doc.to_dict()
        
        # Update the specified field
        field_name = update.field.lower().replace(" ", "_")
        current_data[field_name] = update.value
        
        # Calculate new carbon footprint using ML model
        footprint_data_calculated = carbon_calculator.calculate(current_data)
        
        # Update Firestore (user_data collection)
        user_ref.update({
            field_name: update.value,
            "carbon_footprint": footprint_data_calculated["total_footprint"], # Update total footprint
            "carbon_footprint_breakdown": footprint_data_calculated["breakdown"], # Update breakdown
            "last_updated": datetime.now()
        })

        # Add new entry to carbon_footprints collection for historical data
        db.collection("carbon_footprints").add({
            "userId": user_id,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "total_footprint": footprint_data_calculated["total_footprint"],
            "breakdown": footprint_data_calculated["breakdown"]
        })
        
        # Get new recommendations
        recommendations = ml_service.get_recommendations(user_id)
        
        initialize_similarity_matrix()  # Profil güncellenince similarity matrix güncellensin

        return {
            "message": "User data updated successfully",
            "new_footprint": footprint_data_calculated["total_footprint"],
            "new_breakdown": footprint_data_calculated["breakdown"],
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"Error updating user data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Öneri motorunu başlat
recommendation_engine = RecommendationEngine()

# Veri setini yükle
try:
    user_data = pd.read_csv("data/Carbon Emission.csv")
    # Öneri motorunu verilerle başlat
    recommendation_engine.load_data(user_data, challenge_service.get_all_challenges())
except Exception as e:
    print(f"Veri yükleme hatası: {str(e)}")
    user_data = None

def calculate_footprint(user_data: dict) -> dict:
    try:
        print(f"Calculating footprint for user data: {user_data}")  # Debug log
        
        # Diet footprint calculation
        diet_type = user_data.get('diet_type', 'Omnivore')
        diet_footprint = {
            'Vegan': 1.0,
            'Vegetarian': 1.5,
            'Pescatarian': 2.0,
            'Omnivore': 2.5
        }.get(diet_type, 2.0)
        print(f"Diet footprint: {diet_footprint}")  # Debug log

        # Transportation footprint calculation
        transport_mode = user_data.get('transportation_mode', 'Private car')
        vehicle_type = user_data.get('vehicle_type', 'Petrol')
        
        transport_footprint = 0.0
        if transport_mode == 'Private car':
            transport_footprint = {
                'Petrol': 5.5,
                'Diesel': 6.0,
                'Electric': 3.0,
                'I don\'t own a vehicle': 0.0
            }.get(vehicle_type, 5.5)
        elif transport_mode == 'Public transport':
            transport_footprint = 2.0
        elif transport_mode == 'Walking/Bicycle':
            transport_footprint = 0.0
        print(f"Transport footprint: {transport_footprint}")  # Debug log

        # Housing footprint calculation
        heating_source = user_data.get('heating_source', 'Natural gas')
        energy_efficiency = user_data.get('home_energy_efficiency', 'No')
        
        base_housing = {
            'Coal': 4.0,
            'Natural gas': 3.0,
            'Electricity': 2.5,
            'Wood': 3.5
        }.get(heating_source, 3.0)
        
        efficiency_multiplier = {
            'No': 1.0,
            'Sometimes': 0.8,
            'Yes': 0.6
        }.get(energy_efficiency, 1.0)
        
        housing_footprint = base_housing * efficiency_multiplier
        print(f"Housing footprint: {housing_footprint}")  # Debug log

        # Lifestyle footprint calculation
        screen_time = user_data.get('screen_time', '4-8 hours')
        internet_usage = user_data.get('internet_usage', '4-8 hours')
        
        screen_footprint = {
            'Less than 4 hours': 0.5,
            '4-8 hours': 0.85,
            '8-16 hours': 1.2,
            'More than 16 hours': 1.5
        }.get(screen_time, 0.85)
        
        internet_footprint = {
            'Less than 4 hours': 0.5,
            '4-8 hours': 0.85,
            '8-16 hours': 1.2,
            'More than 16 hours': 1.5
        }.get(internet_usage, 0.85)
        
        lifestyle_footprint = (screen_footprint + internet_footprint) / 2
        print(f"Lifestyle footprint: {lifestyle_footprint}")  # Debug log

        # Waste footprint calculation
        recycling = user_data.get('recycling', 'I do not recycle')
        trash_size = user_data.get('trash_bag_size', 'Medium')
        
        recycling_multiplier = {
            'Paper': 0.8,
            'Plastic': 0.8,
            'Glass': 0.8,
            'Metal': 0.8,
            'I do not recycle': 1.0
        }.get(recycling, 1.0)
        
        trash_footprint = {
            'Small': 0.4,
            'Medium': 0.8,
            'Large': 1.2,
            'Extra large': 1.6
        }.get(trash_size, 0.8)
        
        waste_footprint = trash_footprint * recycling_multiplier
        print(f"Waste footprint: {waste_footprint}")  # Debug log

        # Calculate total footprint
        total_footprint = diet_footprint + transport_footprint + housing_footprint + lifestyle_footprint + waste_footprint
        print(f"Total footprint: {total_footprint}")  # Debug log

        return {
            'diet': diet_footprint,
            'transportation': transport_footprint,
            'housing': housing_footprint,
            'lifestyle': lifestyle_footprint,
            'waste': waste_footprint,
            'total': total_footprint,
            'recommendations': []
        }
    except Exception as e:
        print(f"Error calculating footprint: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return default values in case of error
        return {
            'diet': 2.0,
            'transportation': 5.5,
            'housing': 3.0,
            'lifestyle': 0.85,
            'waste': 0.64,
            'total': 12.49,
            'recommendations': []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 