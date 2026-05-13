#!/usr/bin/env python3
"""
Test script for the Customer Review Classification API
Run this after starting the Docker container to verify everything works
"""

import requests
import json
import sys
from typing import Dict, Any

API_BASE = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health_check() -> bool:
    """Test the health check endpoint"""
    print_section("Testing Health Check")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("model_loaded"):
            print("✅ Health check passed - Model is loaded")
            return True
        else:
            print("❌ Health check failed - Model not loaded")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_get_labels() -> bool:
    """Test the labels endpoint"""
    print_section("Testing Get Labels")
    try:
        response = requests.get(f"{API_BASE}/labels", timeout=5)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Labels: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and "labels" in data:
            print("✅ Labels endpoint working")
            return True
        else:
            print("❌ Labels endpoint failed")
            return False
    except Exception as e:
        print(f"❌ Labels endpoint failed: {str(e)}")
        return False

def test_single_classification() -> bool:
    """Test single review classification"""
    print_section("Testing Single Classification")
    
    test_cases = [
        "Great service, thank you!",
        "My device won't turn on",
        "I want my money back immediately",
        "How do I cancel my subscription?",
        "The product is broken",
        "What are your business hours?"
    ]
    
    all_passed = True
    for text in test_cases:
        try:
            response = requests.post(
                f"{API_BASE}/classify",
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n📝 Review: \"{text}\"")
                print(f"   Label: {data['label']} (ID: {data['label_id']})")
                print(f"   Confidence: {data['confidence']:.2%}")
                print("   ✅ Success")
            else:
                print(f"\n❌ Failed for: \"{text}\"")
                print(f"   Status: {response.status_code}")
                print(f"   Error: {response.text}")
                all_passed = False
                
        except Exception as e:
            print(f"\n❌ Error for: \"{text}\"")
            print(f"   {str(e)}")
            all_passed = False
    
    return all_passed

def test_batch_classification() -> bool:
    """Test batch review classification"""
    print_section("Testing Batch Classification")
    
    reviews = [
        "Great service, thank you!",
        "My device won't turn on",
        "I want my money back immediately"
    ]
    
    try:
        response = requests.post(
            f"{API_BASE}/classify/batch",
            json={"reviews": reviews},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Processed: {data['total_processed']}")
            print("\nResults:")
            
            for i, result in enumerate(data['results'], 1):
                print(f"\n{i}. \"{result['text']}\"")
                print(f"   Label: {result['label']} (ID: {result['label_id']})")
                print(f"   Confidence: {result['confidence']:.2%}")
            
            print("\n✅ Batch classification successful")
            return True
        else:
            print(f"❌ Batch classification failed")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Batch classification error: {str(e)}")
        return False

def test_error_handling() -> bool:
    """Test error handling"""
    print_section("Testing Error Handling")
    
    all_passed = True
    
    # Test empty text
    print("\n1. Testing empty text...")
    try:
        response = requests.post(
            f"{API_BASE}/classify",
            json={"text": ""},
            timeout=5
        )
        if response.status_code == 422:
            print("   ✅ Correctly rejected empty text")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        all_passed = False
    
    # Test too many reviews in batch
    print("\n2. Testing batch size limit...")
    try:
        large_batch = ["test review"] * 101
        response = requests.post(
            f"{API_BASE}/classify/batch",
            json={"reviews": large_batch},
            timeout=5
        )
        if response.status_code == 422:
            print("   ✅ Correctly rejected oversized batch")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            all_passed = False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print("\n" + "🎯" * 30)
    print("  Customer Review Classification API - Test Suite")
    print("🎯" * 30)
    
    print(f"\nTesting API at: {API_BASE}")
    print("Make sure the Docker container is running!")
    print("Run: docker-compose up")
    
    results = {
        "Health Check": test_health_check(),
        "Get Labels": test_get_labels(),
        "Single Classification": test_single_classification(),
        "Batch Classification": test_batch_classification(),
        "Error Handling": test_error_handling()
    }
    
    # Summary
    print_section("Test Summary")
    total = len(results)
    passed = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The API is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)

# Made with Bob
