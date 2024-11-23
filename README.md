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


### Serializers
Django Rest Framework serializers are used for converting model instances into JSON format and vice versa.

- **AnswerSerializer**: Serializes answer data for CRUD operations.
- **QuestionSerializer**: Serializes question data for CRUD operations.
- **QuizSerializer**: Serializes quiz data for CRUD operations.
- **InputSerializer**: Serializes input data for quiz generating.
- **AnswerCheckerSerializer**: Serializes input data for checking answers.
- **UserAnswerCheckerSerializer**: Serializes output data for checking and creating answers.
- **RegistrationSerializer**: Serializes input data for user registration.
- **UserAnswerSerializer/UserQuestionSerializer/UserQuizSerializer**: Serializes data for personal account viewset.
- **QuizForCreatorSerializer**: Serializes data for quiz creator viewset.
- **CreatedQuizeDeatilSerializer**: Serializes data for quiz creator detail viewset.


### ViewSets
Django Rest Framework viewsets are used for handling CRUD operations for models.

- **QuizViewSet**: Generates Quiz and handles CRUD operations.
- **AnswerCheckerViewSet**: Checks answers with AI and creates UserAnswer objects.
- **CreateUserViewSet**: Registers a new user.
- **TakenQuizViewSet**: Lists all quizzes user took.
- **CreatedQuizViewSet**: Lists all quizzes user created with statistics.


### Permissions
- **IsCreater**: Custom permission for checking if the user is the creator of the quiz.
- **IsThisUser**: Custom permission for checking if the user is the owner of the account.


### URLs
The URLs are routed through Django’s URL dispatcher and include versioning for better API management.

- `api/`: Base URL for API.
- `accounts/`: Base URL for user authentication.
- `/`: Swagger API documentation.


## Installation
To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/hella753/ai_quiz_generator.git
   cd ai_quiz_generator
   ```
   
2. Create a virtual environment and install dependencies:
   ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
   
3. Apply migrations:
    ```bash
    python manage.py migrate
    ```
   
4. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
   
5. Run the development server:
    ```bash
    python manage.py runserver
    ```
