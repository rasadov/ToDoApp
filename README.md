# FastAPI Task Management API

A RESTful API built with FastAPI for managing users (authentication) and their tasks. This project utilizes JWT for authentication and includes CRUD operations for tasks.

## Features

* **User Management:**
    * User Registration (`/user/register`)
    * User Login (`/user/login`) generating Access and Refresh tokens (Refresh token stored in HttpOnly cookie).
    * Token Refresh (`/user/refresh`) using the Refresh token cookie.
    * User Logout (`/user/logout`) clearing the Refresh token cookie.
* **Task Management:**
    * Create Tasks (`/tasks/create`)
    * Get Task by ID (`/tasks/{task_id}`)
    * List Tasks (`/tasks/list`) with pagination and optional status filtering.
    * Get My Tasks (`/tasks/users/me`).
    * List Tasks for a specific user (`/tasks/user/{user_id}`) with pagination.
    * Update Tasks (`/tasks/update`) (User can only update their own tasks).
    * Delete Tasks (`/tasks/{task_id}`) (User can only delete their own tasks).
* **Authentication:** JWT-based using Access and Refresh tokens.
* **API Documentation:** Auto-generated interactive documentation (Swagger UI & ReDoc).
* **Database Migrations:** Alembic

## Technology Stack

* **Backend:** Python 3.11+
* **Framework:** FastAPI
* **Database:** PostgreSQL (interfaced via SQLAlchemy)
* **ORM:** SQLAlchemy
* **Migrations:** Alembic
* **Async Driver:** asyncpg (implied by SQLAlchemy async usage with PostgreSQL)
* **Validation:** Pydantic
* **Dependency Management:** pip
* **API Specification:** OpenAPI 3.1.0
* **Testing:** Pytest, pytest-asyncio, HTTPX (via TestClient)
* **Containerization:** Docker, Docker Compose
* **Web Server:** Uvicorn

## Prerequisites

