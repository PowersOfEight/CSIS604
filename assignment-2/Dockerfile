# Use a lightweight official python runtime
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt to the working directory
COPY requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app.py into the container
COPY app.py .

# Expose port 5000 
EXPOSE 5000

# Set default NODE_ID
ENV NODE_ID=node-01

# Set default PORT
ENV PORT=5000

# Set the entrypoint of the application
CMD ["python", "./app.py"]
