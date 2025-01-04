import os
import logging

def send_file(file_path, conn):
    """Send a file over an established connection."""
    try:
        # Prepare metadata
        file_size = os.path.getsize(file_path)
        metadata = f"{os.path.basename(file_path)}|{file_size}"
        logging.info(f"[Sender] Sending metadata: {metadata}")
        conn.sendall(metadata.encode())  # Send metadata

        # Wait for acknowledgment
        ack = conn.recv(1024).decode()
        logging.info(f"[Sender] Acknowledgment received: {ack}")
        if ack != "READY":
            logging.error("[Sender] Receiver not ready.")
            return

        # Send file content
        logging.info(f"[Sender] Sending file content for: {file_path}")
        with open(file_path, "rb") as f:
            while chunk := f.read(1024):
                conn.sendall(chunk)
        logging.info(f"[Sender] File {file_path} sent successfully.")
    except Exception as e:
        logging.error(f"[Sender] Error during file sending: {e}")


def receive_file(save_directory, conn):
    """Receive a file over an established connection."""
    try:
        # Receive metadata
        metadata = conn.recv(1024).decode()
        logging.info(f"[Receiver] Metadata received: {metadata}")
        if not metadata or "|" not in metadata:
            raise ValueError(f"Invalid metadata format received: {metadata}")

        # Parse metadata
        filename, file_size = metadata.split("|")
        file_size = int(file_size)

        # Confirm readiness
        conn.sendall("READY".encode())
        logging.info(f"[Receiver] Ready to receive file: {filename} ({file_size} bytes)")

        # Construct save path
        save_path = os.path.join(save_directory, filename)
        os.makedirs(save_directory, exist_ok=True)

        # Receive file content
        logging.info(f"[Receiver] Receiving file: {filename}")
        with open(save_path, "wb") as f:
            received = 0
            while received < file_size:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        logging.info(f"[Receiver] File received and saved to {save_path}.")
    except ValueError as ve:
        logging.error(f"[Receiver] Metadata parsing error: {ve}")
    except Exception as e:
        logging.error(f"[Receiver] Error during file reception: {e}")




