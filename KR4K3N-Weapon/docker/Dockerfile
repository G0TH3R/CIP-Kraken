# Use an official Python runtime as a parent image
FROM ubuntu:22.04

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt update && apt upgrade -y

RUN apt install python3-pip nano vim -y

# Install the required packages from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

#RUN pip install -r requirements.txt

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Expose the Flask app port
EXPOSE 5300

# Run the Flask application
# CMD ["flask", "run", "--host=0.0.0.0","--port=5300"]
CMD ["python3","app.py"]
