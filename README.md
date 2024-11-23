# AI Quiz Generator
Backend API built with **Django**, for AI Quiz Generator. Provides endpoints to handle Quiz Generating, 
Quiz Correcting and Authorization. Excellent Tool for Teachers and Students to Develop their skills and make studying easier.
## Table of Contents

- [Features](#features)
- [Endpoints](#endpoints)
  - [User Authentication](#user-authentication)
  - [Quiz Generating](#quiz-generating)
  - [Quiz Correcting](#quiz-correcting)
  - [Personal Accounts](#personal-accounts)
- [Components](#components)
  - [Models](#models)
  - [Serializers](#serializers)
  - [Views](#views)
  - [Permissions](#permissions)
  - [URLs](#urls)
- [Installation](#installation)
- [Configuration](#configuration)
- [License](#license)


## Features
- **User Authentication**: User registration, login, and authentication via JWT. Unauthorized users are represented as Guests.
- **Quiz Generating**: Endpoints for Quiz Generating(with subject or via uploaded file), Editing, Destroying, Listing and Retrieving.
- **Quiz Correcting**: Endpoint for Checking Answers of the users with AI and explaining correct answers in detail.
- **Permissions & Security**: Custom permissions and exceptions for ensuring data privacy and security.
- **Middleware**: Middleware for handling Guest sessions.
- **Email Sending**: Handles Message Sending to registered users and creators.
- **Managers**: Provides some basic statistics for the users.
- **Internationalization and localization**: Supports two languages - English/Georgian. (not yet)
- **Pagination**: Pagination support for large datasets. (not yet)


## Endpoints
### User Authentication
- `POST /accounts/create-user`: Registers a new user.
- `GET /accounts/`: Listing of all the users if authenticated.
- `POST /api/token/`: Provides a JWT token.
- `POST /api/token/refresh/`: Provides refresh JWT token.
### Quiz Generating
- `GET /api/quiz/`: Lists all quizzes if authenticated.
- `POST /api/quiz/`: Creates a new quiz (authenticated only).
- `GET /api/quiz/{id}/`: Retrieves questions and answers of a specific quiz.
- `PUT /api/quiz/{id}/`: Updates an existing quiz (creator only).
- `DELETE /api/quiz/{id}/`: Deletes a specific quiz (creator only).
### Quiz Correcting
- `POST /api/quiz/`: Checks answers with AI and creates UserAnswer objects. Returns JSON with questions, answers and explanation.

### Personal Accounts
- `GET /accounts/taken-quiz/{username}/`: Lists all quizzes user took (Himself Only).
- `GET /accounts/created-quiz/`: Lists all quizzes user created. 
- `GET /accounts/created-quiz/{id}/`: Retrieves the specific quiz and displays basic statistics.

## Components

### Models
The backend uses Django ORM to define models representing entities like `User`, `UserAnswer`. `Answer`, `Quiz`, `Question`.

- **User**: Extended user model with custom fields and authentication methods.
- **Answer**: Contains fields: `answer`, `correct`, `question(fk)`
- **UserAnswer**: Contains fields: `answer`, `correct`, `question(fk)`, `user(fk)`, `guest`, `explanation` also method `get_score()`
- **Question**: Contains fields: `question`, `score`, `quiz(fk)`
- **Quiz**: Contains fields: `name`, `creator(fk)`
- **ModifiedTimeModel**: Abstract for adding creation and modification times.
