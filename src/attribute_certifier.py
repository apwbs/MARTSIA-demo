import json
from datetime import datetime
import random
import block_int
from decouple import config
import io
import sqlite3
import ipfshttpclient
import argparse
from authorities_info import authorities_names

# Store the generated process ID in the .env file
def store_process_id_to_env(value):
    name = 'PROCESS_INSTANCE_ID'
    with open('../src/.env', 'r', encoding='utf-8') as file:
        data = file.readlines()
    # Remove any existing process ID line
    for line in data:
        if line.startswith(name):
            data.remove(line)
            break
    # Add the new process ID line
    line = name + "=" + value + "\n"
    data.append(line)
    with open('../src/.env', 'w', encoding='utf-8') as file:
        file.writelines(data)

# Generate attributes for users, save data to IPFS, and store metadata in SQLite
def generate_attributes(roles_file):
    # Generate a unique process instance ID using the current timestamp
    now = datetime.now()
    now = int(now.strftime("%Y%m%d%H%M%S%f"))
    random.seed(now)
    process_instance_id = random.randint(10_000_000_000_000_000_000, 18_446_744_073_709_551_615)
    print(f'process instance id: {process_instance_id}')
    
    # Load roles data from JSON input
    with open(roles_file, 'r') as file:
        roles_data = json.load(file)
    roles = {key: [value] if not isinstance(value, list) else value for key, value in roles_data.items()}
    
    # Assign Authorities to each role and prepare user attributes
    authorities = authorities_names()
    dict_users = {}
    for role, attributes in roles.items():
        address = config(f'{role}_ADDRESS')
        dict_users[address] = [f'{process_instance_id}@{auth}' for auth in authorities] + attributes
    
    # Prepare JSON to be uploaded to IPFS
    f = io.StringIO()
    dict_users_dumped = json.dumps(dict_users)
    f.write('"process_instance_id": ' + str(process_instance_id) + '####')
    f.write(dict_users_dumped)
    f.seek(0)
    file_to_str = f.read()
    
    # Upload user data to IPFS and get the file hash
    api = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    hash_file = api.add_json(file_to_str)
    print(f'ipfs hash: {hash_file}')
    
    # Send attributes to the blockchain
    attribute_certifier_address = config('CERTIFIER_ADDRESS')
    private_key = config('CERTIFIER_PRIVATEKEY')
    block_int.send_users_attributes(attribute_certifier_address, private_key, process_instance_id, hash_file)
    
    # Save process instance data to SQLite3 database
    conn = sqlite3.connect('../databases/attribute_certifier/attribute_certifier.db')
    x = conn.cursor()
    x.execute("INSERT OR IGNORE INTO user_attributes VALUES (?,?,?)",
              (str(process_instance_id), hash_file, file_to_str))
    conn.commit()
    
    # Store the process ID in .env
    store_process_id_to_env(str(process_instance_id))

# Parse command-line arguments and initiate attribute generation
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Certifier configuration')
    parser.add_argument('-i', '--input', type=str, help='Specify the path of the roles.json file')
    args = parser.parse_args()
    if args.input:
        generate_attributes(args.input)
    else:
        parser.print_help()

