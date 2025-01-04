from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QFileDialog
)
import logging
import sys
import threading
from app.file_transfer import send_file, receive_file

class LogHandler(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        log_entry = self.format(record)
        self.text_edit.append(log_entry)

class P2PFileSharingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P File Sharing Application")
        self.resize(800, 600)

        # Main Layout
        self.layout = QVBoxLayout()

        # Host and Port Fields
        self.layout.addWidget(QLabel("Enter Host (IP):"))
        self.host_input = QLineEdit()
        self.layout.addWidget(self.host_input)

        self.layout.addWidget(QLabel("Enter Port:"))
        self.port_input = QLineEdit()
        self.layout.addWidget(self.port_input)

        # File Selection
        self.layout.addWidget(QLabel("File to Send:"))
        self.file_path_input = QLineEdit()
        self.layout.addWidget(self.file_path_input)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.layout.addWidget(self.browse_button)

        # Send and Receive Buttons
        self.send_button = QPushButton("Send File")
        self.send_button.clicked.connect(self.send_file)
        self.layout.addWidget(self.send_button)

        self.receive_button = QPushButton("Receive File")
        self.receive_button.clicked.connect(self.receive_file)
        self.layout.addWidget(self.receive_button)

        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.layout.addWidget(QLabel("Logs:"))
        self.layout.addWidget(self.log_display)

        # Set Main Layout
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # Logger Setup
        self.setup_logger()

    def setup_logger(self):
        handler = LogHandler(self.log_display)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_path_input.setText(file_path)

    def send_file(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        file_path = self.file_path_input.text()

        if host and port and file_path:
            threading.Thread(target=send_file, args=(file_path, host, port), daemon=True).start()
            logging.info(f"Sending file: {file_path} to {host}:{port}")
        else:
            logging.error("Please fill in all fields to send a file.")

    def receive_file(self):
        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        port = int(self.port_input.text())

        if save_directory and port:
            threading.Thread(target=receive_file, args=(save_directory, port), daemon=True).start()
            logging.info(f"Ready to receive file in directory: {save_directory} on port {port}")
        else:
            logging.error("Please select a directory and enter a port to receive a file.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = P2PFileSharingApp()
    main_window.show()
    sys.exit(app.exec_())
