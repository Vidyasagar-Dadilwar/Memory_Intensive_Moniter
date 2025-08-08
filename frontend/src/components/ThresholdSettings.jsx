import React, { useState } from 'react';
import { Modal, Button, Form, Row, Col } from 'react-bootstrap';

const ThresholdSettings = ({
  show,
  onHide,
  settings,
  onSave,
  refreshInterval,
  onRefreshIntervalChange
}) => {
  // Local state for form values
  const [formValues, setFormValues] = useState({
    memoryThreshold: settings.memoryThreshold,
    cpuThreshold: settings.cpuThreshold,
    enableAlerts: settings.enableAlerts,
    alertDebounce: settings.alertDebounce,
    refreshInterval: refreshInterval / 1000 // Convert ms to seconds for display
  });

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormValues({
      ...formValues,
      [name]: type === 'checkbox' ? checked : Number(value)
    });
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Update refresh interval
    onRefreshIntervalChange(formValues.refreshInterval * 1000); // Convert seconds to ms
    
    // Update threshold settings
    onSave({
      memoryThreshold: formValues.memoryThreshold,
      cpuThreshold: formValues.cpuThreshold,
      enableAlerts: formValues.enableAlerts,
      alertDebounce: formValues.alertDebounce
    });
  };

  return (
    <Modal show={show} onHide={onHide} centered>
      <Modal.Header closeButton>
        <Modal.Title>Monitor Settings</Modal.Title>
      </Modal.Header>
      <Form onSubmit={handleSubmit}>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Refresh Interval (seconds)</Form.Label>
            <Form.Control
              type="number"
              name="refreshInterval"
              value={formValues.refreshInterval}
              onChange={handleChange}
              min="0.5"
              max="10"
              step="0.5"
            />
            <Form.Text className="text-muted">
              How often to refresh process data (0.5 - 10 seconds)
            </Form.Text>
          </Form.Group>

          <hr />
          <h5>Threshold Settings</h5>

          <Row>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Memory Threshold (%)</Form.Label>
                <Form.Control
                  type="number"
                  name="memoryThreshold"
                  value={formValues.memoryThreshold}
                  onChange={handleChange}
                  min="1"
                  max="50"
                />
                <Form.Text className="text-muted">
                  Highlight processes using more than this % of memory
                </Form.Text>
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>CPU Threshold (%)</Form.Label>
                <Form.Control
                  type="number"
                  name="cpuThreshold"
                  value={formValues.cpuThreshold}
                  onChange={handleChange}
                  min="1"
                  max="100"
                />
                <Form.Text className="text-muted">
                  Highlight processes using more than this % of CPU
                </Form.Text>
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Check
              type="checkbox"
              label="Enable Alerts"
              name="enableAlerts"
              checked={formValues.enableAlerts}
              onChange={handleChange}
            />
            <Form.Text className="text-muted">
              Show notifications when thresholds are exceeded
            </Form.Text>
          </Form.Group>

          {formValues.enableAlerts && (
            <Form.Group className="mb-3">
              <Form.Label>Alert Debounce (seconds)</Form.Label>
              <Form.Control
                type="number"
                name="alertDebounce"
                value={formValues.alertDebounce}
                onChange={handleChange}
                min="5"
                max="60"
              />
              <Form.Text className="text-muted">
                Minimum time between alerts for the same process
              </Form.Text>
            </Form.Group>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={onHide}>
            Cancel
          </Button>
          <Button variant="primary" type="submit">
            Save Settings
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
};

export default ThresholdSettings;