# Use an official Ubuntu image as the base
FROM ubuntu

# Set the working directory to /app
WORKDIR /app

# Copy the requirements and application files to the working directory
COPY requirements.txt /app
COPY myproject /app/myproject

# Install Python and pip, and then set up a virtual environment
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv && \
    python3 -m venv /app/venv && \
    /app/venv/bin/pip install -r requirements.txt

# Run Django database migrations and any custom management commands
RUN /app/venv/bin/python myproject/manage.py makemigrations && \
    /app/venv/bin/python myproject/manage.py migrate && \
    /app/venv/bin/python myproject/manage.py create_plans

# Expose the port that the Django app will run on
EXPOSE 8000

# Start the Django development server using the virtual environment
ENTRYPOINT ["/app/venv/bin/python"]
CMD ["myproject/manage.py", "runserver", "0.0.0.0:8000"]     






