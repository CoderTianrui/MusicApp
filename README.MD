# MusicFlow Platform

## Overview

MusicFlow is a music management and playback platform designed to offer a seamless experience for users to discover, listen to, and organize music. Users can create playlists, explore albums, and manage their music collection. The platform also includes an admin interface for managing tracks, artists, albums, and genres.

## Installation Guide

### 1. Backend Setup

To get started with the backend, follow these steps:

1. **Install Python 3.12.7**  
   Ensure you have Python 3.12.7 installed. You can download it from the [official Python website](https://www.python.org/downloads/). Verify the installation by running:
   ```bash
   python --version
   ```

2. **Initialize a Virtual Environment (Optional but Recommended)**
    In the backend directory, set up a virtual environment to isolate project dependencies:
   ```bash
   python -m venv env
   ```

3. **Create a PowerShell Script for Easy Virtual Environment Activation (Optional)**
    reate a script named env.ps1 in the backend directory with the following content:
    ```bash
    ./env/Scripts/Activate.ps1
    ```

4. **Activate the Virtual Environment**
    Run the following command to activate the virtual environment:
    ```bash
    ./env.ps1
    ```

5. **Install Dependencies**
    Install all required Python packages by running:
    ```bash
    pip install -r requirements.txt
    ```

6. **Run the Django Development Server**
    Start the backend server by running:
    ```bash
    python manage.py runserver
    ```

### 2. Frontend Setup

To get the frontend server running:

1. **Install Dependencies**
    Navigate to the frontend directory and install all required packages:
    ```bash
    npm install
    ```
    
2. **Start the Vite Development Server**
    After the dependencies are installed, start the frontend server:
    ```bash
    npm run dev
    ```

3. **Access the Frontend**  
   The frontend will now be accessible at http://localhost:5173.

By following these steps, both the backend (Django) and frontend (Vite) development servers will be running, enabling local development.

### 3. Settings Configuration

#### 3.1 CORS and CSRF Setup
To enable secure communication between the frontend and backend, certain configurations need to be made in the Django `settings.py` file for Cross-Origin Resource Sharing (CORS) and Cross-Site Request Forgery (CSRF) protection.

1. **CORS Configuration**
    Add the frontend server's address to the `CORS_ALLOWED_ORIGINS` list in `backend/myproject/settings.py`. This ensures the backend can accept requests from the frontend.
    ```python
    CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Frontend Vite server address
    "http://your-frontend-address.com",  # Replace with your actual frontend address
    ]
    ```

1. **CSRF Configuration**
    Add the frontend server's address to the `CSRF_TRUSTED_ORIGINS` list to allow secure form submissions and authentication requests from the frontend.
    ```python
    CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",  # Frontend Vite server address
    "http://your-frontend-address.com",  # Replace with your actual frontend address
    ]
    ```

### 4. AWS RDS Credentials Setup

The AWS RDS credentials, used to connect your Django application to the remote database, are securely stored within the `DATABASES` section of the `backend/myproject/settings.py` file.

Since the project is hosted on the University of Sydney’s secure enterprise GitHub account, it’s safe to store these credentials directly in the settings file. However, in a production environment, it is recommended to store sensitive information like database credentials in environment variables or use a secret management system like AWS Secrets Manager.

### 5. Handling IPv6 Access Errors (Addressing ::1 Errors)

If you encounter access errors related to the address `::1`, this indicates that the backend is attempting to use the IPv6 loopback address (`::1`) for local access. If your environment does not support IPv6, or if you prefer to use IPv4, follow these steps:

1. **Switch to IPv4**
Ensure that your development environment is configured to use the IPv4 loopback address (127.0.0.1) instead of ::1.

2. **Disable IPv6 (if needed)**
On some systems, you may need to explicitly disable IPv6 to force local development to use IPv4. This varies based on the OS you are using and may involve changing network settings or configuration files.

By ensuring that your local development environment is using IPv4, you can avoid `::1` access issues.

### 6. Usage Instructions
After completing the setup and configuration, you can start both the backend and frontend servers as described above. Access the frontend at http://localhost:5173 and interact with the platform's features like album exploration, music playback, and playlist management.

Admins can access the admin panel for managing tracks, artists, albums, and genres.

### 7. API Documentatation
[a relative link](API_DOC.MD)

### 8. Known Issues
* **IPv6 Access Errors**: If you encounter `::1` errors, refer to the Handling IPv6 Access Errors section for a fix.
* **Search Functionality**: The search bar UI is in place, but additional backend API logic might be required for full search functionality.
* **Playlist UI Integration**: Playlist management functionality is partially implemented. While users can create and manage playlists, the full integration of playlists into the UI (e.g., dynamically displaying and interacting with playlists) is still in progress.
