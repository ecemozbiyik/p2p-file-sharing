import os

def get_file_size(filename):
    return os.path.getsize(filename)

def validate_checksum(file_path, expected_checksum):
    import hashlib
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == expected_checksum