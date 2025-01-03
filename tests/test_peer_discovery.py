from app.peer_discovery import discover_peers

def test_discover_peers():
    peers = discover_peers()
    assert isinstance(peers, list)