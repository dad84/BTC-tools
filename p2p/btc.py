import ecdsa
import hashlib
import base58
import time
import json

class Block:
    def __init__(self, index, timestamp, keys):
        self.index = index
        self.timestamp = timestamp
        self.keys = keys
        self.prev_hash = None
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode() +
                   str(self.timestamp).encode() +
                   str(self.keys).encode() +
                   str(self.prev_hash).encode())
        return sha.hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2

    def create_genesis_block(self):
        return Block(0, time.time(), [])

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.prev_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.prev_hash != prev_block.hash:
                return False

        return True

    def serialize(self, filename):
        data = {
            'chain': [block.__dict__ for block in self.chain],
            'difficulty': self.difficulty
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def deserialize(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)

        self.chain = [Block(**block_data) for block_data in data['chain']]
        self.difficulty = data['difficulty']

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

    blockchain = Blockchain()
    block_keys = []

    with open('btc.txt', 'r') as f:
        target_addresses = sorted(f.read().splitlines())

    while True:
        priv_key_hex, address = generate_key()
        block_keys.append((priv_key_hex, address))

        if len(block_keys) == 100000:
            block = Block(len(blockchain.chain), time.time(), block_keys)
            blockchain.add_block(block)
            block_keys = []

            # Print the hash of the new block for other peers to see
            print(f'Block hash: {block.hash}')

        index = binary_search(target_addresses, address)
        if index != -1:
            # Save the private key and corresponding address to a text file
            with open('matches.txt', 'a') as f:
                f.write(f'Address: {address}, Private Key: {priv_key_hex}\n')
            print(f'Address {address} matches a target address.')
            break
        else:
            print(f'{address} not match.')

    # Save the blockchain to a file
    blockchain.serialize('blockchain.json')

    input('Press enter to exit...')

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

if __name__ == '__main__':
    main()
