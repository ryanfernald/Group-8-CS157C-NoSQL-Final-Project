CREATE DATABASE IF NOT EXISTS carrier_messenger;

USE carrier_messenger;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE messages (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  chat_id VARCHAR(255),
  sender_id INT,
  sender_name VARCHAR(100),
  message_text TEXT,
  timestamp DATETIME
);