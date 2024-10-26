from decouple import config

# Function to retrieve the number of Authorities
def authorities_count():
    count = 1
    # Loop to count Authorities by checking if each Authority name is defined in the .env file
    while True:
        name_key = f'AUTHORITY{count}_NAME'
        name = config(name_key, default=None)
        if not name:
            break
        count += 1
    return count - 1

# Function to retrieve the list of Authority names
def authorities_names():
    authorities = []
    count = 1
    # Loop to gather all Authority names from the .env file
    while True:
        name_key = f'AUTHORITY{count}_NAME'
        name = config(name_key, default=None)
        if not name:
            break
        authorities.append(name)
        count += 1
    return authorities

# Function to retrieve the list of Authorities as (name, address) tuples
def authorities_names_and_addresses():
    authorities = []
    count = 1
    # Loop to gather Authority names and addresses until none are found
    while True:
        address_key = f'AUTHORITY{count}_ADDRESS'
        name_key = f'AUTHORITY{count}_NAME'
        address = config(address_key, default=None)
        name = config(name_key, default=None)
        if not address or not name:
            break
        authorities.append((name, address))
        count += 1
    return authorities

# Function to retrieve Authorities' addresses and names as separate lists
def authorities_addresses_and_names_separated():
    authorities_names = []
    authorities_addresses = []
    count = 1
    # Loop to collect Authority names and addresses into two separate lists
    while True:
        address_key = f'AUTHORITY{count}_ADDRESS'
        name_key = f'AUTHORITY{count}_NAME'
        # Break loop if either name or address is missing
        if not config(address_key, default=None) or not config(name_key, default=None):
            break
        authorities_names.append(config(name_key))
        authorities_addresses.append(config(address_key))
        count += 1
    return authorities_addresses, authorities_names

