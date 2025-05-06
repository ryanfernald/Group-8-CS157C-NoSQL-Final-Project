# Chat API Documentation

This document provides details on how to interact with the Chat API backend.

**Base URL:** `http://localhost:5000` (or your deployed URL)

---

## Authentication

Most endpoints require authentication via a Bearer Token obtained through the login process.

**How to Authenticate:**

1.  Log in using the `POST /auth/login` endpoint to receive a token.
2.  For subsequent requests to protected endpoints, include an `Authorization` header with the value `Bearer <your_token>`, replacing `<your_token>` with the actual token received.

**Example Header:**
`Authorization: Bearer abc123def456...`

---

## Auth Endpoints

These endpoints handle user registration and login.

### 1. Register User

* **Method:** `POST`
* **Path:** `/auth/register`
* **Description:** Creates a new user account.
* **Authentication:** Not required.
* **Request Body (JSON):**
    ```json
    {
        "username": "newuser",
        "email": "new@example.com",
        "password": "strongpassword"
    }
    ```
* **Success Response (201 Created):**
    ```json
    {
        "message": "User registered successfully",
        "user": {
            "user_id": 11,
            "username": "newuser",
            "email": "new@example.com",
            "created_at": "2025-05-06T12:00:00Z"
        }
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Missing fields, empty fields.
        ```json
        { "error": "Missing username, email, or password in request body" }
        ```
    * `409 Conflict`: Username or email already exists.
        ```json
        { "error": "Username already exists" }
        ```json
        { "error": "Email already exists" }
        ```
    * `500 Internal Server Error`: Database error during commit.

### 2. Login User

* **Method:** `POST`
* **Path:** `/auth/login`
* **Description:** Authenticates a user and returns an access token.
* **Authentication:** Not required.
* **Request Body (JSON):**
    ```json
    {
        "username": "newuser",
        "password": "strongpassword"
    }
    ```
* **Success Response (200 OK):**
    ```json
    {
        "message": "Login successful",
        "token": "a_long_hex_token_string_generated_by_uuid..."
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Missing or empty fields.
        ```json
        { "error": "Missing username or password in request body" }
        ```
    * `401 Unauthorized`: Invalid username or password.
        ```json
        { "error": "Invalid username or password" }
        ```
    * `503 Service Unavailable`: Redis connection error during token storage.
        ```json
        { "error": "Authentication service temporarily unavailable (Redis connection)." }
        ```
    * `500 Internal Server Error`: Other unexpected errors.

---

## Chat Endpoints

These endpoints manage chat sessions.

### 1. Create Chat

* **Method:** `POST`
* **Path:** `/chats`
* **Description:** Creates a new one-on-one or group chat.
* **Authentication:** **Required** (Bearer Token).
* **Request Body (JSON):**
    ```json
    {
        "participant_ids": [2, 5], // List of user IDs *other* than the creator
        "is_group": true,          // boolean: true for group, false for 1-on-1
        "chat_name": "Project Alpha" // Required if is_group is true, ignored otherwise
    }
    ```
    * For a 1-on-1 chat, `participant_ids` should contain exactly one ID.
* **Success Response (201 Created):**
    ```json
    {
        "message": "Chat created successfully",
        "chat": {
            "chat_id": 9,
            "is_group_chat": true,
            "chat_name": "Project Alpha",
            "created_at": "2025-05-06T12:05:00Z"
            // Members list not included in create response currently
        }
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Missing fields, invalid data types (e.g., non-integer IDs), creating 1-on-1 with self, wrong number of participants for 1-on-1, missing group name.
    * `401 Unauthorized`: Invalid or missing token.
    * `404 Not Found`: One or more specified participant IDs do not exist.
    * `500 Internal Server Error`: Database error during creation.

### 2. List User's Chats

* **Method:** `GET`
* **Path:** `/chats`
* **Description:** Retrieves a list of all chats the authenticated user is a member of.
* **Authentication:** **Required** (Bearer Token).
* **Request Body:** None.
* **Success Response (200 OK):**
    ```json
    {
        "chats": [
            {
                "chat_id": 1,
                "is_group_chat": false,
                "chat_name": "otheruser", // Other user's username for 1-on-1
                "members": [
                    {"user_id": 1, "username": "me"},
                    {"user_id": 2, "username": "otheruser"}
                ]
            },
            {
                "chat_id": 9,
                "is_group_chat": true,
                "chat_name": "Project Alpha",
                "members": [
                    {"user_id": 1, "username": "me"},
                    {"user_id": 2, "username": "otheruser"},
                    {"user_id": 5, "username": "userfive"}
                ]
            }
            // ... more chats
        ]
    }
    ```
* **Error Responses:**
    * `401 Unauthorized`: Invalid or missing token.
    * `500 Internal Server Error`: Database error during retrieval.

---

## Message Endpoints

These endpoints handle sending and retrieving messages within a specific chat.

### 1. Send Message

* **Method:** `POST`
* **Path:** `/chats/<int:chat_id>/messages`
* **Description:** Sends a message to the specified chat. Message is written to the Redis cache.
* **Authentication:** **Required** (Bearer Token).
* **Path Parameter:**
    * `chat_id` (integer): The ID of the chat to send the message to.
* **Request Body (JSON):**
    ```json
    {
        "content": "This is my message!"
    }
    ```
* **Success Response (201 Created):**
    ```json
    {
        "message": "Message sent successfully",
        "message_data": {
            "sender_id": 1,
            "content": "This is my message!",
            "created_at": "2025-05-06T12:10:00Z"
        }
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Missing or empty `content`.
    * `401 Unauthorized`: Invalid or missing token.
    * `403 Forbidden`: Authenticated user is not a member of the specified `chat_id`.
    * `503 Service Unavailable`: Redis connection error.
    * `500 Internal Server Error`: Other unexpected errors.

### 2. Get Messages

* **Method:** `GET`
* **Path:** `/chats/<int:chat_id>/messages`
* **Description:** Retrieves messages for the specified chat. Fetches recent messages from Redis cache unless `before_timestamp` is provided, in which case it fetches older messages from MySQL.
* **Authentication:** **Required** (Bearer Token).
* **Path Parameter:**
    * `chat_id` (integer): The ID of the chat to retrieve messages from.
* **Query Parameters (Optional):**
    * `limit` (integer): Maximum number of messages to return (Default: 50). Must be positive.
    * `before_timestamp` (string): ISO 8601 formatted timestamp (e.g., `2025-05-06T12:10:00Z`). If provided, retrieves messages created *before* this time from MySQL. If omitted, retrieves the most recent messages from Redis.
* **Request Body:** None.
* **Success Response (200 OK):**
    ```json
    {
        "messages": [
            {
                "message_id": 123, // Only present for messages fetched from MySQL
                "sender_id": 2,
                "content": "An older message",
                "created_at": "2025-05-06T11:59:59Z"
            },
            {
                // "message_id" might be absent for messages from Redis cache
                "sender_id": 1,
                "content": "A more recent message",
                "created_at": "2025-05-06T12:05:30Z"
            }
            // ... more messages (ordered newest-first within the fetched batch)
        ]
    }
    ```
* **Error Responses:**
    * `400 Bad Request`: Invalid `limit` or `before_timestamp` format.
    * `401 Unauthorized`: Invalid or missing token.
    * `403 Forbidden`: Authenticated user is not a member of the specified `chat_id`.
    * `503 Service Unavailable`: Redis connection error (when fetching recent).
    * `500 Internal Server Error`: Database error (when fetching older) or other unexpected errors.

---