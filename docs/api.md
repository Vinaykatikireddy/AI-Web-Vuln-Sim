# API Documentation

This document provides comprehensive documentation for the AI-Powered Web Application Attack Simulation Platform API.

## Overview

The API follows RESTful principles with JSON as the primary data format. All endpoints are accessible via HTTPS and require authentication via JWT tokens.

### Base URL

```
https://your-domain.com/api
```

### Authentication

All protected endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Tokens are obtained by authenticating with the `/auth/login` endpoint.

### Response Format

Successful responses:
```json
{
  "data": {},
  "meta": {
    "timestamp": "2026-06-06T12:00:00Z",
    "version": "0.1.0"
  }
}
```

Error responses:
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired token",
    "details": {}
  }
}
```

### Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Success |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Authentication successful but insufficient privileges |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Unexpected server error |
| 503 | Service Unavailable - Server temporarily unable to handle request |

## Authentication Endpoints

### Register User

Registers a new user account.

```
POST /auth/register
```

**Request Body**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Password Requirements**:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Response (201)**:
```json
{
  "data": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (400)**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Password must be at least 8 characters long",
    "details": {}
  }
}
```

### Login

Authenticates a user and returns a JWT token.

```
POST /auth/login
```

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200)**:
```json
{
  "data": {
    "access_token": "string",
    "token_type": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (401)**:
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Incorrect username or password",
    "details": {}
  }
}
```

### Get Current User

Retrieves the current authenticated user's profile.

```
GET /auth/me
```

**Response (200)**:
```json
{
  "data": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (401)**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required",
    "details": {}
  }
}
```

## Dashboard Endpoints

### Get Dashboard

Retrieves dashboard information for the current user.

```
GET /dashboard
```

**Response (200)**:
```json
{
  "data": {
    "user_id": "integer",
    "username": "string",
    "total_scans": "integer",
    "completed_scans": "integer",
    "active_labs": "integer",
    "recent_scans": [
      {
        "id": "integer",
        "lab_name": "string",
        "attack_type": "string",
        "status": "string",
        "created_at": "string"
      }
    ],
    "recent_reports": [
      {
        "id": "integer",
        "scan_id": "integer",
        "format": "string",
        "generated_at": "string",
        "status": "string"
      }
    ]
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

## Labs Endpoints

### List Labs

Retrieves a list of all available vulnerable labs.

```
GET /labs
```

**Response (200)**:
```json
{
  "data": [
    {
      "id": "integer",
      "name": "string",
      "description": "string",
      "docker_image": "string",
      "port": "integer",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

### Get Lab

Retrieves details for a specific lab.

```
GET /labs/{lab_id}
```

**Path Parameters**:
- `lab_id`: ID of the lab to retrieve

**Response (200)**:
```json
{
  "data": {
    "id": "integer",
    "name": "string",
    "description": "string",
    "docker_image": "string",
    "port": "integer",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "LAB_NOT_FOUND",
    "message": "Lab not found",
    "details": {}
  }
}
```

### Start Lab

Starts a vulnerable lab container.

```
POST /labs/start
```

**Request Body**:
```json
{
  "lab_id": "integer"
}
```

**Response (200)**:
```json
{
  "data": {
    "message": "string",
    "lab": {
      "id": "integer",
      "name": "string",
      "description": "string",
      "docker_image": "string",
      "port": "integer",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "LAB_NOT_FOUND",
    "message": "Lab not found",
    "details": {}
  }
}
```

**Response (409)**:
```json
{
  "error": {
    "code": "LAB_ALREADY_RUNNING",
    "message": "Lab is already running",
    "details": {}
  }
}
```

### Stop Lab

Stops a vulnerable lab container.

```
POST /labs/stop
```

**Request Body**:
```json
{
  "lab_id": "integer"
}
```

**Response (200)**:
```json
{
  "data": {
    "message": "string",
    "lab": {
      "id": "integer",
      "name": "string",
      "description": "string",
      "docker_image": "string",
      "port": "integer",
      "status": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "LAB_NOT_FOUND",
    "message": "Lab not found",
    "details": {}
  }
}
```

**Response (409)**:
```json
{
  "error": {
    "code": "LAB_ALREADY_STOPPED",
    "message": "Lab is already stopped",
    "details": {}
  }
}
```

## Scans Endpoints

### Run Scan

Initiates a security scan against a vulnerable lab.

```
POST /scans/run
```

**Request Body**:
```json
{
  "lab_id": "integer",
  "attack_type": "string"
}
```

**Attack Types**:
- `sql_injection` - SQL Injection
- `reflected_xss` - Reflected XSS
- `stored_xss` - Stored XSS
- `idor` - Insecure Direct Object Reference
- `auth_bypass` - Authentication Bypass
- `dir_traversal` - Directory Traversal
- `file_upload_abuse` - File Upload Abuse

**Response (201)**:
```json
{
  "data": {
    "id": "integer",
    "user_id": "integer",
    "lab_id": "integer",
    "attack_type": "string",
    "status": "string",
    "started_at": "string",
    "completed_at": "string",
    "created_at": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "LAB_NOT_FOUND",
    "message": "Lab not found",
    "details": {}
  }
}
```

**Response (409)**:
```json
{
  "error": {
    "code": "LAB_NOT_RUNNING",
    "message": "Lab is not currently running",
    "details": {}
  }
}
```

### Get Scan History

Retrieves the user's scan history.

```
GET /scans/history
```

**Query Parameters**:
- `limit`: Maximum number of results (default: 10)
- `offset`: Number of results to skip (default: 0)

**Response (200)**:
```json
{
  "data": [
    {
      "id": "integer",
      "user_id": "integer",
      "lab_id": "integer",
      "attack_type": "string",
      "status": "string",
      "started_at": "string",
      "completed_at": "string",
      "created_at": "string",
      "lab": {
        "id": "integer",
        "name": "string",
        "status": "string"
      }
    }
  ],
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

## Reports Endpoints

### Get Report

Retrieves a security report.

```
GET /reports/{id}
```

**Path Parameters**:
- `id`: ID of the report to retrieve

**Query Parameters**:
- `format`: Output format (html, markdown, pdf)

**Response (200)**:
```json
{
  "data": {
    "id": "integer",
    "scan_id": "integer",
    "user_id": "integer",
    "content": "string",
    "format": "string",
    "generated_at": "string",
    "status": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "REPORT_NOT_FOUND",
    "message": "Report not found",
    "details": {}
  }
}
```

## AI Analysis Endpoints

### Analyze Scan

Initiates AI analysis of a scan's logs.

```
POST /ai/analyze
```

**Request Body**:
```json
{
  "scan_id": "integer"
}
```

**Response (201)**:
```json
{
  "data": {
    "message": "string",
    "scan_id": "integer",
    "analysis_status": "string"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

**Response (404)**:
```json
{
  "error": {
    "code": "SCAN_NOT_FOUND",
    "message": "Scan not found",
    "details": {}
  }
}
```

**Response (409)**:
```json
{
  "error": {
    "code": "ANALYSIS_IN_PROGRESS",
    "message": "Analysis already in progress for this scan",
    "details": {}
  }
}
```

## Settings Endpoints

### Get User Settings

Retrieves the current user's settings.

```
GET /settings
```

**Response (200)**:
```json
{
  "data": {
    "notifications": "boolean",
    "email_notifications": "boolean",
    "dark_mode": "boolean",
    "ai_analytics": "boolean",
    "auto_generate_reports": "boolean",
    "ai_endpoint": "string",
    "ai_api_key": "string",
    "data_retention": "integer"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

### Update User Settings

Updates the current user's settings.

```
PUT /settings
```

**Request Body**:
```json
{
  "notifications": "boolean",
  "email_notifications": "boolean",
  "dark_mode": "boolean",
  "ai_analytics": "boolean",
  "auto_generate_reports": "boolean",
  "ai_endpoint": "string",
  "ai_api_key": "string",
  "data_retention": "integer"
}
```

**Response (200)**:
```json
{
  "data": {
    "notifications": "boolean",
    "email_notifications": "boolean",
    "dark_mode": "boolean",
    "ai_analytics": "boolean",
    "auto_generate_reports": "boolean",
    "ai_endpoint": "string",
    "ai_api_key": "string",
    "data_retention": "integer"
  },
  "meta": {
    "timestamp": "string",
    "version": "string"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Invalid input parameters |
| INVALID_CREDENTIALS | Incorrect username or password |
| UNAUTHORIZED | Authentication required |
| LAB_NOT_FOUND | The specified lab doesn't exist |
| LAB_ALREADY_RUNNING | The lab is already running |
| LAB_ALREADY_STOPPED | The lab is already stopped |
| LAB_NOT_RUNNING | The lab is not currently running |
| SCAN_NOT_FOUND | The specified scan doesn't exist |
| ANALYSIS_IN_PROGRESS | Analysis is already underway for this scan |
| REPORT_NOT_FOUND | The specified report doesn't exist |
| DATABASE_ERROR | Database operation failed |
| AI_SERVICE_ERROR | AI analysis service failed |
| RATE_LIMITED | Request limit exceeded |
| INTERNAL_SERVER_ERROR | Unexpected server error |
| SERVICE_UNAVAILABLE | Server temporarily unavailable |

## API Rate Limits

To prevent abuse, rate limits are enforced:

| Endpoint | Limit | Time Window |
|----------|-------|-------------|
| `/auth/login` | 5 requests | 5 minutes |
| `/auth/register` | 10 requests | 24 hours |
| `/scans/run` | 10 requests | 1 minute |
| `/ai/analyze` | 5 requests | 1 minute |
| `/reports/{id}` | 20 requests | 1 minute |
| `/dashboard` | 30 requests | 1 minute |
| All other endpoints | 50 requests | 1 minute |

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum number of requests allowed
- `X-RateLimit-Remaining`: Number of requests remaining
- `X-RateLimit-Reset`: Time when the limit resets

## API Versioning

The API supports versioning through the URL path. Currently, only v1 is available:

```
https://your-domain.com/api/v1/
```

Future versions will be available at `/api/v2/`, etc., with backward compatibility maintained for older versions.

## Swagger/OpenAPI Documentation

The full OpenAPI specification is available at:

```
https://your-domain.com/api/docs
```

This interactive documentation provides detailed information about all endpoints, request/response examples, and allows for testing API calls directly from the browser.

## Testing API

You can test the API using tools like:

1. **curl**:
   ```bash
   curl -X POST https://your-domain.com/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"testuser","password":"password123"}'
   ```

2. **Postman**:
   - Import the OpenAPI definition from `/api/docs`
   - Set the Authorization header with your token
   - Test all endpoints with sample data

3. **HTTP Clients**:
   - Python requests
   - JavaScript fetch
   - Any HTTP client library

## API Deprecation Policy

- Minor updates (feature additions): No deprecation
- Major updates (breaking changes): 90-day deprecation notice
- Deprecated endpoints: Will be removed after 6 months of deprecation
- All changes to the API will be documented in the CHANGELOG.md file

## Example Usage

Here's an example of completing an authentication, scan, and report workflow:

```python
import requests
import json

# 1. Authenticate
auth_response = requests.post(
    "https://your-domain.com/api/auth/login",
    json={"username": "testuser", "password": "password123"}
)

auth_data = auth_response.json()
token = auth_data["data"]["access_token"]

# 2. Get lab ID
labs_response = requests.get(
    "https://your-domain.com/api/labs",
    headers={"Authorization": f"Bearer {token}"}
)

labs_data = labs_response.json()
lab_id = labs_data["data"][0]["id"]

# 3. Start lab
requests.post(
    "https://your-domain.com/api/labs/start",
    json={"lab_id": lab_id},
    headers={"Authorization": f"Bearer {token}"}
)

# 4. Run scan
scan_response = requests.post(
    "https://your-domain.com/api/scans/run",
    json={"lab_id": lab_id, "attack_type": "sql_injection"},
    headers={"Authorization": f"Bearer {token}"}
)

scan_data = scan_response.json()
scan_id = scan_data["data"]["id"]

# 5. Analyze with AI
requests.post(
    "https://your-domain.com/api/ai/analyze",
    json={"scan_id": scan_id},
    headers={"Authorization": f"Bearer {token}"}
)

# 6. Get report
report_response = requests.get(
    f"https://your-domain.com/api/reports/{scan_id}",
    headers={"Authorization": f"Bearer {token}"}
)

report_data = report_response.json()
print(json.dumps(report_data, indent=2))
```

This API documentation provides a comprehensive guide for interacting with the platform's API. Always refer to the OpenAPI specification at `/api/docs` for the most up-to-date information.