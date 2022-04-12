# Base builder image
FROM python:3.10-alpine as builder

# Configure environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc g++ musl-dev rust cargo patchelf python3-dev

# Copy requirements files
COPY ./requirements/requirements.txt /app/requirements.txt
COPY ./requirements/requirements.lint.txt /app/requirements.lint.txt
COPY ./requirements/requirements.dev.txt /app/requirements.dev.txt

# Install project dependencies
RUN pip install --upgrade pip-tools
RUN pip-sync requirements.txt requirements.*.txt


# Base image
FROM python:3.10-alpine

# Configure environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set working directory
WORKDIR /app

# Copy project dependencies
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Install system dependencies
RUN apk add --no-cache libstdc++

# Copy project files
COPY . .
