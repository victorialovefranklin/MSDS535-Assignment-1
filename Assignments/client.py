"""
Client-Side Application
-----------------------
1. Connects to MySQL and extracts EHR table data.
2. Writes data to EHR.csv.
3. Generates RSA key pair (2048-bit) and signs EHR.csv with SHA-256.
4. Sends the public key, EHR.csv, and digital signature to the server.
"""

import socket
import csv
import os
import mysql.connector
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


# ── Configuration ────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "vfranklin",
    "password": "Memphis34@",       # adjust to your MySQL credentials
    "database": "healthcareDB"
}

SERVER_HOST = "localhost"
SERVER_PORT = 65432
CSV_FILE = "EHR.csv"


# ── Step 1: Extract data from MySQL ─────────────────────────────────────────
def extract_ehr_data():
    """Connect to healthcareDB and return all rows from the EHR table."""
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM EHR")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    print(f"[CLIENT] Extracted {len(rows)} record(s) from EHR table.")
    return columns, rows


# ── Step 2: Write data to CSV ────────────────────────────────────────────────
def write_csv(columns, rows):
    """Write the extracted EHR data to a CSV file."""
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    print(f"[CLIENT] Data written to {CSV_FILE}.")


# ── Step 3: Generate RSA key pair and sign the file ──────────────────────────
def generate_keys():
    """Generate a 2048-bit RSA private/public key pair."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    print("[CLIENT] RSA 2048-bit key pair generated.")
    return private_key, public_key


def sign_file(private_key, filepath):
    """Create a digital signature for the given file using SHA-256."""
    with open(filepath, "rb") as f:
        file_data = f.read()

    signature = private_key.sign(
        file_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print(f"[CLIENT] Digital signature created for {filepath} (SHA-256 + RSA-PSS).")
    return signature


def serialize_public_key(public_key):
    """Serialize the public key to PEM format for transmission."""
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )


# ── Step 4: Send data to server ─────────────────────────────────────────────
def send_data(pub_key_bytes, file_data, signature):
    """
    Establish a socket connection and send three items to the server:
      1. Public key (PEM)
      2. EHR.csv contents
      3. Digital signature
    Each item is preceded by its length (8-byte big-endian integer).
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_HOST, SERVER_PORT))
    print(f"[CLIENT] Connected to server at {SERVER_HOST}:{SERVER_PORT}.")

    for label, payload in [("Public Key", pub_key_bytes),
                           ("EHR.csv", file_data),
                           ("Signature", signature)]:
        length = len(payload)
        sock.sendall(length.to_bytes(8, "big"))
        sock.sendall(payload)
        print(f"[CLIENT] Sent {label} ({length} bytes).")

    # Wait for server response
    response = sock.recv(1024).decode()
    print(f"[CLIENT] Server response: {response}")

    sock.close()
    print("[CLIENT] Connection closed.")


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EHR Database Transfer Client with Digital Signature")
    print("=" * 60)

    # Step 1 – Extract
    columns, rows = extract_ehr_data()

    # Step 2 – Write CSV
    write_csv(columns, rows)

    # Step 3 – Key generation and signing
    private_key, public_key = generate_keys()
    signature = sign_file(private_key, CSV_FILE)
    pub_key_bytes = serialize_public_key(public_key)

    # Step 4 – Read file and send
    with open(CSV_FILE, "rb") as f:
        file_data = f.read()

    send_data(pub_key_bytes, file_data, signature)

    # Clean up local CSV (optional)
    print("[CLIENT] Transfer complete.")


if __name__ == "__main__":
    main()
