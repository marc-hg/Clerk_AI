# Use an official Python runtime as a parent image
FROM python:3.12-slim

# poppler needed for pdf library
RUN apt-get update && apt-get install -y poppler-utils

# Set the working directory in the container to /clerkai
WORKDIR /clerkai
COPY ./requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the command to start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
