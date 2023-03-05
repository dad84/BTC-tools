# Bitcoin Address Matcher

The Bitcoin Address Matcher is a program that scans Bitcoin addresses for matches to a set of target addresses. It uses distributed computing to process the search in parallel, with multiple clients scanning different ranges of keys. The program is implemented using a master-slave architecture, where a central server distributes key ranges to clients and collects results from them.

## Server

The server is responsible for listening for incoming connections from clients and managing the distribution of key ranges. When a client connects to the server, it is assigned a unique ID and added to a list of active clients. The server then divides the range of keys to be scanned into smaller ranges and assigns each range to a client. The clients are responsible for scanning their assigned ranges of keys and reporting back to the server when they find a match.

The server also keeps track of progress and reports results back to clients. It maintains a dictionary of user data and progress data, and updates them as clients report progress and matches. When a client reports a match, the server sends a message to all connected clients indicating the address and private key of the match.

The server is implemented using Python 3 and the following libraries:

- `ecdsa`
- `base58`
- `hashlib`
- `pika`

The server can be run using the following command:

`python3 server.py`


## Client

The client is responsible for sending requests to the server for key ranges to scan. It then scans those key ranges for matches to the target addresses. The client uses a message queue to communicate with the server, allowing multiple clients to communicate with the server concurrently.

When the client starts, it prompts the user for a username. It then connects to the server and sends a message requesting a key range to scan. The server responds with the start and end values for the range to be scanned. The client scans the keys in the range and reports back to the server when it finds a match.

The client keeps track of progress and prints updates to the console as it scans keys. When a match is found, the client prints the address and private key of the match to the console and saves it to a file called `matches.txt`.

The client is implemented using Python 3 and the following libraries:

- `ecdsa`
- `base58`
- `hashlib`
- `pika`
- `socket`

The client can be run using the following command:

`python3 client.py`


## Master-Slave Architecture

The Bitcoin Address Matcher uses a master-slave architecture to distribute the workload of scanning Bitcoin addresses. In this architecture, the server acts as the master and the clients act as slaves. The server is responsible for dividing the range of keys to be scanned into smaller ranges and assigning each range to a client. The clients are responsible for scanning their assigned ranges of keys and reporting back to the server when they find a match.

This architecture has several advantages over a traditional client-server architecture. First, it allows multiple clients to communicate with the server concurrently, which can improve performance and reduce the time it takes to scan a large number of keys. Second, it allows the workload to be distributed among multiple clients, which can help to reduce the processing time required to scan a large number of keys. Finally, it allows the system to scale easily as more clients can be added to the system to handle increased workloads.

## Conclusion

The Bitcoin Address Matcher is a program that scans Bitcoin addresses for matches to a set of target addresses. It uses distributed computing and a master-slave architecture to distribute the workload of scanning keys among multiple clients. This approach allows the program to scale easily and process large numbers of keys quickly.

The program can be used for a variety of purposes, such as testing the security of Bitcoin addresses, recovering lost private keys, or simply searching for a specific address. It can also be modified to work with other cryptocurrencies that use public-private key pairs for address generation.

The program has several limitations, however. First, it is only effective if the target addresses are known. If the target addresses are unknown, the program will have to scan the entire key space, which can be time-consuming and resource-intensive. Second, it assumes that the private keys are generated using the same algorithm as the Bitcoin protocol. If a different algorithm is used, the program may not be effective in finding matches. Finally, it assumes that the target addresses are vulnerable to brute-force attacks. If the target addresses are protected using strong encryption or other security measures, the program may not be effective.

Despite these limitations, the Bitcoin Address Matcher is a powerful tool for scanning Bitcoin addresses for matches to a set of target addresses. It demonstrates the power of distributed computing and the effectiveness of master-slave architectures for handling large-scale computational tasks. The program can be used by researchers, security analysts, and anyone else interested in Bitcoin address security.

## References
Satoshi Nakamoto. Bitcoin: A Peer-to-Peer Electronic Cash System. https://bitcoin.org/bitcoin.pdf
ECDSA Public Key Recovery. https://crypto.stackexchange.com/questions/18105/ecdsa-public-key-recovery
Base58Check Encoding. https://en.bitcoin.it/wiki/Base58Check_encoding

