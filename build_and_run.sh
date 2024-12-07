#!/bin/bash

# Navigate to the frontend directory and install dependencies
cd frontend
npm install

# Build the Vite app
npm run build

# Move the built files to the backend's static folder
rm -rf ../backend/static
mv dist ../backend/static

# Navigate back to the backend directory and start the Flask app
cd ../backend
gunicorn app:app