import socket

def discover_peers(broadcast_port=5000, discovery_message="DISCOVER_PEERS"):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)
    
    sock.sendto(discovery_message.encode(), ('<broadcast>', broadcast_port))
    
    peers = []
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            peers.append(addr)
    except socket.timeout:
        pass
    
    return peers