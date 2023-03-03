import curses
import requests
import random
import time

def generate_hex():
    return ''.join(random.choices('0123456789abcdef', k=64))

def get_address_info(address):
    url = f'https://blockchain.info/rawaddr/{address}'
    retries = 3
    while retries > 0:
        try:
            response = requests.get(url)
            if response.ok:
                return response.json()
            else:
                print(f'Error retrieving information for address {address}: {response.status_code}')
        except requests.exceptions.RequestException as e:
            print(f'Network error retrieving information for address {address}: {str(e)}')
        retries -= 1
        time.sleep(5)
    return None

def get_balance(address_info):
    return address_info['final_balance']

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

def main(stdscr):
    curses.curs_set(0)  # hide cursor
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # color for positive balances
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  # color for zero balances

    stdscr.addstr(0, 0, 'Bitcoin Address Lookup')
    stdscr.addstr(2, 0, 'Press any key to start...', curses.A_BOLD)
    stdscr.getch()

    with open('btc.txt', 'r') as f:
        target_addresses = sorted(f.read().splitlines())

    num_scans = 0
    start_time = time.time()
    while True:
        num_scans += 1
        hex_num = generate_hex()
        address = f'1{hex_num[:39]}'
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        stdscr.addstr(4, 0, f'Total number of addresses checked: {num_scans} ({minutes}m {seconds}s)', curses.A_BOLD)
        stdscr.addstr(5, 0, f'Scans per minute: {num_scans / elapsed_time * 60:.2f}', curses.A_BOLD)

        index = binary_search(target_addresses, address)
        if index != -1:
            address_info = get_address_info(address)
            if address_info:
                balance = get_balance(address_info)
                if balance > 0:
                    key = index + 1
                    stdscr.addstr(7, 0, f'Address {address} has a non-zero balance of {balance} satoshis.', curses.color_pair(1))
                    stdscr.addstr(8, 0, f'The key for this address is {key}.', curses.A_BOLD)
                    stdscr.addstr(9, 0, 'Press any key to exit...', curses.A_BOLD)
                    stdscr.getch()
                    break
                else:
                    stdscr.addstr(7, 0, f'Address {address} has a balance of 0 satoshis.', curses.color_pair(2))
            else:
                stdscr.addstr(7, 0, f'Error retrieving information for address {address}.', curses.A_BOLD)
        else:
            stdscr.addstr(7, 0, f'Address {address} not found in target list. Trying again...', curses.A_BOLD)

        stdscr.refresh()

curses.wrapper(main)

