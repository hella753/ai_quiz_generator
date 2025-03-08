# AI Quiz Generator
Backend API built with **Django Rest Framework**, for AI Quiz Generator which uses openAI api. Provides endpoints to handle Quiz Generating, 
Quiz Correcting and Authorization. Has additional features like email sending, working with files, exporting to worksheet quiz and basic statistics for users
Excellent Tool for Teachers and Students to Develop their skills and make studying easier.

![Logo](/logo.png)


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
  - [Viewsets and Views](#viewsets-and-views)
  - [Permissions](#permissions)
  - [URLs](#urls)
- [Services](#services) 
  - [Email Sending](#email-sending)
  - [AI Integration](#ai-integration)
  - [File Handling](#file-handling)
  - [Managers](#managers)
  - [Statistics](#statistics)
- [Installation](#installation)
- [Credits](#Credits)


## Features
- **User Authentication**: User registration, login, and authentication via JWT. Unauthorized users are represented as Guests.
- **Quiz Generating**: Endpoints for Quiz Generating (with a subject or via uploaded file), Editing, Destroying, Listing and Retrieving.
- **Quiz Correcting**: Endpoint for Checking Answers of the users with AI and explaining correct answers in detail.
- **Personal Accounts**: Endpoints for Listing all quizzes user took, Listing all quizzes user created, Retrieving specific quiz and displaying basic statistics.
- **AI Integration**: Uses OpenAI API for checking answers and providing explanations.
- **File Handling**: Handles file uploading and exporting to worksheet quiz.
- **Permissions & Security**: Custom permissions and exceptions for ensuring data privacy and security.
- **Email Sending**: Handles Message Sending to registered users and creators.
- **Managers**: Provides some basic statistics for the users.
- **Multiple Language Support**.
- **Pagination**: Pagination support for large datasets. 


## Endpoints
### User Authentication
- `POST /accounts/create-user`: Registers a new user.
- `POST /api/token/`: Provides a JWT token.
- `POST /api/token/refresh/`: Provides refresh JWT token.
- `PUT /change-password/`: Changes user password.
- `POST /forgot-password/request/`: Sends an email with a link to reset the password.
- `POST /forgot-password/reset/<uuid:token>/`: Resets the user password.
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
- **QuizScore**: Contains fields: `score`, `user(fk)`, `quiz(fk)`, `guest`
- **ModifiedTimeModel**: Abstract for adding creation and modification times.


### Serializers
Django Rest Framework serializers are used for converting model instances into JSON format and vice versa.

- **User app**: Contains serializers for User Creation, User Password Change, User Password Reset, Quiz Score and Analysis.
- **Quiz app**: Contains serializers for Quiz Creation, Quiz Update, Quiz Retrieve and Listing, Answer Checking, UserAnswer Creation.

### ViewSets and Views
Django Rest Framework Views and ViewSets are used for handling CRUD operations for models.

- **QuizViewSet**: Generates Quiz with AI and handles CRUD operations with the help of `QuizCreator` and `QuizUpdater`.
- **AnswerCheckerViewSet**: Checks answers with AI and creates UserAnswer objects with Total Score.
- **CreateUserViewSet**: Registers a new user.
- **TakenQuizViewSet**: Lists all quizzes user took.
- **CreatedQuizViewSet**: Lists all quizzes users created with statistics.
- **ChangePasswordView**: Changes user password.
- **RequestPasswordResetView**: Sends an email with a link to reset the password.
- **ResetPasswordView**: Resets the user password.


### Permissions
- **IsCreator**: Custom permission for checking if the user is the creator of the quiz.
- **IsThisUser**: Custom permission for checking if the user is the owner of the account.
- **CanSeeAnalysis**: Custom permission for safe methods, checking if the user is the owner of the account.


### URLs
The URLs are routed through Django’s URL dispatcher.
- `api/`: Base URL for API.
- `accounts/`: Base URL for user authentication.
- `/`: Swagger API documentation.


## Services

### Email Sending
- Send an email with a link to reset the password
- Email the creator of the quiz if the user takes the quiz.
- Verify the email address of the user during registration.

### AI Integration
- `QuizGenerationService`, `QuizSubmissionCheckerService`, `QuizDataProcessor` in `services.py` and `QuizGenerator` 
in `ai_generator.py` are responsible for handling AI integration with the OpenAI API with the help of pydantic.

### File Handling
- `FileProcessor` in `file_processor.py` is responsible for handling file uploading.
- `ExportToWorksheet` in `worksheet.py` is responsible for exporting the quiz to a worksheet.

### Managers
- `QuizManager` in `managers.py` is responsible for providing basic statistics for the users.
- `UserAnswerManager` in `managers.py` is responsible for providing basic statistics for the users.

### Statistics
- `QuizRetrievalService` and `QuizAnalyticsService` are responsible for providing basic statistics for the user creators. Which include:
  - What percentage of the users answered the question correctly or incorrectly.
  - What are the most challenging questions for the users?
  - Users who took the quiz with their scores and answers.

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

4. Environment  Variables: 
    - Create a `.env` file in the root directory and add the following variables:
    ```bash
    OPEN_AI_SECRET_KEY
    EMAIL_KEY
    WKHTMLTOPDF_PATH
    CELERY_BROKER_URL
    DJANGO_SECRET_KEY
   ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```
   
6. Run the development server:
    ```bash
    python manage.py runserver
    ```

7. Run Celery:
    ```bash
    celery -A ai_quiz_generator worker --loglevel=info --pool=solo
    ```

## Credits
- **[Collaborator GigaDarchia](https://github.com/GigaDarchia)**
- **[Collaborator Gogeishvili](https://github.com/Gogeishvili)**

Collaborated on building and maintaining the backend infrastructure. <br>
Special thanks to all contributors who helped make this project possible!
