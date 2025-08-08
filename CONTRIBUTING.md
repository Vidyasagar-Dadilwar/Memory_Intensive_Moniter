# Contributing to Memory Intensive Monitor

Thank you for considering contributing to Memory Intensive Monitor! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Bugs are tracked as GitHub issues. When you create an issue, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots if applicable
- Your environment details (OS, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are also tracked as GitHub issues. When suggesting an enhancement, please include:

- A clear and descriptive title
- A detailed description of the proposed functionality
- Any potential implementation details you can provide
- Why this enhancement would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Run tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 14 or higher
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/memory-intensive.git
cd memory-intensive

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## Project Structure

```
├── backend/              # FastAPI backend
│   ├── app/              # Application code
│   │   ├── __init__.py
│   │   ├── api.py        # API endpoints
│   │   ├── logger.py     # Logging functionality
│   │   ├── main.py       # Application entry point
│   │   └── monitor.py    # Process monitoring
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.jsx       # Main application component
│   │   └── index.js      # Entry point
│   ├── Dockerfile
│   └── package.json
├── docs/                # Documentation
└── tests/               # Test files
```

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use docstrings for functions and classes
- Write unit tests for new functionality

### JavaScript/React

- Follow ESLint configuration
- Use functional components with hooks
- Document component props with JSDoc

## Testing

### Backend Tests

```bash
cd tests
python -m unittest discover
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Documentation

Please update documentation when adding or modifying features. This includes:

- Code comments and docstrings
- README.md updates if needed
- API documentation in docs/api.md
- Usage documentation in docs/usage.md

## Versioning

We use [Semantic Versioning](https://semver.org/) for releases.

## License

By contributing to Memory Intensive Monitor, you agree that your contributions will be licensed under the project's MIT License.