import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class DataLoader:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent.parent / 'data' / 'Carbon Emission.csv'
        self.data = None
        self.X = None
        self.y = None
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.load_data()
        self.preprocess_data()
    
    def load_data(self):
        """CSV dosyasını yükler ve DataFrame'e dönüştürür."""
        try:
            self.data = pd.read_csv(self.data_path)
            print("Veri seti başarıyla yüklendi.")
            print("\nVeri seti boyutu:", self.data.shape)
            print("\nSütunlar:", self.data.columns.tolist())
            print("\nVeri seti özeti:")
            print(self.data.describe())
            print("\nEksik değerler:")
            print(self.data.isnull().sum())
        except Exception as e:
            print(f"Veri seti yüklenirken hata oluştu: {str(e)}")
    
    def preprocess_data(self):
        """Veriyi ön işler ve model için hazırlar."""
        try:
            # Hedef değişkeni ayır
            self.y = self.data['CarbonEmission']
            
            # Kategorik değişkenleri sayısallaştır
            categorical_columns = [
                'Body Type', 'Sex', 'Diet', 'How Often Shower',
                'Heating Energy Source', 'Transport', 'Vehicle Type',
                'Social Activity', 'Waste Bag Size', 'Energy efficiency',
                'Recycling'
            ]
            
            # Cooking_With sütununu işle (liste formatında)
            self.data['Cooking_With'] = self.data['Cooking_With'].apply(eval)
            cooking_methods = set()
            for methods in self.data['Cooking_With']:
                cooking_methods.update(methods)
            
            # Her pişirme yöntemi için binary sütun oluştur
            for method in cooking_methods:
                self.data[f'Cooking_{method}'] = self.data['Cooking_With'].apply(
                    lambda x: 1 if method in x else 0
                )
            
            # Kategorik değişkenleri dönüştür
            for column in categorical_columns:
                le = LabelEncoder()
                self.data[column] = le.fit_transform(self.data[column])
                self.label_encoders[column] = le
            
            # Sayısal değişkenleri ölçeklendir
            numerical_columns = [
                'Monthly Grocery Bill', 'Vehicle Monthly Distance Km',
                'Waste Bag Weekly Count', 'How Long TV PC Daily Hour',
                'How Many New Clothes Monthly', 'How Long Internet Daily Hour'
            ]
            
            self.data[numerical_columns] = self.scaler.fit_transform(self.data[numerical_columns])
            
            # Model için özellik matrisini oluştur
            feature_columns = categorical_columns + numerical_columns + [f'Cooking_{method}' for method in cooking_methods]
            self.X = self.data[feature_columns]
            
            print("\nVeri ön işleme tamamlandı.")
            print("Özellik sayısı:", len(feature_columns))
            
        except Exception as e:
            print(f"Veri ön işleme sırasında hata oluştu: {str(e)}")
    
    def train_model(self):
        """Karbon emisyonu tahmin modelini eğitir."""
        try:
            # Veriyi eğitim ve test setlerine ayır
            X_train, X_test, y_train, y_test = train_test_split(
                self.X, self.y, test_size=0.2, random_state=42
            )
            
            # Random Forest modelini eğit
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Model performansını değerlendir
            train_score = self.model.score(X_train, y_train)
            test_score = self.model.score(X_test, y_test)
            
            print("\nModel eğitimi tamamlandı.")
            print(f"Eğitim seti R2 skoru: {train_score:.3f}")
            print(f"Test seti R2 skoru: {test_score:.3f}")
            
            # Özellik önemliliklerini göster
            feature_importance = pd.DataFrame({
                'feature': self.X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nEn önemli 10 özellik:")
            print(feature_importance.head(10))
            
            # Modeli kaydet
            model_dir = Path(__file__).parent.parent.parent / 'models'
            model_dir.mkdir(exist_ok=True)
            
            joblib.dump(self.model, model_dir / 'carbon_emission_model.joblib')
            joblib.dump(self.label_encoders, model_dir / 'label_encoders.joblib')
            joblib.dump(self.scaler, model_dir / 'scaler.joblib')
            
            print("\nModel ve dönüştürücüler kaydedildi.")
            
        except Exception as e:
            print(f"Model eğitimi sırasında hata oluştu: {str(e)}")
    
    def get_data(self):
        """Yüklenen veri setini döndürür."""
        return self.data
    
    def get_feature_importance(self):
        """Özellik önemliliklerini döndürür."""
        if self.model is None:
            self.train_model()
        
        return pd.DataFrame({
            'feature': self.X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
    
    def predict_emission(self, user_data):
        """Kullanıcı verilerine göre karbon emisyonunu tahmin eder."""
        if self.model is None:
            self.train_model()
        
        # Kullanıcı verilerini dönüştür
        processed_data = {}
        
        # Kategorik değişkenleri dönüştür
        for column, encoder in self.label_encoders.items():
            if column in user_data:
                processed_data[column] = encoder.transform([user_data[column]])[0]
        
        # Sayısal değişkenleri ölçeklendir
        numerical_columns = [
            'Monthly Grocery Bill', 'Vehicle Monthly Distance Km',
            'Waste Bag Weekly Count', 'How Long TV PC Daily Hour',
            'How Many New Clothes Monthly', 'How Long Internet Daily Hour'
        ]
        
        for column in numerical_columns:
            if column in user_data:
                processed_data[column] = self.scaler.transform([[user_data[column]]])[0][0]
        
        # Pişirme yöntemlerini işle
        cooking_methods = [col for col in self.X.columns if col.startswith('Cooking_')]
        user_cooking = user_data.get('Cooking_With', [])
        
        for method in cooking_methods:
            method_name = method.replace('Cooking_', '')
            processed_data[method] = 1 if method_name in user_cooking else 0
        
        # Tahmin için veriyi hazırla
        X_pred = pd.DataFrame([processed_data])
        
        # Eksik sütunları 0 ile doldur
        for col in self.X.columns:
            if col not in X_pred.columns:
                X_pred[col] = 0
        
        # Sütunları doğru sıraya koy
        X_pred = X_pred[self.X.columns]
        
        # Tahmin yap
        prediction = self.model.predict(X_pred)[0]
        
        return {
            'predicted_emission': prediction,
            'feature_importance': self.get_feature_importance().to_dict('records')
        }

if __name__ == "__main__":
    # Test amaçlı veri setini yükle ve modeli eğit
    loader = DataLoader()
    loader.train_model()
    
    # Veri setindeki mevcut değerleri al
    data = loader.get_data()
    unique_values = {
        'Body Type': data['Body Type'].unique(),
        'Sex': data['Sex'].unique(),
        'Diet': data['Diet'].unique(),
        'How Often Shower': data['How Often Shower'].unique(),
        'Heating Energy Source': data['Heating Energy Source'].unique(),
        'Transport': data['Transport'].unique(),
        'Vehicle Type': data['Vehicle Type'].unique(),
        'Social Activity': data['Social Activity'].unique(),
        'Energy efficiency': data['Energy efficiency'].unique(),
        'Recycling': data['Recycling'].unique()
    }
    
    print("\nVeri setindeki mevcut değerler:")
    for column, values in unique_values.items():
        print(f"\n{column}:")
        print(values)
    
    # Örnek tahmin için veri setindeki ilk kullanıcıyı kullan
    test_user = data.iloc[0].to_dict()
    test_user['Cooking_With'] = eval(test_user['Cooking_With'])  # String'i listeye çevir
    
    print("\nTest kullanıcısı verileri:")
    for key, value in test_user.items():
        print(f"{key}: {value}")
    
    prediction = loader.predict_emission(test_user)
    print("\nTest kullanıcısı için tahmin:")
    print(f"Tahmini karbon emisyonu: {prediction['predicted_emission']:.2f}")
    print(f"Gerçek karbon emisyonu: {test_user['CarbonEmission']:.2f}")
    
    # Özellik önemliliklerini göster
    print("\nÖzellik önemlilikleri:")
    feature_importance = pd.DataFrame(prediction['feature_importance'])
    print(feature_importance.head(10)) 