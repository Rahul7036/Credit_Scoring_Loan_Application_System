# Credit Scoring and Loan Application System

A full-stack application for managing loan applications with automated credit scoring, built using FastAPI, MongoDB, Redis, and JWT authentication.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Installation Steps](#installation-steps)
5. [API Documentation](#api-documentation)
6. [Database Schema](#database-schema)
7. [Security](#security)
8. [Frontend](#frontend)

## Project Overview

The Credit Scoring and Loan Application System is designed to:
- Process and manage loan applications
- Calculate credit scores automatically
- Provide role-based access (Admin/User)
- Track loan application status
- Ensure secure data handling

## Features

### User Features
- User registration and authentication
- Loan application submission
- Real-time loan status tracking
- Credit score visibility
- Loan history view

### Admin Features
- Comprehensive dashboard
- Loan application review
- Credit score calculation
- Application status management
- Statistical overview

## Tech Stack

### Backend
- FastAPI (Python web framework)
- MongoDB (Database)
- Redis (Caching)
- JWT (Authentication)

### Frontend
- HTML/CSS
- Jinja2 Templates

### Infrastructure
- Docker
- Docker Compose


## Installation Steps

1. Clone the repository
git clone <repository-url>

2. Create environment file (.env)
env
MONGODB_URL=mongodb://admin:password123@mongodb:27017
DB_NAME=credit_scoring_db
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

3. Build and run using Docker Compose
docker-compose up --build

4. Access the application
Frontend: http://localhost:8000

## API Documentation

### Authentication Endpoints
- `POST /auth/register`
  - Register new regular user
  - Body: `{email, full_name, password}`
  - Returns: User details

- `POST /auth/create-admin`
  - Create admin user
  - Body: `{email, full_name, password}`
  - Returns: Success message

- `POST /auth/token`
  - User login
  - Body: Form data `{username (email), password}`
  - Returns: JWT access token

- `GET /auth/me`
  - Get current user details
  - Auth: Required
  - Returns: User profile

### Loan Endpoints
- `POST /loans/apply`
  - Submit loan application
  - Auth: Required
  - Body: `{amount, purpose, duration_months}`
  - Returns: Created loan details

- `GET /loans/my-loans`
  - Get user's loan history
  - Auth: Required
  - Returns: List of user's loans

- `GET /loans/{loan_id}`
  - Get specific loan details
  - Auth: Required
  - Returns: Loan details

- `GET /loans/status-history/{loan_id}`
  - Get loan status history
  - Auth: Required
  - Returns: List of status changes

### Admin Endpoints
- `GET /admin/loans`
  - List all loans
  - Auth: Admin only
  - Query params: status (optional)
  - Returns: List of all loans

- `PATCH /admin/loans/{loan_id}/review`
  - Review loan application
  - Auth: Admin only
  - Body: `{status, notes}`
  - Returns: Updated loan

- `POST /admin/loans/{loan_id}/calculate-score`
  - Calculate credit score
  - Auth: Admin only
  - Returns: Updated loan with score

- `GET /admin/loans/{loan_id}/score-details`
  - Get detailed credit score breakdown
  - Auth: Admin only
  - Returns: Score components and details

- `GET /admin/stats`
  - Get loan statistics
  - Auth: Admin only
  - Returns: Overall loan stats

## Database Schema

### Users Collection
{
    "_id": ObjectId,
    "email": String (unique),
    "full_name": String,
    "hashed_password": String,
    "created_at": DateTime,
    "is_active": Boolean,
    "is_admin": Boolean
}

### Loans Collection
{
    "_id": ObjectId,
    "user_email": String,
    "amount": Float,
    "purpose": String,
    "duration_months": Integer,
    "status": Enum["pending", "in_review", "approved", "rejected"],
    "credit_score": Float,
    "created_at": DateTime,
    "updated_at": DateTime,
    "status_history": [
        {
            "status": String,
            "changed_at": DateTime,
            "changed_by": String,
            "notes": String
        }
    ]
}

### Indexes
The following indexes are automatically created for optimization:

// Users Collection
{ "email": 1 } (unique)

// Loans Collection
{ "email": 1 }
{ "status": 1 }
{ "email": 1, "status": 1 }

### Relationships
- One-to-Many relationship between Users and Loans (via user_email)
- Each Loan document contains its complete status history

### Data Types
- ObjectId: MongoDB's unique identifier
- String: Text fields
- Float: Decimal numbers (for amount and credit score)
- Integer: Whole numbers (for duration)
- DateTime: ISO format timestamps
- Boolean: True/False values
- Array: For status history
- Enum: Predefined status values

### Constraints
- User email must be unique
- Loan status must be one of: pending, in_review, approved, rejected
- Credit score is optional but must be between 0 and 100 when present
- All timestamps are in UTC

### Caching
Redis is used for caching with the following implementations:
- Admin loan listings are cached for 60 seconds
- User authentication tokens
- Statistical aggregations

## Security

### Authentication & Authorization
- JSON Web Token (JWT) based authentication
- Tokens expire after 30 minutes (configurable)
- Role-based access control (User/Admin)
- Password hashing using bcrypt with salt rounds

### API Security
- CORS (Cross-Origin Resource Sharing) protection
- Request validation using Pydantic models
- Input sanitization for all API endpoints
- Secure headers implementation

### Data Protection
- Encrypted database connections
- Environment variables for sensitive configuration
- Secure session handling
- MongoDB security features:
  - Authentication required
  - Role-based access control

### Infrastructure Security
- Docker containers with minimal base images
- Redis password protection
- Network isolation using Docker Compose

### Secure Development Practices
- Dependencies regularly updated
- SQL injection prevention (using MongoDB)

### API Endpoint Protection
- All sensitive endpoints require authentication
- Admin endpoints require admin role
- Request size limitations
- Validation of all input parameters

## Frontend

### Overview
The frontend is built using HTML, CSS, with Jinja2 templating for server-side rendering. The application follows a responsive design pattern and provides different interfaces for users and administrators.

### Templates Structure
- base.html: Base template with common layout and navigation
- login.html: User authentication page
- register.html: New user registration
- dashboard.html: User's main dashboard
- admin_dashboard.html: Administrator interface
- loan_application.html: Loan application form
- loan_details.html: Detailed loan view

### Features
1. User Interface
   - Responsive dashboard with loan statistics
   - Interactive loan application form
   - Loan history visualization

2. Admin Interface
   - Comprehensive loan management dashboard
   - Statistical overview with charts
   - Loan review system
   - Credit score calculation interface

### Styling
- Custom CSS with responsive design
- Status-based color coding
- Interactive elements and animations
- Consistent theme across pages

### User Experience
- Intuitive navigation
- Clear error messages
- Responsive feedback
- Accessible design

### Integration Points
- RESTful API consumption
- Authentication flow