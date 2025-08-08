import unittest
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI app
from backend.app.main import app


class TestAPI(unittest.TestCase):
    """Test cases for the API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('app', data)
        self.assertIn('version', data)
        self.assertIn('api_docs', data)
    
    def test_processes_endpoint(self):
        """Test the processes endpoint"""
        response = self.client.get("/api/processes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('processes', data)
        self.assertIn('timestamp', data)
        self.assertIn('system_memory', data)
        
        # Check that we have processes
        self.assertGreater(len(data['processes']), 0)
        
        # Check process data structure
        process = data['processes'][0]
        self.assertIn('pid', process)
        self.assertIn('name', process)
        self.assertIn('memory_percent', process)
        self.assertIn('cpu_percent', process)
    
    def test_processes_filtering(self):
        """Test filtering processes"""
        # Test top parameter
        response = self.client.get("/api/processes?top=5")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['processes']), 5)
        
        # Test sort_by parameter
        response = self.client.get("/api/processes?sort_by=cpu_percent")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for i in range(len(data['processes']) - 1):
            self.assertGreaterEqual(
                data['processes'][i]['cpu_percent'],
                data['processes'][i + 1]['cpu_percent']
            )
    
    def test_system_memory_endpoint(self):
        """Test the system memory endpoint"""
        response = self.client.get("/api/system/memory")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('memory', data)
        self.assertIn('swap', data)
        
        # Check memory data structure
        memory = data['memory']
        self.assertIn('total', memory)
        self.assertIn('available', memory)
        self.assertIn('used', memory)
        self.assertIn('percent', memory)
    
    def test_system_info_endpoint(self):
        """Test the system info endpoint"""
        response = self.client.get("/api/system/info")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('system', data)
        self.assertIn('processor', data)
        self.assertIn('cpu_count', data)
        self.assertIn('boot_time', data)
    
    def test_kill_process_validation(self):
        """Test process kill endpoint validation"""
        # Test with invalid data (missing pid)
        response = self.client.post("/api/processes/kill", json={})
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Test with invalid PID type
        response = self.client.post("/api/processes/kill", json={"pid": "not-a-number"})
        self.assertEqual(response.status_code, 422)  # Validation error
        
        # Test with non-existent PID (this should return 200 but with success=False)
        response = self.client.post("/api/processes/kill", json={"pid": 999999999})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('not found', data['message'].lower())


if __name__ == '__main__':
    unittest.main()