# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project files into the working directory in the container
COPY . /app/

# Expose the port the app runs on
EXPOSE 8000

# Run the Django development server (or use gunicorn for production)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
