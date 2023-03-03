# Bitcoin Address Lookup Tool

This is a Python script that uses the [curses](https://docs.python.org/3/howto/curses.html) library to create a command-line interface for a Bitcoin address lookup tool. The program generates random Bitcoin addresses and checks if they match any of the addresses in a list stored in a file called "btc.txt". If a match is found, the program retrieves information about the address from the blockchain and displays the balance of the address in satoshis. If the balance is non-zero, the program displays the key for the address.

The program uses a binary search algorithm to search for the Bitcoin address in the target list, which is faster than a linear search for large lists.

The program also handles network errors by retrying the request up to three times with a delay of 5 seconds between each attempt.

The program uses two colors to highlight the balance of the address: green for positive balances and red for zero balances.

The program runs in a loop until a match is found or the user exits by pressing any key.

## Requirements

To run this program, you need to have Python 3 and the following Python packages installed:

- `curses`
- `requests`

You can install these packages using pip:

`pip install curses requests`


## Usage

To use this program, follow these steps:

1. Clone this repository to your local machine.
2. Open a terminal or command prompt and navigate to the directory where the repository was cloned.
3. Run the following command:

`python btc.py`


4. The program will start running and display a message to press any key to start.
5. Press any key to start the program.
6. The program will generate random Bitcoin addresses and search for matches in the target list.
7. If a match is found with a non-zero balance, the program will display the key for the address and wait for the user to press any key to exit.
8. If a match is found with a zero balance or an error occurs, the program will continue searching.
9. To exit the program at any time, press any key.

## Contributing

Contributions to this project are welcome. To contribute, follow these steps:

1. Fork this repository.
2. Create a new branch with your changes: `git checkout -b my-feature-branch`.
3. Commit your changes and push them to your fork: `git commit -m "Add new feature" && git push origin my-feature-branch`.
4. Create a pull request for your changes.
