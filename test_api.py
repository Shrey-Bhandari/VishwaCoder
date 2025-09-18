#!/usr/bin/env python3
"""
Test script for AI Leaf Health Assessment API
Run this to test your backend functionality
"""
import requests
import json
import os
import time
from PIL import Image
import numpy as np

# Configuration
API_BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = "test_leaf.jpg"

def create_test_image():
    """Create a test leaf image for testing"""
    if not os.path.exists(TEST_IMAGE_PATH):
        # Create a simple test image (green rectangle simulating a leaf)
        img = Image.new('RGB', (224, 224), color='green')
        
        # Add some brown spots to simulate disease
        pixels = img.load()
        for i in range(50, 100):
            for j in range(50, 100):
                pixels[i, j] = (139, 69, 19)  # Brown color
        
        img.save(TEST_IMAGE_PATH)
        print(f"Created test image: {TEST_IMAGE_PATH}")
    return TEST_IMAGE_PATH

def test_health_check():
    """Test the health check endpoint"""
    print("\n1. Testing Health Check Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Models loaded: {data.get('models_loaded')}")
            print(f"   Total models: {data.get('total_models')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_models_endpoint():
    """Test the models listing endpoint"""
    print("\n2. Testing Models Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/models")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print("✅ Models endpoint working")
            print(f"   Available models: {len(models)}")
            
            for model in models:
                status = "✅" if model['available'] else "⚠️"
                print(f"   {status} {model['name']} ({model['classes_count']} classes)")
            return models
        else:
            print(f"❌ Models endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Models endpoint error: {str(e)}")
        return []

def test_analyze_endpoint(available_models):
    """Test the leaf analysis endpoint"""
    print("\n3. Testing Analyze Endpoint...")
    
    # Create test image
    test_image = create_test_image()
    
    # Test with each available model
    for model in available_models:
        if not model['available']:
            print(f"⚠️  Skipping {model['name']} - not loaded")
            continue
        
        print(f"\n   Testing with {model['name']}...")
        
        try:
            with open(test_image, 'rb') as f:
                files = {'image': f}
                data = {'model': model['id']}
                
                response = requests.post(
                    f"{API_BASE_URL}/api/analyze-leaf",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Analysis successful")
                print(f"      Health Status: {result.get('healthStatus')}")
                print(f"      Damage: {result.get('damagePercentage')}%")
                print(f"      Severity: {result.get('severityLevel')}")
                print(f"      LAI: {result.get('leafAreaIndex')}")
                print(f"      Disease: {result.get('detectedDisease', 'None')}")
                print(f"      Confidence: {result.get('confidence')}%")
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                if response.content:
                    try:
                        error = response.json()
                        print(f"      Error: {error.get('error')}")
                    except:
                        print(f"      Raw error: {response.text[:200]}")
        
        except Exception as e:
            print(f"   ❌ Analysis error: {str(e)}")
        
        time.sleep(1)  # Small delay between requests

def test_error_handling():
    """Test error handling"""
    print("\n4. Testing Error Handling...")
    
    # Test without image
    try:
        response = requests.post(f"{API_BASE_URL}/api/analyze-leaf", data={'model': 'model1'})
        if response.status_code == 400:
            print("   ✅ Correctly handles missing image")
        else:
            print(f"   ⚠️  Unexpected response for missing image: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing missing image: {str(e)}")
    
    # Test with invalid model
    test_image = create_test_image()
    try:
        with open(test_image, 'rb') as f:
            files = {'image': f}
            data = {'model': 'invalid_model'}
            
            response = requests.post(
                f"{API_BASE_URL}/api/analyze-leaf",
                files=files,
                data=data
            )
        
        if response.status_code == 400:
            print("   ✅ Correctly handles invalid model")
        else:
            print(f"   ⚠️  Unexpected response for invalid model: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid model: {str(e)}")

def test_cors():
    """Test CORS headers"""
    print("\n5. Testing CORS Headers...")
    try:
        response = requests.options(f"{API_BASE_URL}/api/health")
        if 'Access-Control-Allow-Origin' in response.headers:
            print("   ✅ CORS headers present")
        else:
            print("   ⚠️  CORS headers might not be configured")
    except Exception as e:
        print(f"   ❌ CORS test error: {str(e)}")

def main():
    """Main test function"""
    print("🧪 AI Leaf Health Assessment API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(API_BASE_URL, timeout=5)
        print(f"✅ Server is running at {API_BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {API_BASE_URL}")
        print("   Make sure the server is running with: python app.py")
        return
    except Exception as e:
        print(f"❌ Server connection error: {str(e)}")
        return
    
    # Run tests
    health_ok = test_health_check()
    
    if health_ok:
        available_models = test_models_endpoint()
        test_analyze_endpoint(available_models)
        test_error_handling()
        test_cors()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    
    # Cleanup
    if os.path.exists(TEST_IMAGE_PATH):
        os.remove(TEST_IMAGE_PATH)
        print(f"Cleaned up test image: {TEST_IMAGE_PATH}")

if __name__ == '__main__':
    main()