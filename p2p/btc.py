import ecdsa
import hashlib
import base58
import time
import socket
import threading
import json

def generate_key():
    # Generate a 256-bit private key
    priv_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

    # Derive the corresponding public key
    pub_key = priv_key.get_verifying_key()

    # Encode the public key in compressed format
    pub_key_bytes = pub_key.to_string('compressed')

    # Hash the public key using SHA-256
    sha256 = hashlib.sha256()
    sha256.update(pub_key_bytes)
    hash1 = sha256.digest()

    # Hash the previous hash using RIPEMD-160
    ripemd160 = hashlib.new('ripemd160')
    ripemd160.update(hash1)
    hash2 = ripemd160.digest()

    # Add the version byte (0x00 for mainnet) and checksum
    version = b'\x00'
    payload = version + hash2
    sha256 = hashlib.sha256()
    sha256.update(payload)
    hash3 = sha256.digest()
    checksum = hash3[:4]
    address_bytes = payload + checksum

    # Encode the address in base58 format
    address = base58.b58encode(address_bytes).decode()

    return priv_key.to_string().hex(), address

def main():
    import os

    if not os.path.exists('matches.txt'):
        with open('matches.txt', 'w') as f:
            f.write('')  # create an empty file

    with open('btc.txt', 'r') as f:
        target_addresses = sorted(f.read().splitlines())

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 10000))
    sock.listen(5)

    nodes = []

    # Thread to handle incoming connections
    def handle_connection(conn):
        node = {}
        node['connection'] = conn
        node['progress'] = []
        nodes.append(node)

        while True:
            # Receive message from the connected node
            data = conn.recv(1024)
            if not data:
                break

            # Parse the message
            message = json.loads(data.decode())

            if message['type'] == 'progress':
                # Add the sender's progress to the list of nodes' progress
                node['progress'].append(message['progress'])
            elif message['type'] == 'match':
                # Save the private key and corresponding address to a text file
                with open('matches.txt', 'a') as f:
                    f.write(f'Address: {message["address"]}, Private Key: {message["priv_key_hex"]}\n')
                print(f'Address {message["address"]} matches a target address.')
                # Broadcast the match message to all connected nodes
                broadcast({'type': 'match', 'address': message['address'], 'priv_key_hex': message['priv_key_hex']})
                break

        # Remove the node from the list of nodes when the connection is closed
        nodes.remove(node)

    # Thread to periodically broadcast progress to all connected nodes
    def broadcast_progress():
        while True:
            # Build the progress message
            progress = {'start': nodes[0]['progress'][0]['start'], 'end': nodes[-1]['progress'][-1]['end'], 'timestamp': int(time.time())}
            message = {'type': 'progress', 'progress': progress}

            # Broadcast
        broadcast(message)
        time.sleep(5)

# Thread to handle keyboard input for stopping the script
def input_thread():
    input()
    # Build and broadcast the stop message
    message = {'type': 'stop'}
    broadcast(message)
    sock.close()

# Start the progress broadcast thread and input thread
broadcast_thread = threading.Thread(target=broadcast_progress)
broadcast_thread.daemon = True
broadcast_thread.start()
input_thread = threading.Thread(target=input_thread)
input_thread.daemon = True
input_thread.start()

while True:
    # Wait for a connection
    conn, addr = sock.accept()

    # Start a new thread to handle the connection
    t = threading.Thread(target=handle_connection, args=(conn,))
    t.daemon = True
    t.start()

def binary_search(lst, target):
    lo, hi = 0, len(lst) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if lst[mid] < target:
            lo = mid + 1
        elif lst[mid] > target:
            hi = mid - 1
        else:
            return mid
    return -1

def broadcast(message):
    # Convert the message to JSON and send it to all connected nodes
    data = json.dumps(message).encode()
    for node in nodes:
        try:
            node['connection'].sendall(data)
        except:
            nodes.remove(node)
