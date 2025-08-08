import React from 'react';
import { Table, Button, Spinner } from 'react-bootstrap';
import { FaSort, FaSortUp, FaSortDown, FaSkull } from 'react-icons/fa';

const ProcessTable = ({
  processes,
  loading,
  sortField,
  sortDirection,
  onSort,
  onKill,
  onSelect,
  selectedPid,
  thresholds
}) => {
  // Helper to determine row class based on thresholds
  const getRowClass = (process) => {
    let classes = [];
    
    // Selected row
    if (selectedPid === process.pid) {
      classes.push('selected');
    }
    
    // Threshold classes
    if (process.memory_percent > thresholds.memoryThreshold * 2) {
      classes.push('danger');
    } else if (process.memory_percent > thresholds.memoryThreshold) {
      classes.push('warning');
    }
    
    return classes.join(' ');
  };

  // Helper to render sort icon
  const renderSortIcon = (field) => {
    if (field !== sortField) {
      return <FaSort className="ms-1" />;
    }
    return sortDirection === 'asc' ? <FaSortUp className="ms-1" /> : <FaSortDown className="ms-1" />;
  };

  return (
    <div className="process-table-container">
      <Table striped bordered hover responsive className="process-table">
        <thead>
          <tr>
            <th onClick={() => onSort('pid')}>
              PID {renderSortIcon('pid')}
            </th>
            <th onClick={() => onSort('name')}>
              Name {renderSortIcon('name')}
            </th>
            <th onClick={() => onSort('username')}>
              User {renderSortIcon('username')}
            </th>
            <th onClick={() => onSort('memory_rss')}>
              Memory (MB) {renderSortIcon('memory_rss')}
            </th>
            <th onClick={() => onSort('memory_percent')}>
              Memory % {renderSortIcon('memory_percent')}
            </th>
            <th onClick={() => onSort('cpu_percent')}>
              CPU % {renderSortIcon('cpu_percent')}
            </th>
            <th onClick={() => onSort('create_time')}>
              Start Time {renderSortIcon('create_time')}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan="8" className="text-center py-4">
                <Spinner animation="border" role="status">
                  <span className="visually-hidden">Loading...</span>
                </Spinner>
              </td>
            </tr>
          ) : processes.length === 0 ? (
            <tr>
              <td colSpan="8" className="text-center py-4">
                No processes found
              </td>
            </tr>
          ) : (
            processes.map((process) => (
              <tr 
                key={process.pid} 
                className={`process-row ${getRowClass(process)}`}
                onClick={() => onSelect(process)}
                style={{ cursor: 'pointer' }}
              >
                <td>{process.pid}</td>
                <td>{process.name}</td>
                <td>{process.username}</td>
                <td>{process.memory_rss_mb.toFixed(2)}</td>
                <td>
                  <div className="d-flex align-items-center">
                    <div 
                      className="me-2" 
                      style={{
                        width: '50px', 
                        height: '10px', 
                        backgroundColor: 
                          process.memory_percent > thresholds.memoryThreshold * 2 ? '#dc3545' :
                          process.memory_percent > thresholds.memoryThreshold ? '#ffc107' : 
                          '#007bff',
                        borderRadius: '2px'
                      }}
                    />
                    {process.memory_percent.toFixed(2)}%
                  </div>
                </td>
                <td>
                  <div className="d-flex align-items-center">
                    <div 
                      className="me-2" 
                      style={{
                        width: `${Math.min(50, process.cpu_percent / 2)}px`, 
                        height: '10px', 
                        backgroundColor: 
                          process.cpu_percent > thresholds.cpuThreshold * 2 ? '#dc3545' :
                          process.cpu_percent > thresholds.cpuThreshold ? '#ffc107' : 
                          '#28a745',
                        borderRadius: '2px'
                      }}
                    />
                    {process.cpu_percent.toFixed(2)}%
                  </div>
                </td>
                <td>{process.start_time}</td>
                <td>
                  <Button
                    variant="danger"
                    size="sm"
                    className="kill-button"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent row selection
                      onKill(process.pid);
                    }}
                    title="Terminate Process"
                  >
                    <FaSkull /> Kill
                  </Button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
};

export default ProcessTable;