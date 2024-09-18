# Use the official Ubuntu base image
FROM ubuntu:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    apt-get clean

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Activate the virtual environment and install the Python dependencies
COPY requirements.txt /app/
RUN . /opt/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Expose the port Flask will run on
EXPOSE 5000

# Add the desired line to /etc/passwd
RUN echo "FLAG{4b496a74f72607d024dd5a1c5a68839aa9c12c14}" >> /etc/passwd

# Copy the rest of the application code
COPY . /app

# Activate virtual environment and run Flask app
CMD ["/opt/venv/bin/python", "app.py"]
