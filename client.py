import socket
import ecdsa
import hashlib
import base58
import json
import pika

# Set up socket
HOST = '78.141.230.251'
PORT = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Set up message queue connection
QUEUE_HOST = 'localhost'
QUEUE_PORT = 5672
QUEUE_USERNAME = 'guest'
QUEUE_PASSWORD = 'guest'
QUEUE_VIRTUAL_HOST = '/'
QUEUE_QUEUE = 'key_requests'
QUEUE_REPLY_QUEUE = 'key_responses'
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
queue_channel.queue_declare(queue=QUEUE_REPLY_QUEUE)
reply_queue = queue_channel.queue_declare(queue='', exclusive=True).method.queue

# Get user input for username
username = input("Enter your username: ")

# Read target addresses from file
with open('btc.txt', 'r') as f:
    target_addresses = sorted(f.read().splitlines())

# Send key requests to server until all ranges have been processed
start = 0
end = 100000000
while start < end:
    # Send a key request for the current range
    message = {
        'type': 'key_request',
        'username': username,
        'start': start,
        'end': min(start + 1000000, end),
        'reply_to': reply_queue,
        'correlation_id': str(start)
    }
    queue_channel.basic_publish(
        exchange='',
        routing_key=QUEUE_QUEUE,
        body=json.dumps(message))
    print(f"Sent key request for range {start}-{min(start + 1000000, end)}")
    # Wait for a response from the server
    method, properties, body = queue_channel.basic_get(queue=QUEUE_REPLY_QUEUE, auto_ack=True)
    if body:
        # Decode the message from JSON format
        message = json.loads(body)
        if message['type'] == 'match':
            # Save the private key and corresponding address to a text file
            priv_key = ecdsa.SigningKey.from_string(bytes.fromhex(message['priv_key']), curve=ecdsa.SECP256k1)
            with open('matches.txt', 'a') as f:
                f.write(f'Address: {message["address"]}, Private Key: {priv_key.to_string().hex()}\n')
            print(f'Address {message["address"]} matches a target address.')
            # Update the start value to avoid processing this range again
            start = int(properties.correlation_id) + 1
        elif message['type'] == 'no_keys':
            # No further key ranges are available
            start = end
            print('No further key ranges available.')
        elif message['type'] == 'progress':
            # Print progress message
            print(f"Processed {message['num_scanned']} keys so far.")
    else:
        # No response from server, try again
        print('No response from server, trying again.')
# Close connection to server and message queue
s.close()
queue_connection.close()



