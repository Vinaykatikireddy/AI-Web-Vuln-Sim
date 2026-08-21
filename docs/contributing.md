# Contributing

Thank you for your interest in contributing to the AI-Powered Web Application Attack Simulation Platform! This document provides guidelines for contributing to the project.

## Code of Conduct

We follow the [Contributor Covenant](https://contributor-covenant.org/) Code of Conduct. All contributors are expected to be respectful and professional in all interactions.

## Getting Started

### Prerequisites

Before contributing to this project, please ensure you have the following installed:

- Docker and Docker Compose
- Python 3.10+
- Node.js 18+
- Git
- PostgreSQL
- Redis

### Setting Up the Development Environment

1. Clone the repository:
```bash
git clone https://github.com/your-username/attack-simulation-platform.git
cd attack-simulation-platform
```

2. Set up the backend:
```bash
cd backend
poetry install
```

3. Set up the frontend:
```bash
cd ../../frontend
npm install
```

4. Set up the database:
```bash
cd ../scripts
python create_tables.py
```

5. Start the development environment:
```bash
cd ../../scripts
./dev.sh
```

The application should now be available at http://localhost:3000

## Development Workflow

### Branching Strategy

We use a Git flow-like branching strategy:

- `main` branch: Production-ready code
- `develop` branch: Integration branch for features
- `feature/*` branches: Individual features
- `bugfix/*` branches: Bug fixes
- `release/*` branches: Release preparation

### Commit Messages

Commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

body

footer
```

Examples:
- `feat(auth): add JWT token validation`
- `fix(login): prevent empty password submissions`
- `docs(architecture): update deployment section`

### Code Style

#### Python (Backend)
- Follow PEP 8 style guidelines
- Use 4 spaces for indentation
- Type hints are required for all functions
- Use docstrings for all public functions and classes
- Use `black` for formatting
- Use `flake8` for linting

#### JavaScript/TypeScript (Frontend)
- Use Prettier for formatting
- Use ESLint with Airbnb style guide
- Use TypeScript for type safety
- Follow React best practices

## Testing

### Backend Testing

Backend tests are written using `pytest` and should be located in `tests/backend/`.

Run tests:
```bash
cd backend
poetry run pytest tests/backend/
```

### Frontend Testing

Frontend tests are written using `vitest` and should be located in `tests/frontend/`.

Run tests:
```bash
cd frontend
npm run test
```

### Integration Testing

Integration tests are written using `pytest` and should be located in `tests/integration/`.

Run integration tests:
```bash
cd backend
poetry run pytest tests/integration/
```

### End-to-End Testing

End-to-end tests are written using `Playwright` and should be located in `tests/e2e/`.

Run end-to-end tests:
```bash
cd frontend
npm run test:e2e
```

### Docker Testing

Container tests verify that each service starts correctly and communicates properly.

Run Docker tests:
```bash
cd docker
./test_containers.sh
```

### Code Coverage

We aim for at least 80% code coverage:

```bash
cd backend
poetry run pytest --cov=app --cov-report=html tests/
```

## Pull Request Guidelines

1. **Single Purpose**: Each PR should address a single issue or feature
2. **Clear Description**: Include a detailed description of your changes
3. **Test Coverage**: Include tests for new functionality
4. **Documentation**: Update documentation as needed
5. **Sign-off**: Add `Signed-off-by: Your Name <email@example.com>` to your commit

## Review Process

1. Submit your PR to the `develop` branch
2. The maintainers will review your changes
3. You may be asked to make changes based on feedback
4. Once approved, your PR will be merged into `develop`
5. Periodically, `develop` is merged into `main` for releases

## Security

As this is a cybersecurity training platform, security is paramount:

1. **No Hardcoded Secrets**: Never commit API keys, credentials, or secrets
2. **Input Validation**: Always validate and sanitize user inputs
3. **Error Handling**: Never expose stack traces or sensitive error information in production
4. **Authentication**: Always validate user permissions
5. **Docker Security**: Containers must run as non-root users when possible

## Documentation

All new features must be documented. Please update:

- `/docs/architecture.md` - Architecture changes
- `/docs/api.md` - API documentation
- `/docs/deployment.md` - Deployment instructions
- `/docs/security.md` - Security considerations

## Issues

If you encounter a bug or have a feature request:

1. Search existing issues to avoid duplicates
2. Create a detailed issue with:
   - Clear title
   - Description of the problem
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment information

## Reporting Security Issues

If you discover a security vulnerability:

1. Do not create a public issue
2. Email the security team at security@attack-simulation-platform.com
3. Provide details of the vulnerability and steps to reproduce
4. We'll respond within 72 hours

## Acknowledgments

We thank all contributors to this project! Your contributions make this platform better for everyone.

*This project follows the Open Source Guide for contributing: https://opensource.guide/*