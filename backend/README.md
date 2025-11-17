# Face Recognition Attendance System - Backend

This directory contains the FastAPI backend for the face recognition attendance system.

## Setup and Installation

Follow these steps to set up the local development environment and run the backend server.

### 1. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### 2. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 3. Run the Server

Start the FastAPI development server using Uvicorn. The `--reload` flag will automatically restart the server when you make code changes.

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
