import numpy as np
from typing import Dict, List
import joblib
import os
import pandas as pd
from .ml_service import MLService

class CarbonCalculator:
    def __init__(self):
        self.ml_service = MLService()
        self.categories = ["diet", "transportation", "housing", "lifestyle", "waste"]
        # Load pre-trained model, label encoders, and scaler if exist
        base_dir = os.path.join(os.path.dirname(__file__), "../../models")
        self.model_path = os.path.join(base_dir, "carbon_model.joblib")
        self.label_encoders_path = os.path.join(base_dir, "label_encoders.joblib")
        self.scaler_path = os.path.join(base_dir, "scaler.joblib")
        try:
            self.model = joblib.load(self.model_path)
        except:
            self.model = None
        try:
            self.label_encoders = joblib.load(self.label_encoders_path)
        except:
            self.label_encoders = None
        try:
            self.scaler = joblib.load(self.scaler_path)
        except:
            self.scaler = None

    def _encode_user_data(self, user_data: Dict) -> pd.DataFrame:
        # Kategorik ve sayısal encoding işlemleri
        processed_data = {}
        # Kategorik değişkenler
        categorical_columns = [
            'Body Type', 'Sex', 'Diet', 'How Often Shower',
            'Heating Energy Source', 'Transport', 'Vehicle Type',
            'Social Activity', 'Waste Bag Size', 'Energy efficiency',
            'Recycling'
        ]
        # Android'den gelen field mapping
        android_to_model = {
            'diet_type': 'Diet',
            'transportation_mode': 'Transport',
            'vehicle_type': 'Vehicle Type',
            'heating_source': 'Heating Energy Source',
            'home_energy_efficiency': 'Energy efficiency',
            'shower_frequency': 'How Often Shower',
            'screen_time': 'How Long TV PC Daily Hour',
            'internet_usage': 'How Long Internet Daily Hour',
            'clothes_purchases': 'How Many New Clothes Monthly',
            'recycling': 'Recycling',
            'trash_bag_size': 'Waste Bag Size',
        }
        # Kategorik encoding
        for android_key, model_key in android_to_model.items():
            if model_key in categorical_columns:
                if android_key in user_data:
                    value = user_data[android_key]
                    if isinstance(value, str):
                        processed_data[model_key] = value.strip().title()
                    else:
                        processed_data[model_key] = value # Keep non-string values as is
        # Sayısal encoding (örnek: hepsi 0 olarak atanacak çünkü Android'de yok)
        numerical_columns = [
            'Monthly Grocery Bill', 'Vehicle Monthly Distance Km',
            'Waste Bag Weekly Count', 'How Long TV PC Daily Hour',
            'How Many New Clothes Monthly', 'How Long Internet Daily Hour'
        ]
        for col in numerical_columns:
            if col in ['How Long TV PC Daily Hour', 'How Many New Clothes Monthly', 'How Long Internet Daily Hour']:
                for android_key, model_key in android_to_model.items():
                    if model_key == col and android_key in user_data:
                        # Already handled in categorical, ensure consistent format if it's a number
                        if isinstance(user_data[android_key], (int, float)):
                            processed_data[model_key] = user_data[android_key]
                        elif isinstance(user_data[android_key], str):
                            # If it's a string that should be numeric, try to convert
                            try:
                                processed_data[model_key] = float(user_data[android_key])
                            except ValueError:
                                processed_data[model_key] = 0.0 # Default to 0 if conversion fails
                        else:
                            processed_data[model_key] = 0.0
            else:
                processed_data[col] = 0.0 # Default for non-existent numerical features

        # Eksik sütunları 0 ile doldur
        all_features = categorical_columns + numerical_columns
        for col in all_features:
            if col not in processed_data:
                processed_data[col] = 0
        
        # DataFrame oluştur
        X_pred = pd.DataFrame([processed_data])
        return X_pred

    def calculate(self, user_data: Dict) -> Dict:
        """
        Calculate carbon footprint based on user data using ML models
        """
        footprint = {
            "total_footprint": 0.0,
            "breakdown": {},
            "recommendations": []
        }
        
        # Try to use ML models for each category
        for category in self.categories:
            try:
                category_footprint = self.ml_service.predict_category_footprint(category, user_data)
                footprint["breakdown"][category] = category_footprint
                footprint["total_footprint"] += category_footprint
                print(f"[CarbonCalculator] Category {category} footprint: {category_footprint}")  # Debug log
            except ValueError as e:
                print(f"[CarbonCalculator] Error calculating {category} footprint with ML model: {str(e)}. Falling back.")  # Debug log
                # Fallback to rule-based calculation if model not available or error occurs
                category_footprint = self._calculate_category_footprint(category, user_data)
                footprint["breakdown"][category] = category_footprint
                footprint["total_footprint"] += category_footprint
                print(f"[CarbonCalculator] Fallback {category} footprint: {category_footprint}")  # Debug log
            except Exception as e:
                print(f"[CarbonCalculator] Unexpected error calculating {category} footprint: {str(e)}. Falling back.") # Debug log
                category_footprint = self._calculate_category_footprint(category, user_data)
                footprint["breakdown"][category] = category_footprint
                footprint["total_footprint"] += category_footprint
                print(f"[CarbonCalculator] Fallback {category} footprint (unexpected error): {category_footprint}")  # Debug log
        
        print(f"[CarbonCalculator] Final footprint breakdown before recommendations: {footprint['breakdown']}")  # Debug log
        print(f"[CarbonCalculator] Final total footprint before recommendations: {footprint['total_footprint']}") # Debug log
        
        # Get personalized recommendations
        try:
            recommendations = self.ml_service.get_recommendations(user_data["userId"])
            footprint["recommendations"] = self._format_recommendations(recommendations)
            print(f"[CarbonCalculator] Recommendations: {footprint['recommendations']}") # Debug log
        except ValueError as e:
            print(f"[CarbonCalculator] Error getting ML recommendations: {str(e)}. Falling back to rule-based.") # Debug log
            # Fallback to rule-based recommendations if collaborative filtering not available
            footprint["recommendations"] = self._get_rule_based_recommendations(footprint["breakdown"])
            print(f"[CarbonCalculator] Fallback Recommendations: {footprint['recommendations']}") # Debug log
        except Exception as e:
            print(f"[CarbonCalculator] Unexpected error getting recommendations: {str(e)}. Falling back to rule-based.") # Debug log
            footprint["recommendations"] = self._get_rule_based_recommendations(footprint["breakdown"])
            print(f"[CarbonCalculator] Fallback Recommendations (unexpected error): {footprint['recommendations']}") # Debug log
        
        print(f"[CarbonCalculator] Final footprint object being returned: {footprint}") # Debug log
        return footprint
    
    def _calculate_category_footprint(self, category: str, user_data: Dict) -> float:
        """Fallback rule-based calculation for a category"""
        if category == "diet":
            return self._calculate_diet_footprint(user_data)
        elif category == "transportation":
            return self._calculate_transport_footprint(user_data)
        elif category == "housing":
            return self._calculate_housing_footprint(user_data)
        elif category == "lifestyle":
            return self._calculate_lifestyle_footprint(user_data)
        elif category == "waste":
            return self._calculate_waste_footprint(user_data)
        return 0.0
    
    def _format_recommendations(self, recommendations: List[Dict]) -> List[str]:
        """Format ML-based recommendations into readable strings"""
        formatted_recommendations = []
        for rec in recommendations:
            feature = rec["feature"]
            improvement = rec["improvement_potential"]
            similarity = rec["similarity_score"]
            
            # Create recommendation message based on feature
            if feature == "diet_type":
                formatted_recommendations.append(
                    f"Similar users with {similarity:.1%} similarity have reduced their diet impact by {improvement:.1f} units"
                )
            elif feature == "transportation_mode":
                formatted_recommendations.append(
                    f"Consider changing your transportation habits like {similarity:.1%} of similar users"
                )
            # Add more feature-specific recommendations as needed
            
        return formatted_recommendations
    
    def _get_rule_based_recommendations(self, breakdown: Dict) -> List[str]:
        """Generate rule-based recommendations based on footprint breakdown"""
        recommendations = []
        
        # Diet recommendations
        if breakdown["diet"] > 2.0:
            recommendations.append("Consider reducing meat consumption or trying plant-based meals")
        
        # Transportation recommendations
        if breakdown["transportation"] > 2.0:
            recommendations.append("Try using public transport or carpooling more often")
        
        # Housing recommendations
        if breakdown["housing"] > 2.0:
            recommendations.append("Consider improving home insulation and using energy-efficient appliances")
        
        # Lifestyle recommendations
        if breakdown["lifestyle"] > 1.5:
            recommendations.append("Try reducing screen time and taking shorter showers")
        
        # Waste recommendations
        if breakdown["waste"] > 1.5:
            recommendations.append("Start recycling more and reduce single-use plastics")
        
        return recommendations
    
    def _calculate_diet_footprint(self, user_data: Dict) -> float:
        """Calculate carbon footprint from diet choices"""
        diet_scores = {
            "Vegan": 1.5,
            "Vegetarian": 2.0,
            "Pescatarian": 2.5,
            "Omnivore": 3.0
        }
        return diet_scores.get(user_data["diet_type"], 2.5)
    
    def _calculate_transport_footprint(self, user_data: Dict) -> float:
        """Calculate carbon footprint from transportation"""
        transport_scores = {
            "Public transport": 1.0,
            "Private car": 3.0,
            "Walking/Bicycle": 0.5
        }
        
        vehicle_scores = {
            "Petrol": 2.5,
            "Diesel": 2.0,
            "Electric": 1.0,
            "I don't own a vehicle": 0.0
        }
        
        base_score = transport_scores.get(user_data["transportation_mode"], 2.0)
        vehicle_score = vehicle_scores.get(user_data["vehicle_type"], 1.5)
        
        return base_score + vehicle_score
    
    def _calculate_housing_footprint(self, user_data: Dict) -> float:
        """Calculate carbon footprint from housing"""
        heating_scores = {
            "Coal": 3.0,
            "Natural gas": 2.0,
            "Electricity": 1.5,
            "Wood": 2.5
        }
        
        efficiency_scores = {
            "No": 2.0,
            "Sometimes": 1.5,
            "Yes": 1.0
        }
        
        heating_score = heating_scores.get(user_data["heating_source"], 2.0)
        efficiency_score = efficiency_scores.get(user_data["home_energy_efficiency"], 1.5)
        
        return heating_score * efficiency_score
    
    def _calculate_lifestyle_footprint(self, user_data: Dict) -> float:
        """Calculate carbon footprint from lifestyle choices"""
        shower_scores = {
            "Daily": 1.0,
            "Twice a day": 1.5,
            "More frequently": 2.0,
            "Less frequently": 0.8
        }
        
        screen_scores = {
            "Less than 4 hours": 0.8,
            "4-8 hours": 1.0,
            "8-16 hours": 1.5,
            "More than 16 hours": 2.0
        }
        
        internet_scores = {
            "Less than 4 hours": 0.8,
            "4-8 hours": 1.0,
            "8-16 hours": 1.5,
            "More than 16 hours": 2.0
        }
        
        clothes_scores = {
            "0-10": 0.8,
            "11-20": 1.2,
            "21-30": 1.5,
            "31+": 2.0
        }
        
        shower_score = shower_scores.get(user_data["shower_frequency"], 1.0)
        screen_score = screen_scores.get(user_data["screen_time"], 1.0)
        internet_score = internet_scores.get(user_data["internet_usage"], 1.0)
        clothes_score = clothes_scores.get(user_data["clothes_purchases"], 1.0)
        
        return (shower_score + screen_score + internet_score + clothes_score) / 4
    
    def _calculate_waste_footprint(self, user_data: Dict) -> float:
        """Calculate carbon footprint from waste management"""
        recycling_scores = {
            "Paper": 0.8,
            "Plastic": 0.8,
            "Glass": 0.8,
            "Metal": 0.8,
            "I do not recycle": 2.0
        }
        
        trash_scores = {
            "Small": 0.8,
            "Medium": 1.0,
            "Large": 1.5,
            "Extra large": 2.0
        }
        
        recycling_score = recycling_scores.get(user_data["recycling"], 1.5)
        trash_score = trash_scores.get(user_data["trash_bag_size"], 1.0)
        
        return recycling_score * trash_score
    
    def train_models(self, training_data: List[Dict]):
        """Train ML models for each category"""
        for category in self.categories:
            try:
                score = self.ml_service.train_category_model(category, training_data)
                print(f"Trained {category} model with R² score: {score:.3f}")
            except Exception as e:
                print(f"Error training {category} model: {str(e)}")
    
    def update_collaborative_filtering(self, user_data: List[Dict]):
        """Update the collaborative filtering system with new user data"""
        try:
            self.ml_service.update_user_item_matrix(user_data)
            print("Updated collaborative filtering system successfully")
        except Exception as e:
            print(f"Error updating collaborative filtering: {str(e)}") 