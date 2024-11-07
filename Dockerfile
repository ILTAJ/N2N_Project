# Base image
FROM python:3.10

# Working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

# Upgrade pip without SSL verification (temporary fix for SSL issues)
RUN pip install --upgrade pip --no-cache-dir --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org --disable-pip-version-check

# Install dependencies without SSL verification (temporary fix)
RUN pip install --no-cache-dir --trusted-host files.pythonhosted.org --trusted-host pypi.org --trusted-host pypi.python.org --disable-pip-version-check -r requirements.txt

# Copy the application code
COPY . .

# Expose port and run
EXPOSE 8081
CMD ["python", "app.py"]
