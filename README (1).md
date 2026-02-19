# Assignment 1: MySQL Database Table Transfer with Digital Signature Verification

## Overview
A client-server Python application that extracts Electronic Health Record (EHR) data from a MySQL database, signs it with a 2048-bit RSA digital signature (SHA-256), transfers it over a socket connection, and verifies the signature on the server before saving.

## Architecture

```
┌─────────────────────────────┐         ┌──────────────────────────────┐
│          CLIENT              │  TCP/IP │           SERVER              │
│                              │ Socket  │                              │
│ 1. Connect to MySQL          │────────►│ 1. Accept connection          │
│ 2. Extract EHR table → CSV   │         │ 2. Receive public key         │
│ 3. Generate RSA 2048 keys    │         │ 3. Receive EHR.csv            │
│ 4. Sign CSV (SHA-256 + PSS)  │         │ 4. Receive signature          │
│ 5. Send: key + CSV + sig     │         │ 5. Verify signature           │
│ 6. Receive confirmation      │         │ 6. Save file if valid         │
└─────────────────────────────┘         └──────────────────────────────┘
```

## Prerequisites
- Python 3.8+
- MySQL Server running locally
- Required Python packages:
  ```
  pip install mysql-connector-python cryptography
  ```

## Setup

### 1. Database Setup
Run the SQL script to create the database, table, and sample data:
```bash
mysql -u root -p < setup_database.sql
```

### 2. Configure Database Credentials
Edit `client.py` and update the `DB_CONFIG` dictionary with your MySQL credentials:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "healthcareDB"
}
```

## Running the Application

### Step 1: Start the Server
```bash
python server.py
```
The server will listen on `localhost:65432`.

### Step 2: Run the Client (in a separate terminal)
```bash
python client.py
```

## Expected Output

### Server Terminal
```
============================================================
  EHR Database Transfer Server with Signature Verification
============================================================
[SERVER] Listening on localhost:65432 ...

[SERVER] Connection accepted from ('127.0.0.1', XXXXX).
[SERVER] Received Public Key (451 bytes).
[SERVER] Received EHR.csv (XXX bytes).
[SERVER] Received Signature (256 bytes).
[SERVER] Verifying digital signature ...
[SERVER] Signature VALID. File saved to received_files/EHR.csv.
[SERVER] Connection with ('127.0.0.1', XXXXX) closed.
```

### Client Terminal
```
============================================================
  EHR Database Transfer Client with Digital Signature
============================================================
[CLIENT] Extracted 2 record(s) from EHR table.
[CLIENT] Data written to EHR.csv.
[CLIENT] RSA 2048-bit key pair generated.
[CLIENT] Digital signature created for EHR.csv (SHA-256 + RSA-PSS).
[CLIENT] Connected to server at localhost:65432.
[CLIENT] Sent Public Key (451 bytes).
[CLIENT] Sent EHR.csv (XXX bytes).
[CLIENT] Sent Signature (256 bytes).
[CLIENT] Server response: SUCCESS: Signature verified. File saved.
[CLIENT] Transfer complete.
```

## File Structure
```
assignment1/
├── client.py            # Client application
├── server.py            # Server application
├── setup_database.sql   # Database setup script
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Security Details
- **Key Size**: RSA 2048-bit
- **Hashing Algorithm**: SHA-256
- **Padding Scheme**: PSS (Probabilistic Signature Scheme) with MGF1
- **Signature Size**: 256 bytes (2048 bits / 8)

## Protocol
The client sends three length-prefixed payloads over TCP:
1. **Public Key** (PEM-encoded) — for the server to verify the signature
2. **EHR.csv** (file contents) — the data to be transferred
3. **Digital Signature** (raw bytes) — the RSA-PSS signature of the CSV

Each payload is preceded by an 8-byte big-endian integer indicating its length.