* Docker ([Install Docker](https://docs.docker.com/get-docker/))
* Docker Compose ([Usually included with Docker Desktop](https://docs.docker.com/compose/install/))
* Git (for cloning)

## Setup and Running the Application

The following steps will guide you through setting up and running the application.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rasadov/ToDoApp.git
    cd ToDoApp
    ```

2.  **Environment Variables:**
    Create a `.env` file in the project's `src` directory (e.g., `ToDoApp/src/.env`). This file stores sensitive configuration and settings. Your application will use these variables to construct the database connection string and for other configurations. Copy the example below and replace placeholder values as needed.

    ```dotenv
    # JWT Settings
    SECRET_KEY=your_super_secret_key_for_jwt_signing # CHANGE THIS! Use a strong, random key
    ALGORITHM=HS256 # Algorithm for JWT signing
    ACCESS_TOKEN_EXPIRE_MINUTES=30 # Lifetime of access tokens
    REFRESH_TOKEN_EXPIRE_MINUTES=10080 # Lifetime of refresh tokens (e.g., 7 days)

    # PostgreSQL Credentials
    # These variables are used to connect to the PostgreSQL database.
    # POSTGRES_HOST should match the service name of your database container in docker-compose.yml
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=mydatabase
    POSTGRES_HOST=db
    POSTGRES_PORT=5432

    # Application Settings
    DEBUG=False # Set to True for more verbose logging in development
    ```
    **Note:**
    * The `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` values should correspond to the credentials configured for the PostgreSQL service in your `docker-compose.yml`.
    * `POSTGRES_HOST` is typically the service name of the PostgreSQL container (e.g., `db`) as defined in `docker-compose.yml`.


3.  **Build and Start Services:**
    This command builds the Docker images (if they don't exist or if `--build` is specified) and starts the FastAPI application and PostgreSQL database services in detached mode (`-d`).
    ```bash
    docker-compose up -d --build
    ```
    This step is necessary to have the database container running and the application container (with Alembic) ready before applying migrations.


4.  **Database Migrations (Alembic):**
    Once the services are running, apply database migrations using Alembic. The command should be run inside your FastAPI application container (referred to as `fastapi_app` here; adjust if your service name in `docker-compose.yml` is different).
    ```bash
    docker exec -it fastapi_app alembic upgrade head
    ```
    This command applies all pending migrations to bring the database schema to the latest version defined in your Alembic migration scripts.


5.  **Application is Running:**
    If the above steps were successful, the API should now be running and accessible.
    * **API URL:** `http://localhost:8000`

## Docker Management

### Stop Services
```bash
  docker-compose down
```

### Start Services
```bash
  docker-compose up -d
```

---

# API Endpoints Documentation

## Overview
This document provides instructions for verifying and testing API endpoints for the task management system.

* **User Authentication:**
    * `POST /user/register`: Create a new user.
    * `POST /user/login`: Log in, receive access token (body) and refresh token (cookie).
    * `POST /user/refresh`: Use refresh token cookie to get a new access token and refresh token.
    * `POST /user/logout`: Clear the refresh token cookie.
* **Task Management:**
    * `POST /tasks/create`: Create a new task.
    * `GET /tasks/list`: Get a paginated list of tasks, optionally filtered by status.
    * `GET /tasks/users/me`: Get a paginated list of tasks for the authenticated user.
    * `GET /tasks/user/{user_id}`: Get a paginated list of tasks for a specific user.
    * `GET /tasks/{task_id}`: Get details of a specific task.
    * `PUT /tasks/update`: Update an existing task.
    * `DELETE /tasks/{task_id}`: Delete a task.

*(Refer to the interactive `/docs` endpoint for detailed request/response schemas, parameters, and to try out the API.)*

## Base URL
Replace `{{baseURL}}` with your actual API base URL in all examples below. It should be `http://localhost:8000` if running locally with Docker.

```plaintext
{{baseURL}} = http://localhost:8000
```

## Authentication
Most endpoints require authentication. Include the access token in the Authorization header:
```
Authorization: Bearer {{access_token}}
```

---

## 👤 User Endpoints

### 1. Login
**POST** `{{baseURL}}/user/login`

Authenticate a user and receive an access token.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

---

### 2. Register
**POST** `{{baseURL}}/user/register`

Register a new user account.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "username": "newuser",
    "password": "securepassword123"
}
```

---

### 3. Refresh Token
**POST** `{{baseURL}}/user/refresh`

Refresh the authentication token.

**Headers:**
```
Authorization: Bearer {{access_token}}
```

---

### 4. Logout
**POST** `{{baseURL}}/user/logout`

Logout the current user.

**Headers:**
```
Authorization: Bearer {{access_token}}
```

---

## 📝 Task Endpoints

> **Note:** All task endpoints require authentication. Include the Authorization header with a valid access token.

### 1. List Tasks
**GET** `{{baseURL}}/tasks/list`

Retrieve a paginated list of tasks.

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `elements_per_page` (integer, optional, default: 10)
- `status` (string, optional): `"new"`, `"in_progress"`, or `"completed"`

**Example:**
```
GET /tasks/list?page=1&elements_per_page=20&status=new
```

---

### 2. Get User Tasks
**GET** `{{baseURL}}/tasks/user/{user_id}`

Retrieve tasks for a specific user.

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Path Parameters:**
- `user_id` (integer, required): The ID of the user

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `elements_per_page` (integer, optional, default: 10)
- `status` (string, optional): `"new"`, `"in_progress"`, or `"completed"`

**Example:**
```
GET /tasks/user/1?page=1&elements_per_page=10
```

---

### 3. Get My Tasks
**GET** `{{baseURL}}/tasks/users/me`
Retrieve tasks for the authenticated user.
**Headers:
```
Authorization: Bearer {{access_token}}
```

**Query Parameters:**
- `page` (integer, optional, default: 1)
- `elements_per_page` (integer, optional, default: 10)
- `status` (string, optional): `"new"`, `"in_progress"`, or `"completed"`

example:
```
GET /tasks/users/me?page=1&elements_per_page=10
```

### 4. Get Task by ID
**GET** `{{baseURL}}/tasks/{task_id}`

Retrieve a specific task by its ID.

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Path Parameters:**
- `task_id` (integer, required): The ID of the task

**Example:**
```
GET /tasks/123
```

---

### 5. Delete Task
**DELETE** `{{baseURL}}/tasks/{task_id}`

Delete a specific task.

**Headers:**
```
Authorization: Bearer {{access_token}}
```

**Path Parameters:**
- `task_id` (integer, required): The ID of the task to delete

**Example:**
```
DELETE /tasks/123
```

---

### 6. Create Task
**POST** `{{baseURL}}/tasks/create`

Create a new task.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Request Body:**
```json
{
    "title": "My New Task",
    "description": "Details about the new task.",
    "status": "new"
}
```

**Field Details:**
- `title` (string, required): Task title
- `description` (string, required): Task description
- `status` (string, optional, default: "new"): Task status (`"new"`, `"in_progress"`, `"completed"`)

---

### 7. Update Task
**PUT** `{{baseURL}}/tasks/update`

Update an existing task.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```

**Request Body:**
```json
{
    "id": 1,
    "title": "Updated Task Title",
    "description": "Updated description.",
    "status": "in_progress"
}
```

**Field Details:**
- `id` (integer, required): ID of the task to update
- `title` (string, optional): New task title
- `description` (string, optional): New task description
- `status` (string, optional): New task status (`"new"`, `"in_progress"`, `"completed"`)

---

## Possible Responses
| Status Code | Description |
|-------------| --- |
| 200         | OK (e.g., successful request) |
| 201         | Created (e.g., user registered, task created) |
| 400         | Bad Request (e.g., validation errors) |
| 401         | Unauthorized (e.g., missing or invalid token) |
| 404         | Not Found (e.g., user or task not found) |
| 422         | Unprocessable Entity (e.g., validation errors) |

## Task Status Values

- `"new"`: Newly created task
- `"in_progress"`: Task currently being worked on  
- `"completed"`: Finished task

## Running Tests

Tests are written using `pytest`.

1.  **Ensure Services are Running and Migrations Applied:**
    If not already running from the setup, start them and ensure migrations are up to date:
    ```bash
    docker-compose up -d
    # If you suspect migrations are not current:
    # docker exec -it fastapi_app alembic upgrade head
    ```

2.  **Execute Tests:**
    Run the tests inside the running application container (`fastapi_app` should match your application's service name in `docker-compose.yml`):
    ```bash
    docker exec fastapi_app pytest
    ```

    To see print statements (`-s`) and more detailed output (`-vv`):
    ```bash
    docker exec fastapi_app pytest -svv
    ```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Please make sure to update tests as appropriate.

## License
The project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License.