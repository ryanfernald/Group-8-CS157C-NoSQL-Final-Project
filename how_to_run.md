# How to Run Carrier Messenger

Follow these steps to get the Carrier Messenger application running locally.

---

## 1. Prerequisites

- **Redis** server running on port **6379**
- **MySQL** server running on port **3306**
- **Python 3.10+**
- **Node.js** and **npm** (for the frontend)
- **Vite** (will be installed with npm dependencies)

---

## 2. Install Python Dependencies

From the project root directory, install all required Python packages:

```sh
pip install -r requirements.txt
```

---

## 3. Start the Flask (Middle Layer) Server

1. Open a terminal.
2. Navigate to the middle layer directory:

   ```sh
   cd carrier-messenger-app/middle_layer
   ```

3. Run the Flask server:

   ```sh
   python app.py
   ```

---

## 4. Start the React Frontend

1. Open a **new terminal** window.
2. Navigate to the frontend directory:

   ```sh
   cd carrier-messenger-app/frontend
   ```

3. Install frontend dependencies:

   ```sh
   npm install
   ```

4. Start the Vite development server:

   ```sh
   npm run dev
   ```

   The app will be available at [http://localhost:5173](http://localhost:5173).

---

## 5. Access the Application

- Visit [http://localhost:5173](http://localhost:5173) in your browser.
- Log in or sign up to start using Carrier Messenger.

---

## Troubleshooting

- Ensure **Redis** and **MySQL** are running and accessible on their default ports. Meaning Redis should be running on port 6379, and MySQL on Port 3306
- If you encounter issues, check the terminal output for errors and verify all dependencies are installed.

---

# How to Run Containerized Backend

## Prerequisites
* Docker Desktop installed and running.

## Setup & Run

1.  **Navigate to Backend Directory:**
    Open a terminal and go to the `ContainerizedBackend` folder.
    ```bash
    cd path/to/GROUP-8-CS157C-NoSQL-Final-Project/carrier-messenger-app/ContainerizedBackend
    ```

2.  **Configure Environment:**
    * Copy `.env.example` to `.env`.
        ```bash
        # Windows (PowerShell)
        Copy-Item .env.example .env
        # macOS/Linux
        cp .env.example .env
        ```
    * Edit `.env` with your database credentials and Flask `SECRET_KEY`.

3.  **Start Services:**
    ```bash
    docker-compose up --build -d
    ```

4.  **Apply Database Migrations (First time / Model changes):**
    ```bash
    docker-compose exec flask_app flask db upgrade
    ```

## Access
* **API:** `http://localhost:5000`

## Logs & Stopping
* **View Logs:** `docker-compose logs -f flask_app`
* **Stop Services:** `docker-compose down`