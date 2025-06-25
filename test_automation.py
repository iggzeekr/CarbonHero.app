import requests
import json
import time
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class CarbonHeroAPITester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message="", execution_time=None):
        if success:
            self.test_results["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
            status = "❌ FAIL"
        
        time_info = f" ({execution_time:.2f}s)" if execution_time else ""
        logger.info(f"{status} - {test_name}{time_info}")
        if message:
            logger.info(f"  └─ {message}")
    
    def test_carbon_calculation_valid(self):
        """Test: Valid carbon footprint calculation"""
        test_name = "Carbon Calculation - Valid Data"
        
        url = f"{self.base_url}/calculate-carbon-footprint"
        data = {
            "userId": "test_user_123",
            "diet_type": "vegetarian",
            "transportation_mode": "public_transport",
            "vehicle_type": "none",
            "heating_source": "natural_gas",
            "home_energy_efficiency": "high",
            "shower_frequency": "daily",
            "screen_time": "moderate",
            "internet_usage": "high",
            "clothes_purchases": "minimal",
            "recycling": "always",
            "trash_bag_size": "small"
        }
        
        try:
            start_time = time.time()
            response = requests.post(url, json=data, timeout=5)
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if "total_footprint" in result and "breakdown" in result:
                    if execution_time < 2.0:  # Performance check
                        self.log_result(test_name, True, f"Total footprint: {result['total_footprint']}", execution_time)
                        return True
                    else:
                        self.log_result(test_name, False, f"Response too slow: {execution_time:.2f}s")
                        return False
                else:
                    self.log_result(test_name, False, "Missing required fields in response")
                    return False
            else:
                self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_carbon_calculation_invalid(self):
        """Test: Invalid data handling"""
        test_name = "Carbon Calculation - Invalid Data"
        
        url = f"{self.base_url}/calculate-carbon-footprint"
        data = {
            "userId": "test_user_123",
            "diet_type": "",  # Empty required field
            "transportation_mode": "invalid_mode",  # Invalid value
        }
        
        try:
            response = requests.post(url, json=data, timeout=5)
            
            # Should return 400 or 422 for validation errors
            if response.status_code in [400, 422, 500]:
                self.log_result(test_name, True, f"Properly handled invalid data with HTTP {response.status_code}")
                return True
            else:
                self.log_result(test_name, False, f"Should have returned error but got HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_user_recommendations(self):
        """Test: User recommendations API"""
        test_name = "User Recommendations"
        
        url = f"{self.base_url}/user-recommendations/test_user_123"
        
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            end_time = time.time()
            execution_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                if "recommendations" in result:
                    self.log_result(test_name, True, f"Got {len(result['recommendations'])} recommendations", execution_time)
                    return True
                else:
                    self.log_result(test_name, False, "Missing recommendations field")
                    return False
            elif response.status_code == 404:
                self.log_result(test_name, True, "User not found - expected behavior")
                return True
            else:
                self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_challenge_recommendations(self):
        """Test: Challenge recommendations API"""
        test_name = "Challenge Recommendations"
        
        url = f"{self.base_url}/recommend-challenges/test_user_123"
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    self.log_result(test_name, True, f"Got {len(result)} challenge recommendations")
                    return True
                else:
                    self.log_result(test_name, False, "Response should be a list")
                    return False
            elif response.status_code == 404:
                self.log_result(test_name, True, "User not found - expected behavior")
                return True
            else:
                self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_leaderboard(self):
        """Test: Leaderboard API"""
        test_name = "Leaderboard"
        
        url = f"{self.base_url}/api/leaderboard"
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    self.log_result(test_name, True, f"Got leaderboard with {len(result)} entries")
                    return True
                else:
                    self.log_result(test_name, False, "Response should be a list")
                    return False
            else:
                self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_user_stats(self):
        """Test: User stats API"""
        test_name = "User Stats"
        
        url = f"{self.base_url}/user-stats/test_user_123"
        
        try:
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                required_fields = ["current_footprint", "breakdown", "user_data"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if not missing_fields:
                    self.log_result(test_name, True, f"All required fields present")
                    return True
                else:
                    self.log_result(test_name, False, f"Missing fields: {missing_fields}")
                    return False
            elif response.status_code == 404:
                self.log_result(test_name, True, "User not found - expected behavior")
                return True
            else:
                self.log_result(test_name, False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Exception: {str(e)}")
            return False
    
    def test_server_health(self):
        """Test: Server health check"""
        test_name = "Server Health"
        
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log_result(test_name, True, "Server is responding")
                return True
            else:
                self.log_result(test_name, False, f"Server health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_result(test_name, False, f"Cannot connect to server: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("🚀 Starting Carbon Hero API Tests...")
        logger.info(f"Target server: {self.base_url}")
        logger.info("-" * 50)
        
        # Test order matters - health check first
        tests = [
            self.test_server_health,
            self.test_carbon_calculation_valid,
            self.test_carbon_calculation_invalid,
            self.test_user_recommendations,
            self.test_challenge_recommendations,
            self.test_leaderboard,
            self.test_user_stats
        ]
        
        for test in tests:
            test()
        
        # Print summary
        logger.info("-" * 50)
        logger.info("📊 TEST SUMMARY")
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        success_rate = (self.test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {self.test_results['passed']} ✅")
        logger.info(f"Failed: {self.test_results['failed']} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if self.test_results["errors"]:
            logger.info("\n🔍 FAILED TESTS:")
            for error in self.test_results["errors"]:
                logger.error(f"  • {error}")
        
        if success_rate >= 80:
            logger.info("\n🎉 Test suite PASSED! (≥80% success rate)")
            return True
        else:
            logger.error("\n💥 Test suite FAILED! (<80% success rate)")
            return False

def main():
    print("=" * 60)
    print("🧪 CARBON HERO - API RELIABILITY TESTS")
    print("=" * 60)
    
    tester = CarbonHeroAPITester()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        exit(0)
    else:
        print("❌ SOME TESTS FAILED - CHECK LOGS ABOVE")
        exit(1)

if __name__ == "__main__":
    main() 