# start from a slim python image
FROM python:3.11-slim

# Set working directory inside the container 
WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y build-essential \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first 
COPY requirements.txt .

# Install python depends
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code into container
COPY . . 

# Expose ports 
EXPOSE 5001 8501

# Defaut command 
CMD ["bash", "run.sh"]

