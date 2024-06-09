# AccuApp API

AccuApp is a social networking application API built using Django Rest Framework. It provides various functionalities for user management and interaction.

## Installation

1. Clone the repository:
    git clone https://github.com/anigam075/AccuKnox-Social-Networking-App

2. Install the required dependencies:
    pip install -r requirements.txt

3. Apply database migrations:
    python manage.py migrate

4. Create a superuser for accessing the admin panel:
    python manage.py createsuperuser

5. Run the development server:
    python manage.py runserver

## Endpoints

### User Management

- **Signup:** `POST /api/signup/`
  - Create a new user account.
  - Required fields: `first_name`, `last_name`, `email`, `password`.

- **Login:** `POST /api/login/`
  - Authenticate and generate a token for the user.
  - Required fields: `email`, `password`.

### Friends

- **Search Users:** `GET /api/search/?query=<search-query>`
  - Search for other users by email or name.

- **Send Friend Request:** `POST /api/friend-request/`
  - Send a friend request to another user.
  - Required fields: `email` (email of the user to send request).

- **Respond to Friend Request:** `POST /api/friend-request/respond/`
  - Respond to a friend request.
  - Required fields: `to_user` (email of the user who sent the request), `action` (accept or reject).

- **List Friends:** `GET /api/friends/`
  - List all accepted friend requests.

- **List Pending Requests:** `GET /api/pending-requests/`
  - List all pending friend requests received.

## Authentication

Token-based authentication is used for accessing the protected endpoints. After logging in, include the token in the Authorization header of subsequent requests:
    Authorization: Token <user-token>

