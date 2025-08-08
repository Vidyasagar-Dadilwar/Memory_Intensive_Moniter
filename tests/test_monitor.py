import unittest
import asyncio
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.monitor import ProcessMonitor


class TestProcessMonitor(unittest.TestCase):
    """Test cases for the ProcessMonitor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.monitor = ProcessMonitor()
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.loop.run_until_complete(self.monitor.shutdown())
        self.loop.close()
    
    def test_initialization(self):
        """Test that the monitor initializes correctly"""
        self.loop.run_until_complete(self.monitor.initialize())
        self.assertTrue(self.monitor.initialized)
        self.assertIsNotNone(self.monitor.last_update)
    
    def test_update(self):
        """Test that the monitor updates process list"""
        self.loop.run_until_complete(self.monitor.initialize())
        self.loop.run_until_complete(self.monitor.update())
        
        # Check that we have processes
        self.assertGreater(len(self.monitor.processes), 0)
        
        # Check that process data has expected fields
        process = self.monitor.processes[0]
        self.assertIn('pid', process)
        self.assertIn('name', process)
        self.assertIn('memory_percent', process)
        self.assertIn('cpu_percent', process)
    
    def test_get_snapshot(self):
        """Test getting a snapshot with filtering"""
        self.loop.run_until_complete(self.monitor.initialize())
        
        # Get full snapshot
        snapshot = self.monitor.get_snapshot()
        self.assertIn('processes', snapshot)
        self.assertIn('timestamp', snapshot)
        self.assertIn('system_memory', snapshot)
        
        # Get filtered snapshot (top 5)
        filtered = self.monitor.get_snapshot(top=5)
        self.assertEqual(len(filtered['processes']), 5)
        
        # Get filtered snapshot with memory threshold
        threshold = 0.1  # 0.1% memory usage
        filtered = self.monitor.get_snapshot(min_mem_percent=threshold)
        for process in filtered['processes']:
            self.assertGreaterEqual(process['memory_percent'], threshold)
    
    def test_sort_options(self):
        """Test sorting functionality"""
        self.loop.run_until_complete(self.monitor.initialize())
        
        # Test sorting by memory (default)
        self.monitor.set_sort_options('memory_percent', True)
        self.loop.run_until_complete(self.monitor.update())
        
        # Check that processes are sorted by memory_percent in descending order
        for i in range(len(self.monitor.processes) - 1):
            self.assertGreaterEqual(
                self.monitor.processes[i]['memory_percent'],
                self.monitor.processes[i + 1]['memory_percent']
            )
        
        # Test sorting by CPU
        self.monitor.set_sort_options('cpu_percent', True)
        self.loop.run_until_complete(self.monitor.update())
        
        # Check that processes are sorted by cpu_percent in descending order
        for i in range(len(self.monitor.processes) - 1):
            self.assertGreaterEqual(
                self.monitor.processes[i]['cpu_percent'],
                self.monitor.processes[i + 1]['cpu_percent']
            )


if __name__ == '__main__':
    unittest.main()