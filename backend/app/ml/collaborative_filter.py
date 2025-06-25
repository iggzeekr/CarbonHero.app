import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict
import pandas as pd
from firebase_admin import firestore

class CollaborativeFilter:
    def __init__(self):
        self.db = firestore.client()
        self.user_matrix = None
        self.user_similarity = None
        self._load_data()

    def _load_data(self):
        """Load and preprocess user data from Firestore"""
        # Get all user data
        users_ref = self.db.collection("user_data").stream()
        users_data = [doc.to_dict() for doc in users_ref]
        
        if not users_data:
            return
        
        # Convert categorical data to numerical features
        self.user_matrix = self._preprocess_user_data(users_data)
        
        # Calculate user similarity matrix
        self.user_similarity = cosine_similarity(self.user_matrix)

    def _preprocess_user_data(self, users_data: List[Dict]) -> np.ndarray:
        """Convert categorical user data to numerical features"""
        # Define feature mappings
        feature_mappings = {
            "body_type": {
                "Underweight": 0, "Normal": 1, "Overweight": 2, "Obese": 3
            },
            "gender": {"Female": 0, "Male": 1},
            "diet_type": {
                "Vegan": 0, "Vegetarian": 1, "Pescatarian": 2, "Omnivore": 3
            },
            "shower_frequency": {
                "Daily": 1, "Twice a day": 2, "More frequently": 3, "Less frequently": 0
            },
            "heating_source": {
                "Coal": 3, "Natural gas": 2, "Electricity": 1, "Wood": 2.5
            },
            "transportation_mode": {
                "Public transport": 0, "Private car": 2, "Walking/Bicycle": 0.5
            },
            "vehicle_type": {
                "Petrol": 2.5, "Diesel": 2, "Electric": 1, "I don't own a vehicle": 0
            },
            "social_activity": {
                "Never": 0, "Sometimes": 1, "Often": 2
            },
            "trash_bag_size": {
                "Small": 0.8, "Medium": 1, "Large": 1.5, "Extra large": 2
            },
            "air_travel_frequency": {
                "Never": 0, "Rarely": 1, "Frequently": 2, "Very frequently": 3
            },
            "home_energy_efficiency": {
                "No": 2, "Sometimes": 1.5, "Yes": 1
            },
            "recycling": {
                "Paper": 0.8, "Plastic": 0.8, "Glass": 0.8, 
                "Metal": 0.8, "I do not recycle": 2
            },
            "cooking_devices": {
                "Stove": 1, "Oven": 1.5, "Microwave": 0.8, 
                "Airfryer": 0.7, "Grill": 1.2
            },
            "screen_time": {
                "Less than 4 hours": 0.8, "4-8 hours": 1,
                "8-16 hours": 1.5, "More than 16 hours": 2
            },
            "clothes_purchases": {
                "0-10": 0.8, "11-20": 1.2, "21-30": 1.5, "31+": 2
            },
            "internet_usage": {
                "Less than 4 hours": 0.8, "4-8 hours": 1,
                "8-16 hours": 1.5, "More than 16 hours": 2
            }
        }
        
        # Convert user data to numerical features
        numerical_data = []
        for user in users_data:
            user_features = []
            for feature, mapping in feature_mappings.items():
                value = user.get(feature, list(mapping.keys())[0])
                if isinstance(value, list):
                    v = value[0] if value else 0
                else:
                    v = value
                user_features.append(mapping.get(v, 0))
            numerical_data.append(user_features)
        
        return np.array(numerical_data)

    def find_similar_users(self, user_data: Dict, n_similar: int = 5) -> List[Dict]:
        """Find similar users based on user data"""
        if self.user_matrix is None or self.user_similarity is None:
            return []
        
        # Convert input user data to numerical features
        user_features = self._preprocess_user_data([user_data])[0]
        
        # Calculate similarity with all users
        similarities = cosine_similarity([user_features], self.user_matrix)[0]
        
        # Get indices of most similar users
        similar_indices = np.argsort(similarities)[::-1][1:n_similar+1]
        
        # Get user data for similar users
        users_ref = self.db.collection("user_data").stream()
        users_data = [doc.to_dict() for doc in users_ref]
        
        similar_users = []
        for idx in similar_indices:
            if idx < len(users_data):
                similar_users.append({
                    "user_data": users_data[idx],
                    "similarity_score": float(similarities[idx])
                })
        
        return similar_users

    def get_user_challenges(self, user_id: str) -> List[Dict]:
        """Get challenges completed by a user"""
        challenges_ref = self.db.collection("user_challenges")\
            .where("userId", "==", user_id)\
            .stream()
        
        return [doc.to_dict() for doc in challenges_ref]

    def recommend_challenges(self, user_data: Dict, n_recommendations: int = 5) -> List[Dict]:
        """Recommend challenges based on similar users' behavior"""
        # Find similar users
        similar_users = self.find_similar_users(user_data)
        
        if not similar_users:
            return []
        
        # Get challenges completed by similar users
        all_challenges = []
        for similar_user in similar_users:
            user_id = similar_user["user_data"].get("userId")
            if user_id:
                challenges = self.get_user_challenges(user_id)
                for challenge in challenges:
                    challenge["similarity_score"] = similar_user["similarity_score"]
                all_challenges.extend(challenges)
        
        # Aggregate and sort challenges by similarity score
        challenge_scores = {}
        for challenge in all_challenges:
            challenge_id = challenge["challengeId"]
            if challenge_id not in challenge_scores:
                challenge_scores[challenge_id] = {
                    "challenge": challenge,
                    "total_score": 0,
                    "count": 0
                }
            
            challenge_scores[challenge_id]["total_score"] += challenge["similarity_score"]
            challenge_scores[challenge_id]["count"] += 1
        
        # Calculate average scores and sort
        recommendations = []
        for challenge_id, data in challenge_scores.items():
            avg_score = data["total_score"] / data["count"]
            recommendations.append({
                "challenge_id": challenge_id,
                "challenge_data": data["challenge"],
                "score": avg_score
            })
        
        # Sort by score and return top N recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:n_recommendations] 