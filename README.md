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

## Verifying Endpoints

You can verify that the API is working through several methods:

1.  **API Documentation (Swagger UI / ReDoc):**
    FastAPI automatically generates interactive API documentation. This is the easiest way to explore and test endpoints.
    * **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs) - Allows you to interact with the API endpoints directly in your browser.
    * **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc) - Provides alternative documentation.

2.  **Using `curl` (or any API client like Postman):**
    You can send requests to the API endpoints using a command-line tool like `curl` or a GUI tool like Postman.

    * **Example: Check the health of the docs endpoint:**
        ```bash
        curl http://localhost:8000/docs
        ```
        You should receive an HTML response.

    * **Example: List tasks (assuming it's a public endpoint or after authentication):**
        ```bash
        curl http://localhost:8000/tasks/list
        ```
        Or, for an endpoint requiring authentication, you would first register/login via `/docs` or your API client to get a token, then include it in your request.

    * **Example: Register a new user (refer to `/docs` for the exact request body):**
        ```bash
        curl -X POST "http://localhost:8000/user/register" \
             -H "Content-Type: application/json" \
             -d '{"email": "user@example.com", "password": "yourpassword"}'
        ```

### Managing Services

* **To stop the services:**
    ```bash
    docker-compose down
    ```
* **To start the services again (without rebuilding):**
    ```bash
    docker-compose up -d
    ```

## API Endpoints Overview

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

*(Refer to the interactive `/docs` endpoint for detailed request/response schemas, parameters, and to try out the API.)*

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