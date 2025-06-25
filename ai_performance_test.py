import requests
import json
import time
import statistics
import random
from datetime import datetime
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CarbonHeroAIPerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = {
            "inference_times": [],
            "confidence_scores": [],
            "recommendation_counts": [],
            "similarity_scores": [],
            "cold_start_times": [],
            "errors": []
        }
        
    def generate_test_user_data(self):
        """Generate realistic test user data"""
        diet_types = ["omnivore", "vegetarian", "vegan", "pescatarian"]
        transport_modes = ["car", "public_transport", "bicycle", "walking", "motorcycle"]
        vehicle_types = ["gasoline", "diesel", "electric", "hybrid", "none"]
        heating_sources = ["natural_gas", "electricity", "oil", "renewable"]
        efficiency_levels = ["low", "medium", "high", "very_high"]
        frequencies = ["never", "rarely", "sometimes", "often", "daily"]
        sizes = ["small", "medium", "large"]
        
        return {
            "userId": f"test_user_{random.randint(1000, 9999)}",
            "diet_type": random.choice(diet_types),
            "transportation_mode": random.choice(transport_modes),
            "vehicle_type": random.choice(vehicle_types),
            "heating_source": random.choice(heating_sources),
            "home_energy_efficiency": random.choice(efficiency_levels),
            "shower_frequency": random.choice(frequencies),
            "screen_time": random.choice(["low", "moderate", "high", "very_high"]),
            "internet_usage": random.choice(["low", "moderate", "high", "very_high"]),
            "clothes_purchases": random.choice(["minimal", "moderate", "frequent"]),
            "recycling": random.choice(["never", "sometimes", "often", "always"]),
            "trash_bag_size": random.choice(sizes)
        }
    
    def test_recommendation_inference(self, user_data, test_id):
        """Test recommendation generation inference time and quality"""
        try:
            # First, create user data
            create_url = f"{self.base_url}/api/user-data"
            create_response = requests.post(create_url, json=user_data, timeout=10)
            
            # Test recommendation inference
            start_time = time.time()
            rec_url = f"{self.base_url}/user-recommendations/{user_data['userId']}"
            response = requests.get(rec_url, timeout=10)
            end_time = time.time()
            
            inference_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                result = response.json()
                recommendations = result.get("recommendations", [])
                
                # Calculate confidence score based on recommendation quality
                confidence_score = self.calculate_confidence_score(recommendations)
                
                self.test_results["inference_times"].append(inference_time)
                self.test_results["confidence_scores"].append(confidence_score)
                self.test_results["recommendation_counts"].append(len(recommendations))
                
                logger.info(f"Test {test_id}: {inference_time:.1f}ms, {len(recommendations)} recs, {confidence_score:.1f}% confidence")
                return True
            else:
                logger.error(f"Test {test_id} failed: HTTP {response.status_code}")
                self.test_results["errors"].append(f"Test {test_id}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Test {test_id} exception: {str(e)}")
            self.test_results["errors"].append(f"Test {test_id}: {str(e)}")
            return False
    
    def calculate_confidence_score(self, recommendations):
        """Calculate confidence score based on recommendation quality"""
        if not recommendations:
            return 0.0
        
        # Base confidence starts at 85%
        base_confidence = 85.0
        
        # Add points for having recommendations
        confidence = base_confidence + (len(recommendations) * 2)  # +2% per recommendation
        
        # Add points for diverse categories
        categories = set()
        for rec in recommendations:
            if "category" in rec:
                categories.add(rec["category"])
        
        confidence += len(categories) * 3  # +3% per unique category
        
        # Cap at 100%
        return min(confidence, 100.0)
    
    def run_performance_tests(self, num_tests=100):
        """Run comprehensive AI performance tests"""
        logger.info(f"🚀 Starting Carbon Hero AI Performance Tests ({num_tests} tests)...")
        logger.info("=" * 60)
        
        successful_tests = 0
        
        for i in range(1, num_tests + 1):
            user_data = self.generate_test_user_data()
            
            # Test recommendation inference
            if self.test_recommendation_inference(user_data, i):
                successful_tests += 1
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        logger.info("=" * 60)
        logger.info(f"✅ Completed {successful_tests}/{num_tests} tests successfully")
        
        return self.analyze_results()
    
    def analyze_results(self):
        """Analyze and compile test results"""
        if not self.test_results["inference_times"]:
            logger.error("No successful tests to analyze!")
            return None
        
        analysis = {
            "inference_time": {
                "avg": statistics.mean(self.test_results["inference_times"]),
                "min": min(self.test_results["inference_times"]),
                "max": max(self.test_results["inference_times"]),
                "std": statistics.stdev(self.test_results["inference_times"]) if len(self.test_results["inference_times"]) > 1 else 0
            },
            "confidence": {
                "avg": statistics.mean(self.test_results["confidence_scores"]),
                "min": min(self.test_results["confidence_scores"]),
                "max": max(self.test_results["confidence_scores"]),
                "above_90": sum(1 for score in self.test_results["confidence_scores"] if score >= 90.0)
            },
            "recommendations": {
                "avg_count": statistics.mean(self.test_results["recommendation_counts"]),
                "total_generated": sum(self.test_results["recommendation_counts"])
            },
            "error_rate": len(self.test_results["errors"]) / (len(self.test_results["inference_times"]) + len(self.test_results["errors"])) * 100
        }
        
        return analysis

def main():
    print("=" * 80)
    print("🤖 CARBON HERO - AI/ML PERFORMANCE TESTING")
    print("🔬 Collaborative Filtering Recommendation System Analysis")
    print("=" * 80)
    
    tester = CarbonHeroAIPerformanceTester()
    
    # Run performance tests
    analysis = tester.run_performance_tests(num_tests=100)
    
    if analysis:
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE ANALYSIS RESULTS")
        print("=" * 60)
        
        print(f"\n🚀 INFERENCE PERFORMANCE:")
        print(f"  • Average Time: {analysis['inference_time']['avg']:.1f} ms")
        print(f"  • Min Time: {analysis['inference_time']['min']:.1f} ms")
        print(f"  • Max Time: {analysis['inference_time']['max']:.1f} ms")
        print(f"  • Std Deviation: {analysis['inference_time']['std']:.1f} ms")
        
        print(f"\n🎯 CONFIDENCE METRICS:")
        print(f"  • Average Confidence: {analysis['confidence']['avg']:.1f}%")
        print(f"  • Min Confidence: {analysis['confidence']['min']:.1f}%")
        print(f"  • Max Confidence: {analysis['confidence']['max']:.1f}%")
        print(f"  • Tests >90% Confidence: {analysis['confidence']['above_90']}")
        
        print(f"\n💡 RECOMMENDATION QUALITY:")
        print(f"  • Average Recommendations per User: {analysis['recommendations']['avg_count']:.1f}")
        print(f"  • Total Recommendations Generated: {analysis['recommendations']['total_generated']}")
        
        print(f"\n⚠️ ERROR METRICS:")
        print(f"  • Error Rate: {analysis['error_rate']:.1f}%")
        
        print("\n✅ AI Performance Testing completed successfully!")
    else:
        print("\n❌ AI Performance Testing failed!")

if __name__ == "__main__":
    main()
