import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Navbar, Nav, Button, Spinner } from 'react-bootstrap';
import { ToastContainer, toast } from 'react-toastify';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-toastify/dist/ReactToastify.css';
import ProcessTable from './components/ProcessTable';
import SystemInfo from './components/SystemInfo';
import ThresholdSettings from './components/ThresholdSettings';
import ProcessChart from './components/ProcessChart';
import './App.css';

function App() {
  // State
  const [processes, setProcesses] = useState([]);
  const [systemMemory, setSystemMemory] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(2000); // 2 seconds
  const [sortField, setSortField] = useState('memory_percent');
  const [sortDirection, setSortDirection] = useState('desc');
  const [thresholdSettings, setThresholdSettings] = useState({
    memoryThreshold: 10, // Default 10%
    cpuThreshold: 50,    // Default 50%
    enableAlerts: true,
    alertDebounce: 10    // 10 seconds
  });
  const [showSettings, setShowSettings] = useState(false);
  const [selectedProcess, setSelectedProcess] = useState(null);
  const [processHistory, setProcessHistory] = useState([]);
  const [showChart, setShowChart] = useState(false);
  const [filterText, setFilterText] = useState('');
  const [topN, setTopN] = useState(20);
  
  // WebSocket connection
  const [wsConnected, setWsConnected] = useState(false);
  const [ws, setWs] = useState(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const wsUrl = `ws://${window.location.hostname}:8000/ws/processes`;
      const socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log('WebSocket connected');
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setProcesses(data.processes || []);
        setSystemMemory(data.system_memory || {});
        setLoading(false);
      };

      socket.onclose = () => {
        console.log('WebSocket disconnected');
        setWsConnected(false);
        // Try to reconnect after a delay
        setTimeout(connectWebSocket, 5000);
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      };

      setWs(socket);

      return socket;
    };

    // Try to connect via WebSocket first
    const socket = connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, []);

  // Fallback to polling if WebSocket fails
  useEffect(() => {
    let intervalId;

    const fetchData = async () => {
      try {
        // Only fetch via HTTP if WebSocket is not connected
        if (!wsConnected) {
          setLoading(true);
          const response = await fetch(`/api/processes?top=${topN}&sort_by=${sortField}`);
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const data = await response.json();
          setProcesses(data.processes || []);
          setSystemMemory(data.system_memory || {});
          setLoading(false);
        }
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    // Only use polling if WebSocket is not connected
    if (!wsConnected) {
      fetchData(); // Initial fetch
      intervalId = setInterval(fetchData, refreshInterval);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [wsConnected, refreshInterval, topN, sortField]);

  // Alert for high memory usage
  useEffect(() => {
    if (!thresholdSettings.enableAlerts || !processes.length) return;

    const highMemoryProcesses = processes.filter(
      p => p.memory_percent > thresholdSettings.memoryThreshold
    );

    if (highMemoryProcesses.length > 0) {
      // Get the top memory consumer
      const topProcess = highMemoryProcesses[0];
      
      // Show notification (debounced)
      const notificationKey = `mem-${topProcess.pid}`;
      toast.warning(
        `Process ${topProcess.name} (PID: ${topProcess.pid}) is using ${topProcess.memory_percent.toFixed(2)}% of memory`,
        {
          toastId: notificationKey,
          autoClose: 5000,
        }
      );

      // Request permission for browser notifications if not already granted
      if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
        Notification.requestPermission();
      }

      // Show browser notification if permitted
      if (Notification.permission === 'granted') {
        new Notification('High Memory Usage', {
          body: `Process ${topProcess.name} (PID: ${topProcess.pid}) is using ${topProcess.memory_percent.toFixed(2)}% of memory`,
          icon: '/logo192.png'
        });
      }
    }
  }, [processes, thresholdSettings]);

  // Handle process selection for detailed view
  const handleProcessSelect = async (process) => {
    setSelectedProcess(process);
    setShowChart(true);
    
    try {
      // Fetch process history if logging is enabled
      const response = await fetch(`/api/processes/${process.pid}/history`);
      if (response.ok) {
        const data = await response.json();
        setProcessHistory(data);
      } else if (response.status !== 404) { // 404 means logging is not enabled
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
    } catch (err) {
      console.error('Error fetching process history:', err);
      toast.error(`Could not fetch process history: ${err.message}`);
    }
  };

  // Handle process termination
  const handleProcessKill = async (pid) => {
    if (!window.confirm(`Are you sure you want to terminate process with PID ${pid}?`)) {
      return;
    }
    
    try {
      const response = await fetch('/api/processes/kill', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pid }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success(result.message);
        // If the killed process was selected, clear the selection
        if (selectedProcess && selectedProcess.pid === pid) {
          setSelectedProcess(null);
          setShowChart(false);
        }
      } else {
        toast.error(result.message);
      }
    } catch (err) {
      console.error('Error killing process:', err);
      toast.error(`Failed to terminate process: ${err.message}`);
    }
  };

  // Handle sorting
  const handleSort = (field) => {
    if (field === sortField) {
      // Toggle direction if same field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // New field, default to descending
      setSortField(field);
      setSortDirection('desc');
    }
  };

  // Apply client-side filtering
  const filteredProcesses = processes.filter(process => {
    if (!filterText) return true;
    const searchTerm = filterText.toLowerCase();
    return (
      process.name.toLowerCase().includes(searchTerm) ||
      process.pid.toString().includes(searchTerm) ||
      (process.username && process.username.toLowerCase().includes(searchTerm))
    );
  });

  return (
    <div className="App">
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand>Memory Intensive Monitor</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link onClick={() => setShowSettings(true)}>Settings</Nav.Link>
              <Nav.Link href="/api/docs" target="_blank">API Docs</Nav.Link>
            </Nav>
            <Navbar.Text>
              {wsConnected ? (
                <span className="text-success">WebSocket Connected</span>
              ) : (
                <span className="text-warning">Using HTTP Polling</span>
              )}
            </Navbar.Text>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container fluid className="mt-3">
        {error && (
          <div className="alert alert-danger">
            Error: {error}
            <Button 
              variant="outline-danger" 
              size="sm" 
              className="ms-2"
              onClick={() => setError(null)}
            >
              Dismiss
            </Button>
          </div>
        )}

        <Row>
          <Col md={showChart && selectedProcess ? 8 : 12}>
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h2>Process Monitor</h2>
              <div className="d-flex">
                <input
                  type="text"
                  className="form-control me-2"
                  placeholder="Filter processes..."
                  value={filterText}
                  onChange={(e) => setFilterText(e.target.value)}
                />
                <select 
                  className="form-select me-2" 
                  value={topN}
                  onChange={(e) => setTopN(Number(e.target.value))}
                >
                  <option value="10">Top 10</option>
                  <option value="20">Top 20</option>
                  <option value="50">Top 50</option>
                  <option value="100">Top 100</option>
                  <option value="0">All</option>
                </select>
                <Button 
                  variant="primary" 
                  onClick={() => {
                    setLoading(true);
                    if (ws && ws.readyState === WebSocket.OPEN) {
                      // Request fresh data via WebSocket
                      ws.send(JSON.stringify({ action: 'refresh' }));
                    }
                    // Otherwise the polling will handle it
                  }}
                >
                  {loading ? <Spinner animation="border" size="sm" /> : 'Refresh'}
                </Button>
              </div>
            </div>

            <SystemInfo systemMemory={systemMemory} />

            <ProcessTable 
              processes={filteredProcesses}
              loading={loading}
              sortField={sortField}
              sortDirection={sortDirection}
              onSort={handleSort}
              onKill={handleProcessKill}
              onSelect={handleProcessSelect}
              selectedPid={selectedProcess?.pid}
              thresholds={thresholdSettings}
            />
          </Col>

          {showChart && selectedProcess && (
            <Col md={4}>
              <div className="process-details card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h3>Process Details</h3>
                  <Button 
                    variant="outline-secondary" 
                    size="sm"
                    onClick={() => {
                      setSelectedProcess(null);
                      setShowChart(false);
                    }}
                  >
                    Close
                  </Button>
                </div>
                <div className="card-body">
                  <h4>{selectedProcess.name} (PID: {selectedProcess.pid})</h4>
                  <p><strong>User:</strong> {selectedProcess.username}</p>
                  <p><strong>Status:</strong> {selectedProcess.status}</p>
                  <p><strong>Started:</strong> {selectedProcess.start_time}</p>
                  <p><strong>Memory:</strong> {selectedProcess.memory_rss_mb} MB ({selectedProcess.memory_percent}%)</p>
                  <p><strong>CPU:</strong> {selectedProcess.cpu_percent}%</p>
                  
                  <div className="mt-3">
                    <Button 
                      variant="danger" 
                      onClick={() => handleProcessKill(selectedProcess.pid)}
                    >
                      Terminate Process
                    </Button>
                  </div>

                  {processHistory.length > 0 && (
                    <div className="mt-4">
                      <h5>Memory/CPU History</h5>
                      <ProcessChart history={processHistory} />
                    </div>
                  )}
                </div>
              </div>
            </Col>
          )}
        </Row>
      </Container>

      <ThresholdSettings 
        show={showSettings}
        settings={thresholdSettings}
        onHide={() => setShowSettings(false)}
        onSave={(newSettings) => {
          setThresholdSettings(newSettings);
          setShowSettings(false);
          toast.success('Settings updated');
        }}
        refreshInterval={refreshInterval}
        onRefreshIntervalChange={setRefreshInterval}
      />

      <ToastContainer position="bottom-right" />
    </div>
  );
}

export default App;