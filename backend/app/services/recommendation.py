from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

class RecommendationEngine:
    def __init__(self):
        self.user_matrix = None
        self.challenge_matrix = None
        self.user_similarities = None
    
    def load_data(self, user_data: pd.DataFrame, challenge_data: List[Dict[str, Any]]):
        """Kullanıcı ve meydan okuma verilerini yükler."""
        # Kullanıcı verilerini sayısallaştır
        self.user_matrix = self._preprocess_user_data(user_data)
        
        # Meydan okuma verilerini matrise dönüştür
        self.challenge_matrix = self._create_challenge_matrix(challenge_data)
        
        # Kullanıcı benzerliklerini hesapla
        self.user_similarities = cosine_similarity(self.user_matrix)
    
    def _preprocess_user_data(self, user_data: pd.DataFrame) -> np.ndarray:
        """Kullanıcı verilerini sayısallaştırır."""
        # Kategorik değişkenleri one-hot encoding ile dönüştür
        categorical_columns = [
            'Body Type', 'Sex', 'Diet', 'How Often Shower',
            'Heating Energy Source', 'Transport', 'Vehicle Type',
            'Social Activity', 'Energy efficiency', 'Recycling'
        ]
        
        # Sayısal değişkenleri normalize et
        numerical_columns = [
            'Monthly Grocery Bill', 'Vehicle Monthly Distance Km',
            'Waste Bag Weekly Count', 'How Long TV PC Daily Hour',
            'How Many New Clothes Monthly', 'How Long Internet Daily Hour'
        ]
        
        # Kategorik değişkenleri dönüştür
        categorical_data = pd.get_dummies(user_data[categorical_columns])
        
        # Sayısal değişkenleri normalize et
        numerical_data = (user_data[numerical_columns] - user_data[numerical_columns].mean()) / user_data[numerical_columns].std()
        
        # Tüm verileri birleştir
        processed_data = pd.concat([categorical_data, numerical_data], axis=1)
        
        return processed_data.values
    
    def _create_challenge_matrix(self, challenge_data: List[Dict[str, Any]]) -> np.ndarray:
        """Meydan okuma verilerini matrise dönüştürür."""
        # Meydan okuma özelliklerini sayısallaştır
        challenge_features = []
        for challenge in challenge_data:
            features = [
                challenge['difficulty'] == 'easy',
                challenge['difficulty'] == 'medium',
                challenge['difficulty'] == 'hard',
                challenge['category'] == 'diet',
                challenge['category'] == 'transportation',
                challenge['category'] == 'energy',
                challenge['category'] == 'waste',
                challenge['category'] == 'lifestyle',
                challenge['carbon_savings'] / 100,  # Normalize edilmiş karbon tasarrufu
                challenge['duration_days'] / 30  # Normalize edilmiş süre
            ]
            challenge_features.append(features)
        
        return np.array(challenge_features)
    
    def get_similar_users(self, user_id: int, n_users: int = 5) -> List[int]:
        """Belirli bir kullanıcıya benzer kullanıcıları bulur."""
        if self.user_similarities is None:
            raise ValueError("Önce load_data() metodunu çağırın")
        
        # Kullanıcının benzerlik skorlarını al
        user_similarities = self.user_similarities[user_id]
        
        # Kendisi hariç en benzer n kullanıcıyı bul
        similar_users = np.argsort(user_similarities)[::-1][1:n_users+1]
        
        return similar_users.tolist()
    
    def recommend_challenges(self, user_id: int, user_challenges: List[Dict[str, Any]], 
                           n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Kullanıcıya meydan okuma önerileri yapar."""
        if self.user_similarities is None or self.challenge_matrix is None:
            raise ValueError("Önce load_data() metodunu çağırın")
        
        # Kullanıcının tamamladığı meydan okumaları
        completed_challenges = {c['challenge_id'] for c in user_challenges if c['completed']}
        
        # Benzer kullanıcıları bul
        similar_users = self.get_similar_users(user_id)
        
        # Benzer kullanıcıların tamamladığı meydan okumaları
        similar_user_challenges = []
        for similar_user_id in similar_users:
            # Burada benzer kullanıcıların meydan okuma verilerini almalıyız
            # Şimdilik örnek veri kullanıyoruz
            pass
        
        # Meydan okuma skorlarını hesapla
        challenge_scores = {}
        for challenge_id, challenge_features in enumerate(self.challenge_matrix):
            if challenge_id not in completed_challenges:
                # Benzer kullanıcıların bu meydan okumayı tamamlama oranı
                completion_rate = sum(1 for c in similar_user_challenges 
                                   if c['challenge_id'] == challenge_id) / len(similar_users)
                
                # Kullanıcı-benzerlik ağırlıklı skor
                score = completion_rate * np.mean(self.user_similarities[user_id, similar_users])
                
                challenge_scores[challenge_id] = score
        
        # En yüksek skorlu meydan okumaları öner
        recommended_challenges = sorted(challenge_scores.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:n_recommendations]
        
        return [{'challenge_id': cid, 'score': score} 
                for cid, score in recommended_challenges]
    
    def get_challenge_recommendations(self, user_data: Dict[str, Any], 
                                    n_recommendations: int = 5) -> List[Dict[str, Any]]:
        """Kullanıcı verilerine göre meydan okuma önerileri yapar."""
        # Kullanıcı verilerini DataFrame'e dönüştür
        user_df = pd.DataFrame([user_data])
        
        # Kullanıcı verilerini işle
        user_features = self._preprocess_user_data(user_df)
        
        # Tüm kullanıcılarla benzerlik hesapla
        similarities = cosine_similarity(user_features, self.user_matrix)[0]
        
        # En benzer kullanıcıları bul
        similar_users = np.argsort(similarities)[::-1][:5]
        
        # Benzer kullanıcıların tamamladığı meydan okumaları
        similar_user_challenges = []
        for similar_user_id in similar_users:
            # Burada benzer kullanıcıların meydan okuma verilerini almalıyız
            # Şimdilik örnek veri kullanıyoruz
            pass
        
        # Meydan okuma skorlarını hesapla
        challenge_scores = {}
        for challenge_id, challenge_features in enumerate(self.challenge_matrix):
            # Benzer kullanıcıların bu meydan okumayı tamamlama oranı
            completion_rate = sum(1 for c in similar_user_challenges 
                               if c['challenge_id'] == challenge_id) / len(similar_users)
            
            # Kullanıcı-benzerlik ağırlıklı skor
            score = completion_rate * np.mean(similarities[similar_users])
            
            challenge_scores[challenge_id] = score
        
        # En yüksek skorlu meydan okumaları öner
        recommended_challenges = sorted(challenge_scores.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)[:n_recommendations]
        
        return [{'challenge_id': cid, 'score': score} 
                for cid, score in recommended_challenges] 