# Carrier Messenger App

Building a Full Stack Messaging Application with React, Flask and a Redis NoSQL Database Cacheing Mechanism with MySQL as a Persistant Storage Solution

<img width="1150" alt="Screenshot 2025-05-06 at 1 54 47 PM" src="https://github.com/user-attachments/assets/1482fcf3-015a-4a42-87ed-1cbd4fb7c5cb" />

---

## 📚 Table of Contents

- [Carrier Messenger App](#carrier-messenger-app)
  - [📚 Table of Contents](#-table-of-contents)
- [About the Project](#about-the-project)
- [The React App](#the-react-app)
  - [Login / Signup Page](#login--signup-page)
  - [Sending Messages](#sending-messages)
  - [Starting a New Chat or a Group Chat](#starting-a-new-chat-or-a-group-chat)
  - [Updating the User Profile](#updating-the-user-profile)
- [Redis Data Model](#redis-data-model)
- [MySQL Persistent Storage Data Model](#mysql-persistent-storage-data-model)
- [About Us](#about-us)

---

# About the Project

Carrier Messenger is a lightweight real-time messaging application designed to explore the integration of modern web technologies with both in-memory and persistent data storage systems. The frontend is built using React, providing a responsive and modular user interface. A Flask-based middle layer serves as the API gateway, handling client-server communication and coordinating data flows between the application and its databases. Message data is initially handled through Redis, a NoSQL in-memory data store, allowing for low-latency communication and temporary session management. After a defined lifecycle, messages and user data are asynchronously flushed to MySQL, which functions as the system’s long-term, relational data store. This architecture demonstrates the separation of volatile and persistent storage responsibilities, and highlights Redis’s value as a performance-oriented caching layer in hybrid database environments.

<img width="1136" alt="Screenshot 2025-05-06 at 2 36 06 PM" src="https://github.com/user-attachments/assets/ea246c3c-4770-420c-b88f-1eae9409ed99" />


---

# The React App

The frontend of the Carrier Messenger project is built using React, allowing for modular component design and dynamic client-side rendering. It consists of two primary views: a login/signup landing page and a post-authentication messaging dashboard.

## Login / Signup Page

The landing page presents users with the option to either sign in or create a new account. Upon submitting the signup form, user credentials are temporarily stored in Redis for fast access and validation, and later persisted to MySQL. Successful login triggers the creation of a session token stored in Redis, allowing authenticated access to the messaging dashboard.

<img width="1483" alt="Screenshot 2025-05-06 at 3 07 42 PM" src="https://github.com/user-attachments/assets/215f437e-9314-47e3-9095-897c00955e32" />

<p align="center">
  <img width="761" alt="Screenshot 2025-05-06 at 3 08 12 PM" src="https://github.com/user-attachments/assets/500ed3fc-1041-4d41-adcd-7911c1692f07" />
</p>

---

## Sending Messages 

After authentication, users are directed to the messages page, where they can view existing conversations, start new one-on-one or group chats, and send real-time messages. The interface dynamically loads associated chats and messages from Redis, allowing for fast interactions. User settings, such as profile photo and username, can also be managed directly from this interface.

<img width="1111" alt="Screenshot 2025-05-06 at 3 10 54 PM" src="https://github.com/user-attachments/assets/89fd4e7e-d843-45a8-b705-b2e30a542e13" />


---

## Starting a New Chat or a Group Chat

Users can initiate a new chat by entering the username or email of another user. The application checks Redis to verify that the recipient exists and that a direct one-on-one chat does not already exist. If validation passes, a new message_token is created and stored in Redis as a hash, which includes the chat_id, a list of participant user IDs, and a timestamp indicating when the chat was created. Group chats are initiated by adding multiple users to the chat creation form. The resulting message_token reflects all participant IDs and follows a naming pattern such as chat_user1_user2_user3_####, allowing for dynamic group composition.

All chats in Redis are stored temporarily using **expiring tokens**. When a token expires—either through logout or a timed expiration—the associated chat is automatically **flushed** to MySQL via a background monitoring service. This ensures that long-term storage is preserved without requiring constant writes to disk. Conversely, when a user logs back in, their associated chats are **hydrated** from MySQL into Redis for immediate access, allowing the application to balance low-latency performance with durable storage. This mechanism showcases how Redis can serve as a transient but performant caching layer in tandem with a persistent relational backend.

<p align="center">
  <img width="460" alt="Screenshot 2025-05-06 at 3 11 31 PM" src="https://github.com/user-attachments/assets/32b9f581-25e7-4172-bf15-7add96dc1668" />
</p>

---

## Updating the User Profile

Users can update their profile information, including their username, password, and profile photo, from within the messaging interface. When a user edits their username, the system automatically detects changes and updates the value in both Redis and MySQL without modifying the user’s unique ID. This design ensures that existing chats and participant references remain valid, preserving the integrity of all message and chat associations. For password updates, the new password is hashed using SHA-256 encryption before being stored, ensuring that sensitive credentials are never saved in plain text. These updates take effect immediately, with Redis serving as a low-latency reflection of the user’s current state.

<p align="center">
  <img width="436" alt="Screenshot 2025-05-06 at 3 12 50 PM" src="https://github.com/user-attachments/assets/77d586fc-dd6b-4537-a700-cf48a36f313f" />
</p>

---

# Redis Data Model

Redis serves two main functions in this application. First, it manages user authentication tokens. When a user logs in, the system generates a unique token. This token is stored in Redis. The token's key maps to the user's ID. Redis automatically assigns an expiration time (TTL) to this token. For subsequent API requests, the system checks Redis for the token to validate the user's session. Second, Redis caches recent messages. New messages are written to Redis lists. This allows fast retrieval of the latest messages for active chats. A background process later moves these messages from Redis to the MySQL database for long-term storage. This approach enhances performance for common operations.

<img width="1083" alt="Screenshot 2025-05-06 at 3 18 19 PM" src="https://github.com/user-attachments/assets/f12a988f-6ebd-4dc1-bfb8-8fce8748490d" />

---

# MySQL Persistent Storage Data Model

The MySQL database serves as the primary persistent storage for the application. It stores essential data such as user accounts, chat session details, and the complete history of messages. Relationships between users, chats, and messages are also maintained within MySQL. The application uses SQLAlchemy as an Object Relational Mapper (ORM) to define data models and interact with the database. Flask-Migrate manages database schema changes over time. This setup ensures data durability and allows for structured querying of information. Figure 2 below, is the tabular representation of the data model as stored in MySQL for perpetual storage.

<img width="1030" alt="Screenshot 2025-05-06 at 3 15 11 PM" src="https://github.com/user-attachments/assets/6d033488-acb3-409f-804f-087d7854811f" />

---


# About Us

<p align="center">
  <img width="763" alt="Screenshot 2025-05-06 at 2 50 25 PM" src="https://github.com/user-attachments/assets/5c5a7767-572d-4e33-87d8-b73662a20456" />
</p>
  
<p align="center">
  <a href="https://www.linkedin.com/in/ryan-fernald/">Ryan Fernald LinkedIn</a> |
  <a href="https://github.com/ryanfernald">Ryan Fernald GitHub</a> |
  <a href="https://www.linkedin.com/in/aldridge-fonseca/">Aldridge Fonseca LinkedIn</a> |
  <a href="https://github.com/aldridge-fonseca">Aldridge Fonseca GitHub</a>
</p>
