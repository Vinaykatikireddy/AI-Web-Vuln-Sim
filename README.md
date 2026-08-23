---
title: ai-web-vuln-sim
emoji: 🐠
colorFrom: yellow
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# AI-Powered Web Application Attack Simulation Platform

A full-stack educational cyber range that allows users to safely launch simulated attacks against intentionally vulnerable web applications.

## Project Structure

```
project/
├── frontend/        # React/Vite/TypeScript frontend
├── backend/         # FastAPI Python backend
├── docker/          # Docker Compose configurations
├── labs/            # Vulnerable application containers
├── ai/              # AI analysis and LLM integration
├── reports/         # Report generation and templates
├── payloads/        # Attack payload library
├── docs/            # Documentation
├── tests/           # Test suites
└── scripts/         # Utility scripts
```

## Getting Started

1. Install Docker
2. Run `docker-compose up` in the docker directory
3. Navigate to http://localhost:3000

## Security Note

This platform is designed for educational purposes only. All attacks execute against isolated, intentionally vulnerable environments. Never use this platform to attack third-party systems.