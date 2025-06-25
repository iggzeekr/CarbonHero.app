from typing import List, Dict
import random

def generate_test_data(n=100):
    data = []
    for i in range(n):
        features = {
            "userId": f"user_{i}",
            "diet_type": random.choice(["Omnivore", "Vegetarian", "Vegan"]),
            "transportation_mode": random.choice(["Car", "Public Transport", "Bike", "Walk"]),
            "vehicle_type": random.choice(["Petrol", "Diesel", "Electric", "Hybrid", "None"]),
            "heating_source": random.choice(["Natural Gas", "Electric", "Coal", "None"]),
            "home_energy_efficiency": random.choice(["Low", "Medium", "High"]),
            "shower_frequency": random.choice(["Daily", "Every Other Day", "Weekly"]),
            "screen_time": random.choice(["Less than 2 hours", "2-4 hours", "4-8 hours", "8+ hours"]),
            "internet_usage": random.choice(["Less than 4 hours", "4-8 hours", "8-16 hours", "More than 16 hours"]),
            "clothes_purchases": random.choice(["0-10", "11-20", "21-30", "31+"]),
            "recycling": random.choice(["Always", "Sometimes", "Never"]),
            "trash_bag_size": random.choice(["Small", "Medium", "Large"])
        }
        carbon_footprint = round(random.uniform(5, 25), 2)
        data.append({
            "userId": features["userId"],
            "carbon_footprint": carbon_footprint,
            "features": features
        })
    return data

def calculate_carbon_footprint(user_data: Dict) -> float:
    """Calculate a realistic carbon footprint based on user data"""
    footprint = 0.0
    
    # Diet impact
    diet_scores = {
        "Vegan": 1.5,
        "Vegetarian": 2.0,
        "Pescatarian": 2.5,
        "Omnivore": 3.0
    }
    footprint += diet_scores.get(user_data["diet_type"], 2.5)
    
    # Transportation impact
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
    footprint += transport_scores.get(user_data["transportation_mode"], 2.0)
    footprint += vehicle_scores.get(user_data["vehicle_type"], 1.5)
    
    # Housing impact
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
    footprint += heating_scores.get(user_data["heating_source"], 2.0)
    footprint *= efficiency_scores.get(user_data["home_energy_efficiency"], 1.5)
    
    # Lifestyle impact
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
    
    lifestyle_score = (
        shower_scores.get(user_data["shower_frequency"], 1.0) +
        screen_scores.get(user_data["screen_time"], 1.0) +
        internet_scores.get(user_data["internet_usage"], 1.0) +
        clothes_scores.get(user_data["clothes_purchases"], 1.0)
    ) / 4
    
    footprint += lifestyle_score
    
    # Waste impact
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
    
    waste_score = (
        recycling_scores.get(user_data["recycling"], 1.5) *
        trash_scores.get(user_data["trash_bag_size"], 1.0)
    )
    
    footprint += waste_score
    
    # Add some random variation (±20%)
    variation = random.uniform(0.8, 1.2)
    footprint *= variation
    
    return round(footprint, 2)

if __name__ == "__main__":
    # Generate 100 test samples
    test_data = generate_test_data(100)
    
    # Print first sample as example
    print("Example test data:")
    print(test_data[0])
    
    # Print statistics
    footprints = [data["carbon_footprint"] for data in test_data]
    print(f"\nStatistics:")
    print(f"Number of samples: {len(test_data)}")
    print(f"Average footprint: {sum(footprints) / len(footprints):.2f}")
    print(f"Min footprint: {min(footprints):.2f}")
    print(f"Max footprint: {max(footprints):.2f}") 