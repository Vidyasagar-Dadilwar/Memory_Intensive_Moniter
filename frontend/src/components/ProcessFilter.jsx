import React from 'react';
import { Form, InputGroup, FormControl, Dropdown, DropdownButton } from 'react-bootstrap';

/**
 * ProcessFilter component provides filtering and sorting controls for the process list
 * 
 * @param {Object} props Component properties
 * @param {string} props.filterText Current filter text
 * @param {Function} props.onFilterChange Handler for filter text changes
 * @param {number} props.topCount Current top count filter
 * @param {Function} props.onTopCountChange Handler for top count changes
 * @param {string} props.sortBy Current sort field
 * @param {Function} props.onSortChange Handler for sort field changes
 */
const ProcessFilter = ({ 
  filterText, 
  onFilterChange, 
  topCount, 
  onTopCountChange,
  sortBy,
  onSortChange
}) => {
  // Available top count options
  const topOptions = [10, 25, 50, 100, 0];
  
  // Available sort options with display names
  const sortOptions = [
    { value: 'memory_percent', display: 'Memory Usage' },
    { value: 'cpu_percent', display: 'CPU Usage' },
    { value: 'name', display: 'Process Name' },
    { value: 'pid', display: 'PID' }
  ];
  
  // Get current sort option display name
  const currentSortDisplay = sortOptions.find(opt => opt.value === sortBy)?.display || 'Memory Usage';
  
  return (
    <div className="process-filter mb-3">
      <div className="row align-items-center">
        <div className="col-md-6 mb-2 mb-md-0">
          <InputGroup>
            <InputGroup.Text>
              <i className="bi bi-search"></i>
            </InputGroup.Text>
            <FormControl
              placeholder="Filter processes by name, PID, or user..."
              value={filterText}
              onChange={(e) => onFilterChange(e.target.value)}
              aria-label="Filter processes"
            />
            {filterText && (
              <InputGroup.Text 
                style={{ cursor: 'pointer' }}
                onClick={() => onFilterChange('')}
              >
                <i className="bi bi-x-circle"></i>
              </InputGroup.Text>
            )}
          </InputGroup>
        </div>
        
        <div className="col-md-3 mb-2 mb-md-0">
          <InputGroup>
            <InputGroup.Text>Sort By</InputGroup.Text>
            <DropdownButton 
              variant="outline-secondary" 
              title={currentSortDisplay}
              id="sort-dropdown"
            >
              {sortOptions.map(option => (
                <Dropdown.Item 
                  key={option.value}
                  active={sortBy === option.value}
                  onClick={() => onSortChange(option.value)}
                >
                  {option.display}
                </Dropdown.Item>
              ))}
            </DropdownButton>
          </InputGroup>
        </div>
        
        <div className="col-md-3">
          <InputGroup>
            <InputGroup.Text>Show Top</InputGroup.Text>
            <DropdownButton 
              variant="outline-secondary" 
              title={topCount === 0 ? 'All' : topCount}
              id="top-dropdown"
            >
              {topOptions.map(count => (
                <Dropdown.Item 
                  key={count}
                  active={topCount === count}
                  onClick={() => onTopCountChange(count)}
                >
                  {count === 0 ? 'All' : count}
                </Dropdown.Item>
              ))}
            </DropdownButton>
          </InputGroup>
        </div>
      </div>
    </div>
  );
};

export default ProcessFilter;