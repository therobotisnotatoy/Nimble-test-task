# Nimble-test-task

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![License: MIT](
https://img.shields.io/github/languages/count/therobotisnotatoy/Nimble-test-task)](https://opensource.org/licenses/MIT) [![License: MIT](
https://img.shields.io/github/languages/top/therobotisnotatoy/Nimble-test-task)](https://opensource.org/licenses/MIT)[![License: MIT](https://img.shields.io/github/issues-pr-raw/therobotisnotatoy/Nimble-test-task)](https://opensource.org/licenses/MIT)

## Overview

This API provides a service to searching for contacts based on certain criteria. The contacts are stored in a PostgreSQL database, and the database is periodically updated with contacts from an external source, Nimble API, using a cron job.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
```
git clone git@github.com:therobotisnotatoy/Nimble-test-task.git
```

2. Change into the project directory:

```
cd Nimble-test-task
```

3. Install the dependencies:

```
pip install -r requirements.txt
```

## Usage
Please ensure that you have properly configured the required environment variables in both cases as described in the [Configuration](#configuration) section.

### Running with Python
To run the web application with Python, use the following command:
```
uvicorn app:app --host 0.0.0.0 --port 8000
```

This will start the FastAPI application, and you can access it at `http://localhost:8000` in your web browser.

### Running with Docker Compose
Make sure you have Docker Compose installed.

To run the web application with Docker Compose, use the following command:

```
docker-compose up
```
This will start the application along with the PostgreSQL database container. You can access the web application at `http://localhost:8000` in your web browser.

Brief instructions on how to use your project. How to run it, what commands to use, etc.

## API Documentation
### Endpoint
Search Contacts:
```
URL: /search

Method: GET
```
Description:

This endpoint allows searching for contacts based on the provided query and fields.

Query Parameters:

- query: The search query string. This parameter is required and must have a minimum length of 1 character.
- fields: Comma-separated fields to search within. If not provided, the search will be performed on all fields. Valid fields are: first_name, last_name, first name, last name, and email.

Request Example:
```
GET /search?query=john&fields=first_name,last_name
```

Response Example:
```
[
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com"
    },
    {
        "id": 2,
        "first_name": "John",
        "last_name": "Smith",
        "email": "john.smith@example.com"
    }
]
```

### Data Format

The API returns data in JSON format. Each contact in the response is represented as a JSON object with the following fields:

- id: The unique identifier of the contact.
- first_name: The first name of the contact.
- last_name: The last name of the contact.
- email: The email address of the contact.

### Periodic Update

The contacts in the database are periodically updated from the Nimble platform. This update is performed once a day using a cron job. The cron job fetches contacts from Nimble's API and updates the corresponding records in the database.

Warning:

This option only works when using docker-compose

### Documentation

This README serves as the documentation for the API, providing information about the endpoints, authentication, data format, and periodic update process.

### GitHub Repository

The source code for the API is available in the GitHub repository: https://github.com/therobotisnotatoy/Nimble-test-task.git

Please refer to the repository for the complete implementation of the API, including code, tests, and documentation.

## Configuration

Before running the application, make sure to add the following environment variables in .env file:

- `DB_HOST`: The hostname or IP address of the PostgreSQL database.
- `DB_PORT`: The port number of the PostgreSQL database.
- `DB_NAME`: The name of the PostgreSQL database.
- `DB_USER`: The username to access the PostgreSQL database.
- `DB_PASSWORD`: The password to access the PostgreSQL database.
- `DB_CONTAINER_NAME`: The name of the PostgreSQL container (e.g., tt_nimble_inc-db-1).
- `DB_SERVICE_NAME`: The name of the PostgreSQL service (e.g., db).
- `NIMBLE_API_KEY`: Your Nimble API key.
- `NIMBLE_API_URL`: The URL of the Nimble API.

Warning:
- When running the application outside of Docker Compose, it will use the DB_HOST environment variable to connect to the PostgreSQL database.
- When running the application with Docker Compose, it will use either the DB_CONTAINER_NAME or DB_SERVICE_NAME environment variable to connect to the PostgreSQL database.

## Testing
Running tests:
```
python -m unittest tests/test_name
```

## Contributing

Not expected

## License

This project is licensed under the MIT License - see the license file [link (TBC)](#License) for details.

---

[Home](#Nimble-test-task)
