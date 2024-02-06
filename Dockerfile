# Use Ubuntu as the base image
FROM ubuntu:latest

# Set environment variables to reduce Python buffering
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean

# Set the working directory in the Docker container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code to the container
COPY server.py /app/

# Set the command to run the Uvicorn server
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port 8000"]