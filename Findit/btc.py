import requests

def get_exchange_addresses(num_exchanges):
    """
    Get a list of Bitcoin addresses associated with the top exchanges and return them as a list.
    
    Parameters:
    num_exchanges (int): The number of exchanges to include in the list.
    
    Returns:
    list: A list of Bitcoin addresses associated with the top exchanges.
    """
    addresses = []
    page = 1
    while len(addresses) < num_exchanges:
        # Get a page of exchanges from the API
        url = f'https://api.coingecko.com/api/v3/exchanges?per_page=100&page={page}'
        response = requests.get(url)
        if response.ok:
            page_data = response.json()
            # Add addresses associated with the exchange to the list
            for i, exchange_data in enumerate(page_data):
                exchange_id = exchange_data['id']
                print(f'Processing exchange {i+1}/{num_exchanges} ({exchange_id})...')
                url = f'https://api.coingecko.com/api/v3/exchanges/{exchange_id}/tickers'
                response = requests.get(url)
                if response.ok:
                    ticker_data = response.json()
                    for ticker in ticker_data['tickers']:
                        address = ticker['base']
                        # Skip addresses that have already been added
                        if address in addresses:
                            continue
                        balance = get_balance(address)
                        if balance is not None and balance >= min_balance:
                            addresses.append(address)
                            print(f'Found address {address} with balance of {balance} satoshis ({balance/1e8} BTC).')
                        # If we have enough addresses, return the list
                        if len(addresses) == num_exchanges:
                            return addresses
                else:
                    return None
            # Move to the next page of results
            page += 1
        else:
            return None

def get_balance(address):
    """
    Get the balance of a Bitcoin address and return it as an integer (in satoshis).
    
    Parameters:
    address (str): The Bitcoin address to retrieve the balance for.
    
    Returns:
    int: The balance of the address in satoshis, or None if the balance could not be retrieved.
    """
    url = f'https://blockchain.info/rawaddr/{address}'
    response = requests.get(url)
    if response.ok:
        address_data = response.json()
        return address_data['final_balance']
    else:
        return None

# Example usage: get Bitcoin addresses associated with the top 100 exchanges with at least 10 BTC
min_balance = 1000000000 # 1 BTC = 100,000,000 satoshis
num_exchanges = 100
addresses = []
print(f'Retrieving Bitcoin addresses associated with the top {num_exchanges} exchanges with at least {min_balance/1e8} BTC...')
# Get the addresses associated with the top exchanges
exchange_addresses = get_exchange_addresses(num_exchanges)
if exchange_addresses:
    with open('btc_addresses.txt', 'w') as f:
        for address in exchange_addresses:
            f.write(f'{address}\n')
        print(f'Successfully saved {len(exchange_addresses)} addresses to file.')
else:
    print('Error: Could not retrieve address data from API.')
