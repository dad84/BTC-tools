# Bitcoin Address Finder

This is a Python script that retrieves Bitcoin addresses with a balance of at least 10 BTC and saves them to a file. It does this by either randomly generating addresses and checking their balances using the Blockchain.info API, or by retrieving a list of addresses associated with top exchanges from the CoinGecko API.

## Requirements

- Python 3.6 or later
- `requests` library (can be installed using pip: `pip install requests`)

## Usage

1. Clone or download this repository.
2. Open a terminal window and navigate to the directory containing the `btca.py` file.
3. Run the script using the command `python btca.py`.
4. The script will retrieve Bitcoin addresses and their balances, and save them to a file named `btc_addresses.txt` in the same directory as the script.

## Configuration

You can modify the following variables in the script to change its behavior:

- `num_addresses`: The number of Bitcoin addresses to retrieve. (Default: 1000)
- `min_balance`: The minimum balance (in satoshis) that an address must have to be included in the output. (Default: 1000000000, or 10 BTC)
- `use_exchange_data`: Whether to retrieve addresses associated with top exchanges instead of randomly generating them. (Default: True)

If `use_exchange_data` is set to `True`, the script will retrieve Bitcoin addresses associated with the top 100 exchanges by trading volume, as reported by the CoinGecko API. If `use_exchange_data` is set to `False`, the script will randomly generate Bitcoin addresses and check their balances using the Blockchain.info API.

## License

This script is licensed under the MIT License. See the `LICENSE` file for more information.
