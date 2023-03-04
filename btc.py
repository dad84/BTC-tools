import ecdsa
import hashlib
import base58
import time

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

    while True:
        priv_key_hex, address = generate_key()

        index = binary_search(target_addresses, address)
        if index != -1:
            # Save the private key and corresponding address to a text file
            with open('matches.txt', 'a') as f:
                f.write(f'Address: {address}, Private Key: {priv_key_hex}\n')
            print(f'Address {address} matches a target address.')
            break
        else:
            print(f' {address} not match.')


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
