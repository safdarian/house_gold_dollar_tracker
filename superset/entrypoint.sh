#!/bin/bash

# Function to check if a Python package is installed
function is_package_installed() {
  local package=$1
  pip list | grep -q "^$package" > /dev/null 2>&1
}

# Function to check if Superset has already been initialized
function is_superset_initialized() {
  # Check for the existence of the 'user_attribute' table in the metadata database
  superset db upgrade > /dev/null 2>&1
  result=$(superset db check > /dev/null 2>&1; echo $?)
  if [ "$result" -eq 0 ]; then
    return 0
  else
    return 1
  fi
}

# Function to check if the admin user exists
function is_admin_user_created() {
  superset fab list-users | grep -q "admin@example.com" > /dev/null 2>&1
}

# Wait for Superset to initialize
echo "Waiting for Superset to initialize..."
sleep 5

# Install ClickHouse SQLAlchemy driver if not already installed
if ! is_package_installed "clickhouse-sqlalchemy"; then
  echo "Installing ClickHouse SQLAlchemy driver..."
  pip install clickhouse-sqlalchemy==0.2.3
else
  echo "ClickHouse SQLAlchemy driver is already installed."
fi

# Upgrade the database schema if necessary
if ! is_superset_initialized; then
  echo "Upgrading Superset database schema..."
  superset db upgrade
else
  echo "Superset database schema is already up-to-date."
fi

# Create the admin user if it doesn't exist
if ! is_admin_user_created; then
  echo "Creating Superset admin user..."
  superset fab create-admin \
    --username admin \
    --firstname Superset \
    --lastname Admin \
    --email admin@example.com \
    --password admin
else
  echo "Superset admin user already exists."
fi

# Initialize Superset if not already done
if ! is_superset_initialized; then
  echo "Initializing Superset..."
  superset init
else
  echo "Superset is already initialized."
fi

# Start Superset
echo "Starting Superset..."
exec "$@"