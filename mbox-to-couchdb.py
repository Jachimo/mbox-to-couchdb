# -*- coding: utf-8 -*-
# Written for Python 3.10+

# USAGE:  python mbox-to-couchdb.py <mbox_file> <db_config_file.toml>

# Exit codes:  0 = success, 1 = critical fail, 2 = partial fail

import sys
import os
import mailbox
import tomli
import couchdb
import hashlib
from email.header import decode_header, make_header
from email.policy import default

DEBUG = False


def main(args):
    mbox_file = args[1]
    db_config_file = args[2]
    retval = 0  # return code for sys.exit()

    # Load database config file
    config = load_config(db_config_file)
    if not config:
        return 1

    # Make sure the mbox file exists
    if not os.path.isfile(mbox_file):
        print(f"Error: The file {mbox_file} does not exist.")
        return 1
    
    # Get CouchDB connection parameters
    couchdb_server_url = config.get('couchdb', {}).get('server_url', '')
    db_name = config.get('couchdb', {}).get('db_name', '')
    db_username = config.get('couchdb', {}).get('username', '')
    db_password = config.get('couchdb', {}).get('password', '')

    if DEBUG:
        print(f"CouchDB URL: {couchdb_server_url}")
        print(f"Database name: {db_name}")
        print(f"Database username: {db_username}")
        print(f"Database password: {db_password}")

    # CouchDB connection setup
    couch = couchdb.Server(f"http://{db_username}:{db_password}@{couchdb_server_url.split('://')[1]}")
    try:
        db = couch[db_name]
    except couchdb.http.ResourceNotFound:
        print("Error: Unable to find specified database in CouchDB. Exiting.")
        return 1
    
    if DEBUG:
        print("Connected to: ", db)

    # Open and parse the mbox file
    try:
        mbox = mailbox.mbox(mbox_file, create=False)
        mbox.lock()

        count = 0
        for message in mbox:
            couchdoc = couchdb.client.Document()
            
            # Add all headers
            for k, v in message.items():
                couchdoc[k] = make_header(decode_header(v)).__str__()  # Convert to clean Unicode

            if DEBUG:
                print("-----------------")
                print_headers(couchdoc)
            
            # Use the Message-Id header as the CouchDB id if present; if not use hash
            if 'Message-ID' in couchdoc:
                couchdoc['_id'] = couchdoc['Message-ID']
            elif 'Message-Id' in couchdoc:
                couchdoc['_id'] = couchdoc['Message-Id']
            else:
                # SHAKE128 with hexdigest length 16 = 32 hex digits, 12 = 24 hex digits, etc.
                # If you are dealing with really huge archives, you can increase as needed.
                couchdoc['_id'] = hashlib.shake_128(message.as_bytes()).hexdigest(12)
            
            # Save to database, skipping duplicates (idempotency)
            try:
                db.save(couchdoc)
            except couchdb.http.ResourceConflict:
                print(f"Message-ID already in database: {couchdoc['_id']}")
                retval = 2
                continue

            # Attach the entire message to the CouchDB document
            db.put_attachment(
                doc=couchdoc,
                content=message.as_bytes(),
                filename=couchdoc['_id'].strip().strip("<>\\/|") + '.eml',
                content_type='message/rfc822')
            
            # Cleanup
            count += 1
            del(couchdoc)

    except Exception as e:
        print(f"{e.__class__.__name__} exception in main processing loop")
        print(e)
        retval = 1
        raise
    finally:
        print(f"Added {count} messages to {db_name}")
        mbox.unlock()
        mbox.close()
        return retval
    

def print_headers(doc):
    for k, v in doc.items():
        print(f"{k}     {v}")


def load_config(config_file):
    """Load server configuration from a TOML file."""
    try:
        with open(config_file, 'rb') as file:
            config = tomli.load(file)
            return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        return False
    except tomli.TomlDecodeError:
        print(f"Error: Configuration file '{config_file}' is not a valid TOML file.")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Incorrect number of arguments.")
        print("Usage: ./mbox-to-couchdb.py <mbox_file> <couchdb_config_file.toml>")
        sys.exit(1)
    sys.exit(main(sys.argv))
