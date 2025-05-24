# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any necessary dependencies from dev-requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r dev-requirements.txt

# Default command to run when the container starts
CMD ["python"]