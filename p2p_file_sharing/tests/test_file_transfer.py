from app.file_transfer import send_file, receive_file

def test_file_transfer():
    import threading
    
    port = 5001
    filename = "test.txt"
    save_path = "received_test.txt"
    
    with open(filename, "w") as f:
        f.write("This is a test.")
    
    def receiver():
        receive_file(save_path, port)
    
    thread = threading.Thread(target=receiver)
    thread.start()
    
    send_file(filename, 'localhost', port)
    thread.join()
    
    with open(save_path, "r") as f:
        content = f.read()
    assert content == "This is a test."
