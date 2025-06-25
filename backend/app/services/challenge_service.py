from typing import List, Dict
from firebase_admin import firestore
from ..ml.collaborative_filter import CollaborativeFilter

class ChallengeService:
    def __init__(self):
        self.db = firestore.client()
        self.collaborative_filter = CollaborativeFilter()
        
        # Predefined challenges with categories and difficulty levels
        self.challenges = {
            "diet": [
                {
                    "id": "diet_1",
                    "title": "Meatless Monday",
                    "description": "Go meat-free every Monday for a month",
                    "category": "diet",
                    "difficulty": "easy",
                    "carbon_savings": 2.5,  # kg CO2 per week
                    "duration_days": 30
                },
                {
                    "id": "diet_2",
                    "title": "Local Produce Week",
                    "description": "Eat only locally grown produce for one week",
                    "category": "diet",
                    "difficulty": "medium",
                    "carbon_savings": 3.0,
                    "duration_days": 7
                },
                {
                    "id": "diet_3",
                    "title": "Vegan Challenge",
                    "description": "Try a vegan diet for two weeks",
                    "category": "diet",
                    "difficulty": "hard",
                    "carbon_savings": 5.0,
                    "duration_days": 14
                },
                {
                    "id": "diet_4",
                    "title": "Plant-Based Meal",
                    "description": "Try a completely plant-based meal today",
                    "category": "diet",
                    "difficulty": "easy",
                    "carbon_savings": 3.5,
                    "duration_days": 1
                },
                {
                    "id": "diet_5",
                    "title": "Reduce Meat Consumption",
                    "description": "Skip meat for one meal today",
                    "category": "diet",
                    "difficulty": "medium",
                    "carbon_savings": 2.0,
                    "duration_days": 1
                },
                {
                    "id": "diet_6",
                    "title": "Local Produce Challenge",
                    "description": "Buy only locally grown produce today",
                    "category": "diet",
                    "difficulty": "easy",
                    "carbon_savings": 2.5,
                    "duration_days": 1
                },
                {
                    "id": "diet_7",
                    "title": "Vegan Day Challenge",
                    "description": "Go completely vegan for one day",
                    "category": "diet",
                    "difficulty": "hard",
                    "carbon_savings": 5.0,
                    "duration_days": 1
                }
            ],
            "transportation": [
                {
                    "id": "transport_1",
                    "title": "Bike to Work",
                    "description": "Use a bicycle for commuting three times a week",
                    "category": "transportation",
                    "difficulty": "medium",
                    "carbon_savings": 4.0,
                    "duration_days": 30
                },
                {
                    "id": "transport_2",
                    "title": "Public Transport Week",
                    "description": "Use only public transport for one week",
                    "category": "transportation",
                    "difficulty": "easy",
                    "carbon_savings": 3.5,
                    "duration_days": 7
                },
                {
                    "id": "transport_3",
                    "title": "Car-Free Month",
                    "description": "Avoid using a car for an entire month",
                    "category": "transportation",
                    "difficulty": "hard",
                    "carbon_savings": 15.0,
                    "duration_days": 30
                },
                {
                    "id": "transport_4",
                    "title": "Walk or Bike",
                    "description": "Choose walking or biking instead of driving for short trips",
                    "category": "transportation",
                    "difficulty": "easy",
                    "carbon_savings": 2.0,
                    "duration_days": 1
                },
                {
                    "id": "transport_5",
                    "title": "Public Transport",
                    "description": "Use public transport instead of private car",
                    "category": "transportation",
                    "difficulty": "medium",
                    "carbon_savings": 2.5,
                    "duration_days": 1
                },
                {
                    "id": "transport_6",
                    "title": "Carpool Challenge",
                    "description": "Share a ride with someone today",
                    "category": "transportation",
                    "difficulty": "medium",
                    "carbon_savings": 2.0,
                    "duration_days": 1
                },
                {
                    "id": "transport_7",
                    "title": "No Car Day",
                    "description": "Don't use your car at all today",
                    "category": "transportation",
                    "difficulty": "hard",
                    "carbon_savings": 4.0,
                    "duration_days": 1
                }
            ],
            "energy": [
                {
                    "id": "energy_1",
                    "title": "Power Down Hour",
                    "description": "Turn off all non-essential electronics for one hour daily",
                    "category": "energy",
                    "difficulty": "easy",
                    "carbon_savings": 1.0,
                    "duration_days": 30
                },
                {
                    "id": "energy_2",
                    "title": "Smart Thermostat",
                    "description": "Optimize your home temperature settings",
                    "category": "energy",
                    "difficulty": "medium",
                    "carbon_savings": 2.5,
                    "duration_days": 30
                },
                {
                    "id": "energy_3",
                    "title": "Renewable Energy Switch",
                    "description": "Switch to a renewable energy provider",
                    "category": "energy",
                    "difficulty": "hard",
                    "carbon_savings": 20.0,
                    "duration_days": 365
                },
                {
                    "id": "energy_4",
                    "title": "Energy Saver",
                    "description": "Turn off lights and unplug devices when not in use",
                    "category": "energy",
                    "difficulty": "easy",
                    "carbon_savings": 1.0,
                    "duration_days": 1
                },
                {
                    "id": "energy_5",
                    "title": "Temperature Control",
                    "description": "Reduce heating/cooling by 2 degrees",
                    "category": "energy",
                    "difficulty": "medium",
                    "carbon_savings": 1.5,
                    "duration_days": 1
                },
                {
                    "id": "energy_6",
                    "title": "LED Bulb Switch",
                    "description": "Replace one regular bulb with LED today",
                    "category": "energy",
                    "difficulty": "easy",
                    "carbon_savings": 0.5,
                    "duration_days": 1
                },
                {
                    "id": "energy_7",
                    "title": "Energy Audit",
                    "description": "Conduct a home energy audit today",
                    "category": "energy",
                    "difficulty": "hard",
                    "carbon_savings": 2.0,
                    "duration_days": 1
                }
            ],
            "waste": [
                {
                    "id": "waste_1",
                    "title": "Zero Waste Week",
                    "description": "Minimize waste production for one week",
                    "category": "waste",
                    "difficulty": "medium",
                    "carbon_savings": 2.0,
                    "duration_days": 7
                },
                {
                    "id": "waste_2",
                    "title": "Recycling Master",
                    "description": "Properly sort and recycle all waste for a month",
                    "category": "waste",
                    "difficulty": "easy",
                    "carbon_savings": 1.5,
                    "duration_days": 30
                },
                {
                    "id": "waste_3",
                    "title": "Compost Challenge",
                    "description": "Start composting organic waste",
                    "category": "waste",
                    "difficulty": "hard",
                    "carbon_savings": 3.0,
                    "duration_days": 90
                },
                {
                    "id": "waste_4",
                    "title": "Zero Waste Meal",
                    "description": "Prepare a meal using all ingredients with no waste",
                    "category": "waste",
                    "difficulty": "medium",
                    "carbon_savings": 1.5,
                    "duration_days": 1
                },
                {
                    "id": "waste_5",
                    "title": "Recycle More",
                    "description": "Properly separate and recycle all waste today",
                    "category": "waste",
                    "difficulty": "easy",
                    "carbon_savings": 1.0,
                    "duration_days": 1
                },
                {
                    "id": "waste_6",
                    "title": "Zero Waste Day",
                    "description": "Produce no waste at all today",
                    "category": "waste",
                    "difficulty": "hard",
                    "carbon_savings": 2.5,
                    "duration_days": 1
                }
            ],
            "lifestyle": [
                {
                    "id": "lifestyle_1",
                    "title": "Digital Detox",
                    "description": "Reduce screen time by 50% for a week",
                    "category": "lifestyle",
                    "difficulty": "medium",
                    "carbon_savings": 1.0,
                    "duration_days": 7
                },
                {
                    "id": "lifestyle_2",
                    "title": "Second-Hand Shopping",
                    "description": "Buy only second-hand items for a month",
                    "category": "lifestyle",
                    "difficulty": "hard",
                    "carbon_savings": 4.0,
                    "duration_days": 30
                },
                {
                    "id": "lifestyle_3",
                    "title": "Water Conservation",
                    "description": "Reduce water usage by 25% for two weeks",
                    "category": "lifestyle",
                    "difficulty": "easy",
                    "carbon_savings": 1.5,
                    "duration_days": 14
                },
                {
                    "id": "lifestyle_4",
                    "title": "Reduce Water Usage",
                    "description": "Take shorter showers and turn off taps when not in use",
                    "category": "lifestyle",
                    "difficulty": "easy",
                    "carbon_savings": 0.8,
                    "duration_days": 1
                },
                {
                    "id": "lifestyle_5",
                    "title": "Minimalist Challenge",
                    "description": "Don't buy anything non-essential today",
                    "category": "lifestyle",
                    "difficulty": "medium",
                    "carbon_savings": 1.0,
                    "duration_days": 1
                }
            ]
        }

    def get_all_challenges(self) -> List[Dict]:
        """Get all available challenges"""
        all_challenges = []
        for category_challenges in self.challenges.values():
            all_challenges.extend(category_challenges)
        return all_challenges

    def get_challenges_by_category(self, category: str) -> List[Dict]:
        """Get challenges for a specific category"""
        return self.challenges.get(category, [])

    def get_challenges_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get challenges for a specific difficulty level"""
        return [
            challenge
            for category_challenges in self.challenges.values()
            for challenge in category_challenges
            if challenge["difficulty"] == difficulty
        ]

    def get_recommended_challenges(self, user_data: Dict, n_recommendations: int = 5) -> List[Dict]:
        """Get personalized challenge recommendations"""
        # Get collaborative filtering recommendations
        cf_recommendations = self.collaborative_filter.recommend_challenges(
            user_data, n_recommendations
        )
        
        # If we have collaborative filtering recommendations, use them
        if cf_recommendations:
            return [
                {
                    "challenge": self._get_challenge_by_id(rec["challenge_id"]),
                    "score": rec["score"]
                }
                for rec in cf_recommendations
                if self._get_challenge_by_id(rec["challenge_id"])
            ]
        
        # Fallback to rule-based recommendations based on user data
        return self._get_rule_based_recommendations(user_data, n_recommendations)

    def _get_challenge_by_id(self, challenge_id: str) -> Dict:
        """Get a challenge by its ID"""
        for category_challenges in self.challenges.values():
            for challenge in category_challenges:
                if challenge["id"] == challenge_id:
                    return challenge
        return None

    def _get_rule_based_recommendations(self, user_data: Dict, n_recommendations: int) -> List[Dict]:
        """Get recommendations based on user data and predefined rules"""
        recommendations = []
        
        # Diet-based recommendations
        if user_data.get("diet_type") in ["Omnivore", "Pescatarian"]:
            recommendations.extend([
                {"challenge": challenge, "score": 0.9}
                for challenge in self.challenges["diet"]
                if challenge["difficulty"] == "easy"
            ])
        
        # Transportation-based recommendations
        if user_data.get("vehicle_type") in ["Petrol", "Diesel"]:
            recommendations.extend([
                {"challenge": challenge, "score": 0.8}
                for challenge in self.challenges["transportation"]
                if challenge["difficulty"] == "medium"
            ])
        
        # Energy-based recommendations
        if user_data.get("home_energy_efficiency") == "No":
            recommendations.extend([
                {"challenge": challenge, "score": 0.85}
                for challenge in self.challenges["energy"]
                if challenge["difficulty"] == "easy"
            ])
        
        # Waste-based recommendations
        if user_data.get("recycling") == "I do not recycle":
            recommendations.extend([
                {"challenge": challenge, "score": 0.75}
                for challenge in self.challenges["waste"]
                if challenge["difficulty"] == "easy"
            ])
        
        # Lifestyle-based recommendations
        if user_data.get("screen_time") in ["8-16 hours", "More than 16 hours"]:
            recommendations.extend([
                {"challenge": challenge, "score": 0.7}
                for challenge in self.challenges["lifestyle"]
                if challenge["difficulty"] == "medium"
            ])
        
        # Sort by score and return top N recommendations
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:n_recommendations]

    def start_challenge(self, user_id: str, challenge_id: str) -> Dict:
        """Start a new challenge for a user"""
        challenge = self._get_challenge_by_id(challenge_id)
        if not challenge:
            raise ValueError(f"Challenge {challenge_id} not found")
        
        # Create challenge record
        challenge_data = {
            "userId": user_id,
            "challengeId": challenge_id,
            "startDate": firestore.SERVER_TIMESTAMP,
            "status": "in_progress",
            "progress": 0,
            "completed": False
        }
        
        # Save to Firestore
        doc_ref = self.db.collection("user_challenges").document()
        doc_ref.set(challenge_data)
        
        return {
            "challenge": challenge,
            "user_challenge": {**challenge_data, "id": doc_ref.id}
        }

    def update_challenge_progress(self, user_challenge_id: str, progress: float) -> Dict:
        """Update the progress of a user's challenge"""
        doc_ref = self.db.collection("user_challenges").document(user_challenge_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise ValueError(f"User challenge {user_challenge_id} not found")
        
        challenge_data = doc.to_dict()
        challenge = self._get_challenge_by_id(challenge_data["challengeId"])
        
        # Update progress
        new_progress = min(100, max(0, progress))
        is_completed = new_progress >= 100
        
        update_data = {
            "progress": new_progress,
            "completed": is_completed,
            "status": "completed" if is_completed else "in_progress"
        }
        
        if is_completed:
            update_data["completionDate"] = firestore.SERVER_TIMESTAMP
        
        doc_ref.update(update_data)
        
        return {
            "challenge": challenge,
            "user_challenge": {**challenge_data, **update_data, "id": doc_ref.id}
        }

    def get_user_challenges(self, user_id: str) -> List[Dict]:
        """Get all challenges for a user"""
        challenges_ref = self.db.collection("user_challenges")\
            .where("userId", "==", user_id)\
            .stream()
        
        user_challenges = []
        for doc in challenges_ref:
            challenge_data = doc.to_dict()
            challenge = self._get_challenge_by_id(challenge_data["challengeId"])
            if challenge:
                user_challenges.append({
                    "challenge": challenge,
                    "user_challenge": {**challenge_data, "id": doc.id}
                })
        
        return user_challenges 