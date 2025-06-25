import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

class CarbonFootprintModel:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'carbon_model.joblib')
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Modeli yükle veya yoksa eğit"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                print("Model başarıyla yüklendi.")
            else:
                print("Model bulunamadı, yeni model eğitilecek...")
                self._train_model()
        except Exception as e:
            print(f"Model yüklenirken hata oluştu: {str(e)}")
            print("Yeni model eğitilecek...")
            self._train_model()

    def _train_model(self):
        """Yeni model eğit"""
        try:
            # Veri setini yükle
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Carbon Emission.csv')
            df = pd.read_csv(data_path)

            # Kategorik değişkenleri otomatik olarak bul ve sayısallaştır
            categorical_columns = df.select_dtypes(include=['object']).columns.tolist()
            for column in categorical_columns:
                self.label_encoders[column] = LabelEncoder()
                df[column] = self.label_encoders[column].fit_transform(df[column].astype(str))

            # Özellikler ve hedef değişken
            X = df.drop(['CarbonEmission'], axis=1, errors='ignore')
            y = df['CarbonEmission']

            # Veriyi ölçeklendir
            X = self.scaler.fit_transform(X)

            # Model eğitimi
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X, y)

            # Modeli kaydet
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            print("Model başarıyla eğitildi ve kaydedildi.")

        except Exception as e:
            print(f"Model eğitilirken hata oluştu: {str(e)}")
            raise

    def predict(self, user_data):
        """Kullanıcı verilerine göre karbon ayak izini tahmin et"""
        try:
            # Kategorik değişkenleri dönüştür
            for column, encoder in self.label_encoders.items():
                if column in user_data:
                    user_data[column] = encoder.transform([str(user_data[column])])[0]

            # Veriyi ölçeklendir
            X = self.scaler.transform([list(user_data.values())])

            # Tahmin yap
            prediction = self.model.predict(X)[0]
            return float(prediction)

        except Exception as e:
            print(f"Tahmin yapılırken hata oluştu: {str(e)}")
            raise

    def get_feature_importance(self):
        """Özellik önemlerini döndür"""
        if self.model is None:
            return None
        
        feature_names = list(self.label_encoders.keys())
        importances = self.model.feature_importances_
        
        # Özellik önemlerini sırala
        feature_importance = dict(zip(feature_names, importances))
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)) 