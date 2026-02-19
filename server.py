"""
Server-Side Application
-----------------------
1. Listens for an incoming client connection.
2. Receives the public key, EHR.csv data, and the digital signature.
3. Verifies the signature using the public key (SHA-256 + RSA-PSS).
4. Saves EHR.csv only if verification is successful.
"""

import socket
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


# ── Configuration ────────────────────────────────────────────────────────────
HOST = "localhost"
PORT = 65432
SAVE_DIR = "received_files"
CSV_FILENAME = "EHR.csv"


# ── Helper: receive exact number of bytes ────────────────────────────────────
def recv_exact(sock, num_bytes):
    """Receive exactly num_bytes from the socket."""
    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(min(4096, num_bytes - len(data)))
        if not chunk:
            raise ConnectionError("Connection closed before all data was received.")
        data += chunk
    return data


# ── Helper: receive a length-prefixed payload ────────────────────────────────
def recv_payload(sock, label):
    """Receive a payload preceded by an 8-byte big-endian length header."""
    length_bytes = recv_exact(sock, 8)
    length = int.from_bytes(length_bytes, "big")
    payload = recv_exact(sock, length)
    print(f"[SERVER] Received {label} ({length} bytes).")
    return payload


# ── Signature Verification ───────────────────────────────────────────────────
def verify_signature(pub_key_pem, file_data, signature):
    """
    Verify the digital signature of the file data using the provided
    public key (PEM) with SHA-256 hashing and RSA-PSS padding.
    Returns True if valid, False otherwise.
    """
    public_key = serialization.load_pem_public_key(pub_key_pem)

    try:
        public_key.verify(
            signature,
            file_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


# ── Main Server Loop ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  EHR Database Transfer Server with Signature Verification")
    print("=" * 60)

    # Create save directory if it does not exist
    os.makedirs(SAVE_DIR, exist_ok=True)

    # Set up listening socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(1)
    print(f"[SERVER] Listening on {HOST}:{PORT} ...\n")

    while True:
        conn, addr = server_sock.accept()
        print(f"[SERVER] Connection accepted from {addr}.")

        try:
            # Receive three payloads
            pub_key_pem = recv_payload(conn, "Public Key")
            file_data = recv_payload(conn, "EHR.csv")
            signature = recv_payload(conn, "Signature")

            # Verify the digital signature
            print("[SERVER] Verifying digital signature ...")
            if verify_signature(pub_key_pem, file_data, signature):
                # Signature valid – save the file
                save_path = os.path.join(SAVE_DIR, CSV_FILENAME)
                with open(save_path, "wb") as f:
                    f.write(file_data)
                print(f"[SERVER] Signature VALID. File saved to {save_path}.")
                conn.sendall(b"SUCCESS: Signature verified. File saved.")
            else:
                # Signature invalid – reject the file
                print("[SERVER] Signature INVALID. File rejected and NOT saved.")
                conn.sendall(b"FAILURE: Signature verification failed. File rejected.")

        except ConnectionError as e:
            print(f"[SERVER] Connection error: {e}")
        except Exception as e:
            print(f"[SERVER] Error: {e}")
            conn.sendall(f"ERROR: {e}".encode())
        finally:
            conn.close()
            print(f"[SERVER] Connection with {addr} closed.\n")


if __name__ == "__main__":
    main()
