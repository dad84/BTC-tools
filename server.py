import socket
import ecdsa
import hashlib
import base58
import threading
import json
import pika

# Set up socket
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

# Store user data and progress data in dictionaries
users = {}
progress = {}

# Set up message queue connection
QUEUE_HOST = 'localhost'
QUEUE_PORT = 5672
QUEUE_USERNAME = 'guest'
QUEUE_PASSWORD = 'guest'
QUEUE_VIRTUAL_HOST = '/'
QUEUE_QUEUE = 'key_requests'
QUEUE_CONNECTION_PARAMETERS = pika.ConnectionParameters(
    host=QUEUE_HOST,
    port=QUEUE_PORT,
    virtual_host=QUEUE_VIRTUAL_HOST,
    credentials=pika.PlainCredentials(
        username=QUEUE_USERNAME,
        password=QUEUE_PASSWORD
    )
)
queue_connection = pika.BlockingConnection(QUEUE_CONNECTION_PARAMETERS)
queue_channel = queue_connection.channel()
queue_channel.queue_declare(queue=QUEUE_QUEUE)

# Function for handling client connections
def handle_client(conn, addr):
    username = None
    print(f"Client connected from {addr}")
    while True:
        # Receive data from client
        data = conn.recv(1024).decode()
        if not data:
            break
        # Set username from first message
        if username is None:
            username = data
            # Add user to dictionary
            users[username] = None
            print(f"User {username} registered")
            # Send confirmation message to client
            conn.sendall(f"User {username} registered".encode())
            # Broadcast new user message to all clients
            broadcast(f"User {username} has joined the server", username)
        else:
            # Check if message contains progress information
            if data.startswith("progress,"):
                # Extract username and progress information from message
                parts = data.split(",")
                username = parts[1]
                progress_info = parts[2]
                # Update progress data for user
                progress[username] = progress_info
                # Broadcast progress update to all clients
                broadcast_progress(progress)
    # Remove user from dictionaries and broadcast leave message to all clients
    if username is not None:
        del users[username]
        del progress[username]
        print(f"User {username} disconnected")
        broadcast(f"User {username} has left the server", username)
    conn.close()

# Function for broadcasting a message to all connected clients
def broadcast(message, exclude_user=None):
    for user, conn in connections.items():
        if user != exclude_user:
            conn.sendall(message.encode())

# Function for broadcasting progress updates to all connected clients
def broadcast_progress(progress):
    print("Broadcasting progress:", progress)
    for user, conn in connections.items():
        if user in progress:
            conn.sendall(progress[user].encode())


# Store connections in a dictionary
connections = {}

# Function for handling key requests from clients
def handle_key_request(ch, method, properties, body):
    # Decode the message from JSON format
    message = json.loads(body)
    username = message['username']
    start = message['start']
    end = message['end']
    reply_to = message['reply_to']
    correlation_id = message['correlation_id']
    # Generate keys and check for matches
    match = generate_key(start, end, username)
    if match is not None:
        # Send the matching address and private key to the client
        message = {
            'type': 'match',
            'username': username,
            'address': match['address'],
            'priv_key': match['priv_key']
        }
        queue_channel.basic_publish(
            exchange='',
            routing_key=reply_to,
            properties=pika.BasicProperties(correlation_id=correlation_id),
            body=json.dumps(message))
    else:
        # Send a message indicating that no further key ranges are available
        message = {
            'type': 'no_keys',
            'username': username
        }
        queue_channel.basic_publish(
            exchange='',
            routing_key=reply_to,
            properties=pika.BasicProperties(correlation_id=correlation_id),
            body=json.dumps(message))
    # Report progress to server
    message = {
        'type': 'progress',
        'username': username,
        'num_scanned': end - start
    }
    queue_channel.basic_publish(
        exchange='',
        routing_key=QUEUE_QUEUE,
        body=json.dumps(message))

def generate_key(start, end, username):
    # Initialize a counter for the number of keys scanned
    num_scanned = 0
    # Iterate through the range of keys and check for matches
    for i in range(start, end):
        # Increment the counter
        num_scanned += 1
        # Generate a byte string with the appropriate length
        secexp = i.to_bytes(32, byteorder='big')
        # Convert the byte string to an integer for use as the secret exponent
        secret_exponent = int.from_bytes(secexp, byteorder='big')
        # Check if the secret exponent is within the valid range for the curve
        if secret_exponent >= 1 and secret_exponent < ecdsa.SECP256k1.order:
            # Generate the private key and address as before
            priv_key = ecdsa.SigningKey.from_secret_exponent(secret_exponent, curve=ecdsa.SECP256k1)
            pub_key = priv_key.get_verifying_key()
            pub_key_bytes = pub_key.to_string('compressed')
            sha256 = hashlib.sha256()
            sha256.update(pub_key_bytes)
            hash1 = sha256.digest()
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(hash1)
            hash2 = ripemd160.digest()
            version = b'\x00'
            payload = version + hash2
            sha256 = hashlib.sha256()
            sha256.update(payload)
            hash3 = sha256.digest()
            checksum = hash3[:4]
            address_bytes = payload + checksum
            address = base58.b58encode(address_bytes).decode()
            # Check if address matches a target address
            if binary_search(target_addresses, address) != -1:
                # Return the matching address and private key
                return {
                    'address': address,
                    'priv_key': priv_key.to_string().hex()
                }
            # Report progress to server every 100,000 iterations
            if num_scanned % 100000 == 0:
                message = {
                    'type': 'progress',
                    'username': username,
                    'num_scanned': num_scanned
                }
                queue_channel.basic_publish(
                    exchange='',
                    routing_key=QUEUE_QUEUE,
                    body=json.dumps(message))

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


# Listen for connections and handle them
while True:
    conn, addr = s.accept()
    print('Connected by', addr)
    # Store connection in dictionary
    connections[threading.current_thread().name] = conn
    # Start thread for handling client
    threading.Thread(target=handle_client, args=(conn, addr)).start()

# Close connection to message queue
queue_connection.close()


