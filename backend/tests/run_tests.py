#!/usr/bin/env python3
"""
Test runner for SideQuest backend tests.
This script sets up the test environment and runs the tests.
"""

import os
import sys
import subprocess
import time

def check_docker():
    """Check if Docker is running and the test database is available."""
    try:
        # Check if Docker is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Docker is not running. Please start Docker first.")
            return False
        
        # Check if test database container is running
        result = subprocess.run(['docker', 'ps', '--filter', 'name=sidequest_db_test'], capture_output=True, text=True)
        if 'sidequest_db_test' not in result.stdout:
            print("❌ Test database container is not running.")
            print("Starting test database...")
            start_test_db()
            return False
        
        print("✅ Test database is running.")
        return True
        
    except FileNotFoundError:
        print("❌ Docker is not installed or not in PATH.")
        return False

def start_test_db():
    """Start the test database using Docker Compose."""
    try:
        print("Starting test database...")
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.test.yml', 'up', '-d'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test database started successfully.")
            # Wait for database to be ready
            print("Waiting for database to be ready...")
            time.sleep(5)
            return True
        else:
            print(f"❌ Failed to start test database: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ docker-compose is not installed or not in PATH.")
        return False

def run_tests():
    """Run the SideQuest tests."""
    try:
        print("Running SideQuest tests...")
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/test_sidequest_models.py',
            'tests/test_sidequest_services.py',
            '-v'
        ], capture_output=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def main():
    """Main test runner function."""
    print("🚀 SideQuest Backend Test Runner")
    print("=" * 40)
    
    # Check and start test database if needed
    if not check_docker():
        return 1
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
