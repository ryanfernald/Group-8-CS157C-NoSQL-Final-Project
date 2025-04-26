CREATE DATABASE IF NOT EXISTS carrier_messenger;

USE carrier_messenger;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_username VARCHAR(255),
    receiver_username VARCHAR(255),
    message_content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);