# FastAPI Task Management API

A RESTful API built with FastAPI for managing users (authentication) and their tasks. This project utilizes JWT for authentication and includes CRUD operations for tasks.

## Features

* **User Management:**
    * User Registration (`/user/register`)
    * User Login (`/user/login`) generating Access and Refresh tokens (Refresh token stored in HttpOnly cookie).
    * Token Refresh (`/user/refresh`) using the Refresh token cookie.
    * User Logout (`/user/logout`) clearing the Refresh token cookie.
* **Task Management:**
    * Create Tasks (`/tasks/create`) (Requires authentication)
    * Get Task by ID (`/tasks/{task_id}`)
    * List Tasks (`/tasks/list`) with pagination and optional status filtering.
    * List Tasks for a specific user (`/tasks/user/{user_id}`) with pagination.
    * Update Tasks (`/tasks/update`) (Requires authentication, user can only update their own tasks).
    * Delete Tasks (`/tasks/{task_id}`) (Requires authentication, user can only delete their own tasks).
* **Authentication:** JWT-based using Access and Refresh tokens.
* **API Documentation:** Auto-generated interactive documentation (Swagger UI & ReDoc).

## Technology Stack

* **Backend:** Python 3.11+
* **Framework:** FastAPI
* **Database:** PostgreSQL (interfaced via SQLAlchemy)
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

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rasadov/ToDoApp.git
    cd ToDoApp
    ```

2.  **Environment Variables:**
    Create a `.env` file in the project root directory. This file stores sensitive configuration and settings. Copy the example below and replace the placeholder values with your actual configuration.

    ```dotenv
    # Database Connection (adjust user, password, host, port, dbname as needed)
    # Ensure the host matches your docker-compose service name for the DB (e.g., 'db')
    DATABASE_URL=postgresql+asyncpg://user:password@db:5432/mydatabase

    # JWT Settings
    SECRET_KEY=your_super_secret_key_for_jwt_signing # CHANGE THIS! Use a strong, random key
    ALGORITHM=HS256 # Algorithm for JWT signing
    ACCESS_TOKEN_EXPIRE_MINUTES=30 # Lifetime of access tokens
    REFRESH_TOKEN_EXPIRE_MINUTES=10080 # Lifetime of refresh tokens (e.g., 7 days)

    # PostgreSQL Credentials (if using standard postgres image in docker-compose)
    # These should match the environment variables set for the db service
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_DB=mydatabase

    # Application Settings
    DEBUG=False # Set to True for more verbose logging in development
    ```

3.  **Build Docker Images (Optional if pulling pre-built):**
    ```bash
    docker-compose build
    ```

4.  **Database Migrations:**
    ```bash
    docker exec -it postgres_db psql -U <db_user> -d <db_name> 
    ```
    Run scripts from `migrations/` to set up the database schema in the ascending order (001_users.sql, 002_tasks.sql).

## Running the Application

1.  **Start Services:**
    ```bash
    docker-compose up -d
    ```
    This command starts the FastAPI application server and the PostgreSQL database in detached mode.

2.  **Access the API:**
    The API should now be running at `http://localhost:8000`.

## API Documentation

FastAPI automatically generates interactive API documentation. Once the application is running, you can access:

* **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
* **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

### Key Endpoints Overview:

* **User Authentication:**
    * `POST /user/register`: Create a new user.
    * `POST /user/login`: Log in, receive access token (body) and refresh token (cookie).
    * `POST /user/refresh`: Use refresh token cookie to get a new access token and refresh token.
    * `POST /user/logout`: Clear the refresh token cookie.
* **Task Management:**
    * `POST /tasks/create`: Create a new task (Requires authentication).
    * `GET /tasks/list`: Get a paginated list of tasks, optionally filtered by status.
    * `GET /tasks/user/{user_id}`: Get a paginated list of tasks for a specific user.
    * `GET /tasks/{task_id}`: Get details of a specific task.
    * `PUT /tasks/update`: Update an existing task (Requires authentication).
    * `DELETE /tasks/{task_id}`: Delete a task (Requires authentication).

*(Refer to the `/docs` endpoint for detailed request/response schemas and parameters.)*

## Running Tests

Tests are written using `pytest`.

1.  **Ensure Services are Running:**
    ```bash
    docker-compose up -d
    ```

2.  **Execute Tests:**
    Run the tests inside the running application container:
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
