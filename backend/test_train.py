import requests
import json
from test_data import generate_test_data

# API endpoint
BASE_URL = "http://127.0.0.1:8080"  # Doğru adres!

def add_user_to_firestore(user):
    response = requests.post(
        f"{BASE_URL}/api/user-data",
        json=user["features"]
    )
    print("User added to Firestore:", response.json())

def train_models(test_data):
    # Print some statistics
    footprints = [data["carbon_footprint"] for data in test_data]
    print(f"\nTest Data Statistics:")
    print(f"Number of samples: {len(test_data)}")
    print(f"Average footprint: {sum(footprints) / len(footprints):.2f}")
    print(f"Min footprint: {min(footprints):.2f}")
    print(f"Max footprint: {max(footprints):.2f}")
    
    # Train models
    print("\nTraining ML models...")
    try:
        response = requests.post(
            f"{BASE_URL}/train-models",
            json=test_data
        )
        response.raise_for_status()
        print("Training successful!")
        print("Response:", response.json())
        # Collaborative filtering güncellemesi için ek istek
        response_cf = requests.post(
            f"{BASE_URL}/train-models",
            json=test_data
        )
        response_cf.raise_for_status()
        print("Collaborative filtering updated!")
    except requests.exceptions.RequestException as e:
        print(f"Error training models: {str(e)}")

def test_recommendations():
    # Test recommendations for a sample user
    print("\nTesting recommendations...")
    try:
        response = requests.get(
            f"{BASE_URL}/user-recommendations/user_0"
        )
        response.raise_for_status()
        print("Recommendations:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error getting recommendations: {str(e)}")

def test_similar_users():
    # Test similar users for a sample user
    print("\nTesting similar users...")
    try:
        response = requests.get(
            f"{BASE_URL}/similar-users/user_0"
        )
        response.raise_for_status()
        print("Similar users:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error getting similar users: {str(e)}")

if __name__ == "__main__":
    print("Starting ML model training and testing...")
    test_data = generate_test_data(100)
    train_models(test_data)  # Önce modeli eğit ve collaborative filtering'i güncelle
    # Daha fazla kullanıcı ekle
    for i in range(20):
        add_user_to_firestore(test_data[i])
    test_recommendations()
    test_similar_users()
    print("\nTesting completed!") 