import React from 'react';
import { Card, Row, Col } from 'react-bootstrap';

const SystemInfo = ({ systemMemory }) => {
  // Format bytes to human-readable format
  const formatBytes = (bytes, decimals = 2) => {
    if (!bytes) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
  };

  // Determine color based on memory usage
  const getMemoryBarColor = (percent) => {
    if (percent > 90) return 'danger';
    if (percent > 70) return 'warning';
    return '';
  };

  if (!systemMemory || !systemMemory.total) {
    return (
      <Card className="system-info">
        <Card.Body>
          <Card.Title>System Memory</Card.Title>
          <p>Loading system information...</p>
        </Card.Body>
      </Card>
    );
  }

  const memoryPercent = systemMemory.percent || 
    ((systemMemory.total - systemMemory.available) / systemMemory.total * 100);
  const memoryBarClass = getMemoryBarColor(memoryPercent);

  return (
    <Card className="system-info">
      <Card.Body>
        <Card.Title>System Memory</Card.Title>
        <Row>
          <Col md={6}>
            <p>
              <strong>Total:</strong> {formatBytes(systemMemory.total)}
            </p>
            <p>
              <strong>Available:</strong> {formatBytes(systemMemory.available)}
            </p>
            <p>
              <strong>Used:</strong> {formatBytes(systemMemory.total - systemMemory.available)} 
              ({memoryPercent.toFixed(1)}%)
            </p>
          </Col>
          <Col md={6}>
            <div className="memory-bar">
              <div 
                className={`memory-bar-fill ${memoryBarClass}`}
                style={{ width: `${memoryPercent}%` }}
              />
            </div>
            <div className="d-flex justify-content-between mt-1">
              <small>0%</small>
              <small>50%</small>
              <small>100%</small>
            </div>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

export default SystemInfo;