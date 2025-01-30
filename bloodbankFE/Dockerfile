# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y \
    python3-tk \
    libpq-dev \
    build-essential

# Upgrade pip to ensure compatibility
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Install Tkinter (as it's not included by default in slim images)
RUN apt-get update && apt-get install -y python3-tk

# Set environment variables for database connection
ENV DATABASE="BloodBankManagement_Normalized"
ENV USER="postgres"
ENV PASSWORD="db@12db"
ENV HOST="localhost"

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run fr.py when the container launches
CMD ["python", "fr.py"]


