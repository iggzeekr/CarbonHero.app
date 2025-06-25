from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

class MLService:
    def __init__(self):
        self.category_models = {
            "diet": None,
            "transportation": None,
            "housing": None,
            "lifestyle": None,
            "waste": None
        }
        self.label_encoders = {}
        self.scalers = {}
        self.user_item_matrix = None
        self.user_similarity_matrix = None
        self.model_dir = "models"
        self.user_id_to_index = {}
        self.index_to_user_id = {}
        self.model_feature_names = {}
        
        # Create models directory if it doesn't exist
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
            
        # Load existing models if they exist
        self._load_models()
    
    def _load_models(self):
        """Load existing models from disk if they exist"""
        for category in self.category_models.keys():
            model_path = os.path.join(self.model_dir, f"{category}_model.joblib")
            encoder_path = os.path.join(self.model_dir, f"{category}_encoder.joblib")
            scaler_path = os.path.join(self.model_dir, f"{category}_scaler.joblib")
            
            if os.path.exists(model_path):
                self.category_models[category] = joblib.load(model_path)
            if os.path.exists(encoder_path):
                self.label_encoders[category] = joblib.load(encoder_path)
            if os.path.exists(scaler_path):
                self.scalers[category] = joblib.load(scaler_path)
    
    def _save_models(self):
        """Save models to disk"""
        for category, model in self.category_models.items():
            if model is not None:
                joblib.dump(model, os.path.join(self.model_dir, f"{category}_model.joblib"))
            if category in self.label_encoders:
                joblib.dump(self.label_encoders[category], 
                          os.path.join(self.model_dir, f"{category}_encoder.joblib"))
            if category in self.scalers:
                joblib.dump(self.scalers[category], 
                          os.path.join(self.model_dir, f"{category}_scaler.joblib"))
    
    def train_category_model(self, category: str, training_data: List[Dict]):
        """Train a model for a specific category"""
        # Convert training data to DataFrame
        df = pd.DataFrame(training_data)
        
        # Prepare features and target
        X = df.drop(['carbon_footprint', 'userId'], axis=1)
        y = df['carbon_footprint']
        
        # Encode categorical features
        if category not in self.label_encoders:
            self.label_encoders[category] = {}
        
        for column in X.select_dtypes(include=['object']).columns:
            if column not in self.label_encoders[category]:
                self.label_encoders[category][column] = LabelEncoder()
            X[column] = self.label_encoders[category][column].fit_transform(X[column])
        
        # Scale features
        if category not in self.scalers:
            self.scalers[category] = StandardScaler()
        X_scaled = self.scalers[category].fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Save model
        self.category_models[category] = model
        self._save_models()
        
        return model.score(X_test, y_test)
    
    def predict_category_footprint(self, category: str, user_data: Dict) -> float:
        """Predict carbon footprint for a specific category"""
        if category not in self.category_models or self.category_models[category] is None:
            raise ValueError(f"No model available for category: {category}")
        
        # Prepare input data
        X = pd.DataFrame([user_data])
        
        # Encode categorical features
        for column in X.select_dtypes(include=['object']).columns:
            if column in self.label_encoders[category]:
                X[column] = self.label_encoders[category][column].transform(X[column])
        
        # Scale features
        X_scaled = self.scalers[category].transform(X)
        
        # Make prediction
        return float(self.category_models[category].predict(X_scaled)[0])
    
    def update_user_item_matrix(self, user_data: List[Dict]):
        """Update the user-item matrix for collaborative filtering"""
        df = pd.DataFrame(user_data)

        # Populate user_id_to_index and index_to_user_id mappings
        for i, user_id in enumerate(df['userId'].unique()):
            if user_id not in self.user_id_to_index:
                self.user_id_to_index[user_id] = len(self.user_id_to_index)
                self.index_to_user_id[self.user_id_to_index[user_id]] = user_id

        # Sadece string, int ve float tipindeki sütunları al
        allowed_types = (str, int, float)
        # Ensure we drop columns that are not features for collaborative filtering
        user_features = df.drop([col for col in ['userId', 'carbon_footprint', 'created_at', 'updated_at', 'recommendations'] if col in df.columns], axis=1)
        user_features = user_features[[col for col in user_features.columns
                                       if user_features[col].map(type).apply(lambda t: t in allowed_types).all()]]

        # Store feature names for later use in recommendations
        self.model_feature_names = user_features.columns.tolist()

        # Eksik değerleri doldur
        user_features = user_features.fillna(0)

        # Encode categorical features
        if 'collaborative' not in self.label_encoders:
            self.label_encoders['collaborative'] = {}
        for column in user_features.select_dtypes(include=['object', 'int', 'float']).columns:
            user_features[column] = user_features[column].astype(str)
            if column not in self.label_encoders['collaborative']:
                self.label_encoders['collaborative'][column] = LabelEncoder()
            
            # Fit and transform, handling unseen labels by fitting to existing data
            # If training data is limited, this might still lead to unseen labels if new values appear post-training.
            # For robust production, consider a predefined vocabulary or a more advanced handling strategy.
            try:
                user_features[column] = self.label_encoders['collaborative'][column].fit_transform(user_features[column])
            except ValueError as e:
                # This means new labels appeared after fit. Refit with all available data or handle specifically.
                print(f"[MLService] Warning: Unseen label during collaborative filtering encoding for column {column}. Error: {e}")
                # Re-fit the encoder with existing classes and new data if necessary. Not ideal, but a workaround.
                all_classes = np.unique(np.concatenate((self.label_encoders['collaborative'][column].classes_, user_features[column].unique())))
                self.label_encoders['collaborative'][column].classes_ = all_classes
                user_features[column] = self.label_encoders['collaborative'][column].transform(user_features[column])

        # Map user IDs to integer indices for the matrix
        user_features['user_index'] = df['userId'].apply(lambda uid: self.user_id_to_index.get(uid, -1))
        user_features = user_features[user_features['user_index'] != -1] # Filter out unmapped users
        
        # Create a dummy column if user_features is empty after mapping
        if user_features.empty:
            self.user_item_matrix = csr_matrix((0, len(user_features.columns) - 1)) # Empty matrix
            self.user_similarity_matrix = None
            return

        # Set user_index as index and drop it from features before creating sparse matrix
        user_features = user_features.set_index('user_index').sort_index()
        # Ensure the matrix has enough rows for all mapped users
        max_user_index = max(self.user_id_to_index.values())
        num_features = len(user_features.columns)

        # Convert to sparse matrix, ensuring correct shape
        self.user_item_matrix = csr_matrix((max_user_index + 1, num_features), dtype=np.float32)
        for idx, row in user_features.iterrows():
            self.user_item_matrix[idx, :] = row.values

        # Calculate user similarity matrix
        self.user_similarity_matrix = cosine_similarity(self.user_item_matrix)
    
    def get_similar_users(self, user_id: str, n_recommendations: int = 5) -> List[Tuple[str, float]]:
        """Get similar users based on collaborative filtering"""
        if self.user_similarity_matrix is None or user_id not in self.user_id_to_index:
            print(f"[MLService] User similarity matrix not initialized or user {user_id} not in index.") # Debug
            raise ValueError("User similarity matrix not initialized or user not found.")
        
        # Get user index from mapping
        user_idx = self.user_id_to_index[user_id]
        print(f"[MLService] Retrieved user index for {user_id}: {user_idx}") # Debug
        
        # Get similarity scores for the user
        user_similarities = self.user_similarity_matrix[user_idx]
        
        # Get top N similar users (excluding the user themselves)
        # Use argsort to get indices that would sort the array, then reverse for descending order
        # Slice to exclude the user themselves and get top N
        similar_indices = np.argsort(user_similarities)[::-1][1:n_recommendations+1]
        similar_scores = user_similarities[similar_indices]

        # Convert similar indices back to original user_ids
        similar_user_ids = [self.index_to_user_id[idx] for idx in similar_indices]
        
        return list(zip(similar_user_ids, similar_scores))
    
    def get_recommendations(self, user_id: str, n_recommendations: int = 5) -> List[Dict]:
        """Get personalized recommendations based on similar users"""
        print(f"[MLService] Getting recommendations for user: {user_id}") # Debug
        try:
            similar_users = self.get_similar_users(user_id, n_recommendations)
        except ValueError as e:
            print(f"[MLService] Error getting similar users: {e}") # Debug
            return [] # Return empty recommendations if similar users cannot be found
        
        recommendations = []
        for similar_user_id, similarity_score in similar_users:
            # Get the similar user's data
            if similar_user_id not in self.user_id_to_index:
                print(f"[MLService] Similar user ID {similar_user_id} not in user_id_to_index. Skipping.") # Debug
                continue
            
            similar_user_idx = self.user_id_to_index[similar_user_id]
            similar_user_data_row = self.user_item_matrix.getrow(similar_user_idx).toarray().flatten()
            
            # Get current user's data
            current_user_idx = self.user_id_to_index[user_id]
            current_user_data_row = self.user_item_matrix.getrow(current_user_idx).toarray().flatten()
            
            # Find features where similar user has better (lower) values
            # Assuming lower value means better (e.g., lower footprint contribution)
            better_features_indices = np.where(similar_user_data_row < current_user_data_row)[0]
            
            # Check ALL better features, not just the first one
            for feature_idx in better_features_indices:
                # Use stored feature names if available, otherwise fallback to hardcoded mapping
                if hasattr(self, 'model_feature_names') and self.model_feature_names and feature_idx < len(self.model_feature_names):
                    feature_name = self.model_feature_names[feature_idx]
                else:
                    # Fallback to hardcoded mapping
                    feature_mapping_for_recommendations = {
                        0: 'diet_type',
                        1: 'transportation_mode',
                        2: 'vehicle_type',
                        3: 'heating_source',
                        4: 'home_energy_efficiency',
                        5: 'shower_frequency',
                        6: 'screen_time',
                        7: 'internet_usage',
                        8: 'clothes_purchases',
                        9: 'recycling',
                        10: 'trash_bag_size',
                    }
                    if feature_idx in feature_mapping_for_recommendations:
                        feature_name = feature_mapping_for_recommendations[feature_idx]
                    else:
                        feature_name = "an unspecified feature"

                recommendation = {
                    "feature": feature_name,
                    "similarity_score": float(similarity_score),
                    "improvement_potential": float(current_user_data_row[feature_idx] - 
                                                similar_user_data_row[feature_idx])
                }
                recommendations.append(recommendation)
        
        return recommendations 