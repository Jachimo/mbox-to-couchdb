#!/usr/bin/env bash

COUCHDB_URL="http://172.25.60.51:5984"   # Change this if your CouchDB is running on a different host or port
COUCHDB_ADMIN_USER="admin"               # Replace with your CouchDB admin username
COUCHDB_ADMIN_PASS="MyPassword"          # Replace with your CouchDB admin password

# Check if username and password are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <username> <password>"
    exit 1
fi

USERNAME=$1
PASSWORD=$2

# Create a new user in CouchDB
echo "Creating user '$USERNAME' in CouchDB..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X PUT "$COUCHDB_URL/_users/org.couchdb.user:$USERNAME" \
    --user "$COUCHDB_ADMIN_USER:$COUCHDB_ADMIN_PASS" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "'"$USERNAME"'",
        "password": "'"$PASSWORD"'",
        "roles": [],
        "type": "user"
    }')

if [ "$RESPONSE" -eq 201 ]; then
    echo "User '$USERNAME' created successfully."
elif [ "$RESPONSE" -eq 409 ]; then
    echo "Error: User '$USERNAME' already exists."
else
    echo "Error: Failed to create user '$USERNAME'. HTTP response code: $RESPONSE."
fi
