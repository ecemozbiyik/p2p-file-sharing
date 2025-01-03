from app.peer_discovery import discover_peers
from app.file_transfer import send_file, receive_file
from app.logger import setup_logger

def main():
    setup_logger()
    print("Discovering peers...")
    peers = discover_peers()
    if not peers:
        print("No peers discovered automatically.")
        manual_mode = input("Do you want to enter the target peer manually? (yes/no): ").strip().lower()
        if manual_mode == "yes":
            host = input("Enter the target host (IP): ").strip()
            port = int(input("Enter the target port: ").strip())
            peers.append((host, port))

    choice = input("Do you want to send or receive a file? (send/receive): ").strip().lower()
    if choice == "send":
        filename = input("Enter the filename to send: ").strip()
        if peers:
            host, port = peers[0]  # Use the first peer in the list
            send_file(filename, host, port)
            print(f"File {filename} sent to {host}:{port}")
        else:
            print("No peers found to send the file.")
    elif choice == "receive":
        save_path = input("Enter the path to save the received file: ").strip()
        port = int(input("Enter the port to listen on: "))
        receive_file(save_path, port)
        print(f"File received and saved to {save_path}")

if __name__ == "__main__":
    main()
