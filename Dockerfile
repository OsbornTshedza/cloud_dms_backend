FROM debian:stable-slim

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-venv python3-pip --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set up virtual environment
RUN python3 -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Define Lambda entrypoint
ENTRYPOINT ["/app/venv/bin/python", "-m", "awslambdaric", "lambda_function.lambda_handler"]
